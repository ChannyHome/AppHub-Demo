using AppHubAgent.Toast;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Windows;
using System.Windows.Input;
using System.Windows.Interop;

namespace AppHubAgent.Protocol
{
    public static class ProtocolHandler
    {
        private const string Scheme = "apphub";
        //AgentHost에서 구독할 종료 요청 이벤트
        public static event Action ExitRequested;

        //OpenPortal 콜백은 AgentHost에서 구독할 수 있도록 공개
        public static void HandleUrl(string rawUrl, Action openPortal)
        {
            if(!Uri.TryCreate(rawUrl, UriKind.Absolute, out var uri))
            {
                MessageBox.Show($"Invalid URL :\n {rawUrl}", "AppHubAgent");
                return;
            }

            if(!uri.Scheme.Equals(Scheme, StringComparison.OrdinalIgnoreCase))
            {
                MessageBox.Show($"Unknown scheme :\n {rawUrl}", "AppHubAgent");
                return;
            }

            var action = uri.Host; // run/install/update/ping/open
            var qs = QueryStringParser.Parse(uri.Query);
            switch(action.ToLowerInvariant())
            {
                case "open":
                    //openPortal?.Invoke();
                    ToastService.ShowSuccess("AppHubAgent", "실행 중");
                    break;
                case "exit":
                    HandleExitAgent(); // Tray 종료
                    break;

                case "ping":
                    //MVP: 살아있음 확인 정도
                    break;

                case "run":
                    HandleRun(qs);
                    break;

                case "install":
                case "update":
                    HandleInstallOrUpdate(qs);
                    break;

                default:
                    MessageBox.Show($"Unknown action :\n {rawUrl}", "AppHubAgent");
                    break;
            }
        }

        private static void HandleExitAgent()
        {
            // ✅ “종료 요청”만 올리고 실제 종료/트레이정리는 AgentHost가 함
            ExitRequested?.Invoke();
        }

        public static void HandleRun(Dictionary<string, string> qs)
        {
            string category = GetFirst(qs, "cat", "category");
            string appName = GetFirst(qs, "app", "appName");
            string exeName = GetFirst(qs, "exe");           // ✅ optional
            bool runAsAdmin = ParseBool(GetFirst(qs, "admin"), defaultValue: false);

            // ✅ args는 디코딩해서 사용 (QueryStringParser가 디코딩 안 하는 케이스 대비)
            string argsRaw = GetFirst(qs, "args");
            string args = DecodeIfNeeded(argsRaw);

            if (string.IsNullOrWhiteSpace(category) || string.IsNullOrWhiteSpace(appName))
            {
                ToastService.Show("AppHub Agent", "run 파라미터가 부족합니다. (cat, app)", ToastKind.Error);
                return;
            }

            category = SanitizeName(category);
            appName = SanitizeName(appName);

            // exeName이 없으면 기본은 "{app}.exe"
            exeName = string.IsNullOrWhiteSpace(exeName) ? (appName + ".exe") : SanitizeExe(exeName);

            // ✅ 설치 루트 계산: ...\AppHubAgent\Agent\AppHubAgent.exe → ...\AppHubAgent
            string agentExePath = Assembly.GetExecutingAssembly().Location;
            string agentDir = Path.GetDirectoryName(agentExePath);
            string rootDir = Directory.GetParent(agentDir).FullName;

            // ✅ Apps\<cat>\<app>\{exeName}
            string appDir = Path.Combine(rootDir, "Apps", category, appName);
            string targetExe = Path.Combine(appDir, exeName);

            if (!File.Exists(targetExe))
            {
                ToastService.Show("AppHub Agent",
                    $"앱을 찾을 수 없습니다\n{category}\\{appName}\\{exeName}",
                    ToastKind.Error);
                return;
            }
            // (옵션) -log 경로 폴더가 없으면 만들어주기 (많은 앱이 폴더 없으면 로그 생성 실패)
            TryEnsureLogDirectory(args);
            // ✅ 실행 전에 Agent 자체 로그로 “실제로 무엇을 실행했는지” 남기기
            WriteAgentRunLog(rootDir, targetExe, runAsAdmin, args);

            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = targetExe,
                    Arguments = string.IsNullOrWhiteSpace(args) ? "" : args,
                    UseShellExecute = true, // runas 필수
                    WorkingDirectory = appDir
                };

                if (runAsAdmin)
                    psi.Verb = "runas";

                Process.Start(psi);

                ToastService.Show("AppHub Agent",
                    runAsAdmin ? $"{exeName} (관리자) 실행 요청" : $"{exeName} 실행 요청",
                    ToastKind.Success);
            }
            catch(Win32Exception ex) when (ex.NativeErrorCode == 1223)
            {
                ToastService.Show("AppHub Agent", "관리자 권한 실행이 취소되었습니다.", ToastKind.Info);
            }
            catch(Exception ex)
            {
                ToastService.Show("AppHub Agent", $"실행 실패: {ex.Message}", ToastKind.Error);
            }
        }

        private static string DecodeIfNeeded(string s)
        {
            if (string.IsNullOrWhiteSpace(s)) return "";
            // %가 있으면 디코딩 시도 (이미 디코딩된 값이면 결과 동일)
            try { return s.Contains("%") ? Uri.UnescapeDataString(s) : s; }
            catch { return s; }
        }

        private static void TryEnsureLogDirectory(string args)
        {
            if (string.IsNullOrWhiteSpace(args)) return;

            // 아주 단순 파서: "-log <path>" 또는 "-log=<path>"
            // 필요하면 나중에 더 탄탄하게 만들 수 있음
            string path = null;

            var idx = args.IndexOf("-log", StringComparison.OrdinalIgnoreCase);
            if (idx < 0) return;

            // "-log=" 형태
            var eq = args.IndexOf("-log=", StringComparison.OrdinalIgnoreCase);
            if (eq >= 0)
            {
                path = args.Substring(eq + 5).Trim();
                // 뒤에 다른 옵션이 있으면 첫 공백까지만
                var sp = path.IndexOf(' ');
                if (sp >= 0) path = path.Substring(0, sp);
                path = path.Trim().Trim('"');
            }
            else
            {
                // "-log <path>" 형태
                var after = args.Substring(idx + 4).Trim();
                if (after.StartsWith("=", StringComparison.Ordinal)) after = after.Substring(1).Trim();

                // 따옴표 우선
                if (after.StartsWith("\""))
                {
                    var end = after.IndexOf('"', 1);
                    if (end > 1) path = after.Substring(1, end - 1);
                }
                else
                {
                    var sp = after.IndexOf(' ');
                    path = sp >= 0 ? after.Substring(0, sp) : after;
                }
            }
            if (string.IsNullOrWhiteSpace(path)) return;
            try
            {
                var dir = Path.GetDirectoryName(path);
                if (!string.IsNullOrWhiteSpace(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);
            }
            catch { }
        }

        private static void WriteAgentRunLog(string rootDir, string exe, bool admin, string args)
        {
            try
            {
                var logDir = Path.Combine(rootDir, "Logs");
                Directory.CreateDirectory(logDir);

                var logPath = Path.Combine(logDir, "agent-run.log");
                File.AppendAllText(logPath,
                    $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] admin={admin} exe=\"{exe}\" args=\"{args}\"\r\n");
            }
            catch { }
        }

        private static string GetFirst(Dictionary<string, string> qs, params string[] keys)
        {
            foreach (var k in keys)
                if (qs.TryGetValue(k, out var v) && !string.IsNullOrWhiteSpace(v))
                    return v.Trim();
            return "";
        }

        private static bool ParseBool(string s, bool defaultValue)
        {
            if (string.IsNullOrWhiteSpace(s)) return defaultValue;
            s = s.Trim().ToLowerInvariant();
            if (s == "1" || s == "true" || s == "yes" || s == "y" || s == "on") return true;
            if (s == "0" || s == "false" || s == "no" || s == "n" || s == "off") return false;
            return defaultValue;
        }

        private static string SanitizeName(string s)
        {
            s = s.Trim();
            s = s.Replace("\\", "").Replace("/", "").Replace("..", "").Replace(":", "");
            foreach (var c in Path.GetInvalidFileNameChars())
                s = s.Replace(c.ToString(), "");
            return s;
        }

        private static string SanitizeExe(string s)
        {
            s = SanitizeName(s);
            // 폴더 지정 못하게 (exe는 파일명만 허용)
            if (s.Contains("\\") || s.Contains("/")) s = Path.GetFileName(s);
            // 확장자 없으면 .exe 붙이기
            if (!s.EndsWith(".exe", StringComparison.OrdinalIgnoreCase)) s += ".exe";
            return s;
        }

        private static void HandleInstallOrUpdate(Dictionary<string, string> qs)
        {
            // 예: apphub://install?msi=C:\temp\a.msi
            // 또는 apphub://install?url=https://server/app.msi  (다운로드 로직은 다음 단계)
            var msi = qs.TryGetValue("msi", out var v1) ? v1 : "";
            var url = qs.TryGetValue("url", out var v2) ? v2 : "";

            MessageBox.Show($"INSTALL/UPDATE\nmsi={msi}\nurl={url}\n(다음 단계: msiexec /i 또는 /update, 다운로드, 완료 감지)", "AppHubAgent");
        }

    }
}
