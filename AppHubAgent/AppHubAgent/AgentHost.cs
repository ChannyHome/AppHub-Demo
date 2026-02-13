
using AppHubAgent.Ipc;
using AppHubAgent.Protocol;
using AppHubAgent.Toast;
using System;
using System.Diagnostics;
using System.Windows;
using System.Windows.Threading;

namespace AppHubAgent
{
    public sealed class AgentHost
    {
        // TODO: MSI에서 DEV/PROD로 심고 여기서 읽도록 확장 가능
        //public const string PortalUrl = "https://your-apphub-portal.example/";
        //private readonly string _portalUrl = "http://127.0.0.1/";

        private readonly string _exePath;
        private TrayIconService _tray;
        private PipeServer _pipeServer;

        private bool _exitInProgress;

        public AgentHost(string exePath)
        {
            _exePath = exePath;
        }

        public void Start(string[] initialArgs)
        {
            try
            {
                // (중복 구독 방지)
                ProtocolHandler.ExitRequested -= OnExitRequested;
                ProtocolHandler.ExitRequested += OnExitRequested;

                // 1) 트레이 시작
                _tray = new TrayIconService(
                    portalUrl: AppConfig.PortalUrl,
                    iconResourcePath: "pack://application:,,,/Assets/AgentTray.ico" // 네 PNG 리소스 경로
                );
                _tray.Start();

                // ✅ MVP: Agent 켜질 때 토스트(성공/실패는 AgentHost에서 호출하는게 더 정확)
                ToastService.ShowSuccess("AppHub Agent", "준비 완료");

                // 2) Pipe 서버 시작 (백그라운드)
                _pipeServer = new PipeServer();
                _pipeServer.MessageReceived += OnPipeMessageReceived;
                _pipeServer.Start();

                // 3) 첫 실행 인자 처리
                // (예: 사용자가 apphub://... 눌러서 Agent가 처음 뜬 경우)
                if (initialArgs != null && initialArgs.Length > 0)
                {
                    var msg = PipeMessage.FromArgs(initialArgs);
                    DispatchHandle(msg);
                }
                else
                {
                    OpenPortal();
                }
            }
            catch (Exception ex)
            {
                // ❌ 실패 토스트
                AppHubAgent.Toast.ToastService.ShowError(
                    "AppHub Agent",
                    "시작 실패"
                );

                // (선택) 디버깅용 로그
                System.Diagnostics.Debug.WriteLine(ex);
            }
        }

        public void OnExitRequested()
        {
            if (_exitInProgress) return;
            _exitInProgress = true;

            var app = Application.Current;
            if (app == null) return;

            // ✅ 무조건 UI 스레드에서 처리
            app.Dispatcher.Invoke(() =>
            {
                // 1) 종료 토스트를 "즉시" 띄움(동기)
                ToastService.Show("AppHub Agent", "종료되었습니다", ToastKind.Info);

                // 2) UI 스레드 타이머로 종료를 늦춤 (Dispatcher가 살아있을 때 확실히 실행됨)
                var timer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromMilliseconds(800)
                };
                timer.Tick += (_, __) =>
                {
                    timer.Stop();

                    try { _tray?.Dispose(); } catch { }
                    try { app.Shutdown(); } catch { }
                };

                timer.Start();
            });
        }
        private void OnPipeMessageReceived(string wire)
        {
            var msg = PipeMessage.FromWire(wire);
            DispatchHandle(msg);
        }
        private void DispatchHandle(PipeMessage msg)
        {
            // Pipe 스레드에서 UI/Process 다루지 말고 Dispatcher로
            Application.Current.Dispatcher.BeginInvoke(new Action(() =>
            {
                try
                {
                    Handle(msg);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Handle failed:\n" + ex, "AppHubAgent");
                }
            }));
        }
        private void Handle(PipeMessage msg)
        {
            // 1) 단순 명령(열기/종료)
            if (msg.Kind == PipeMessageKind.Command)
            {
                if (msg.CommandText.Equals("open", StringComparison.OrdinalIgnoreCase))
                {
                    OpenPortal();
                    return;
                }
                if (msg.CommandText.Equals("exit", StringComparison.OrdinalIgnoreCase))
                {
                    Application.Current.Shutdown();
                    return;
                }
                if (msg.CommandText.Equals("run", StringComparison.OrdinalIgnoreCase))
                {
                    return;
                }
            }            // 2) URL 스킴 처리 (apphub://...)
            if (msg.Kind == PipeMessageKind.Url && !string.IsNullOrWhiteSpace(msg.Url))
            {
                ProtocolHandler.HandleUrl(msg.Url, OpenPortal);
                return;
            }
            else
            {
                //Local .exe로 실행
                ToastService.ShowSuccess("AppHub Agent", "실행 중");
            }
            // 3) 인자 없음 등: 포탈 열기(원하는 정책대로, Local .exe로 실행 포함)
            OpenPortal();
        }
        private void OpenPortal()
        {
            Process.Start(new ProcessStartInfo(AppConfig.PortalUrl) { UseShellExecute = true });
        }
        public void Dispose()
        {
            _pipeServer?.Dispose();
            _tray?.Dispose();
        }
    }
}
