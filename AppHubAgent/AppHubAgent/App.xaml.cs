using AppHubAgent.Ipc;
using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading;
using System.Windows;

namespace AppHubAgent
{
    /// <summary>
    /// App.xaml에 대한 상호 작용 논리
    /// </summary>
    public partial class App : Application
    {
        // 전 사용자 공통으로 1개만 뜨게: Global\ 사용
        private const string MutexName = @"Global\AppHubAgent_Mutex_v1";
        private static Mutex _mutex;

        //public const string PortalUrl ="http://127.0.0.1/";

        private AgentHost _host;


        private void Application_Startup(object sender, StartupEventArgs e)
        {
            var args = e.Args ?? Array.Empty<string>();
            var exePath = Assembly.GetExecutingAssembly().Location;
            // C:\Program Files (x86)\AppHubAgent\Agent\AppHubAgent.exe
            string agentDir = Path.GetDirectoryName(exePath);
            // C:\Program Files (x86)\AppHubAgent\Agent
            string rootDir = Directory.GetParent(agentDir).FullName;
            // C:\Program Files (x86)\AppHubAgent

            bool createdNew;
            _mutex = new Mutex(initiallyOwned: true, name: MutexName, createdNew: out createdNew);

            if (!createdNew)
            {
                // 이미 떠있음 → 메시지를 기존 인스턴스에 전달하고 종료
                var msg = PipeMessage.FromArgs(args);
                PipeClient.TrySend(PipeServer.PipeName, msg.ToWire());
                Shutdown(0);
                return;
            }
            else
            {
                var msg = PipeMessage.FromArgs(args);
                if (!Uri.TryCreate(msg.Url, UriKind.Absolute, out var uri))
                {

                }
                if (uri != null)
                {
                    var action = uri.Host; // run/install/update/ping/open
                    if (action.ToLowerInvariant() == "run"
                        || action.ToLowerInvariant() == "open")
                    {

                    }
                    else
                    {
                        Shutdown(0);
                        return;
                    }
                }
            }
            // 최초 인스턴스(트레이 상주)
            _host = new AgentHost(exePath);
            _host.Start(args); // 첫 실행 인자도 처리(예: apphub://로 바로 시작될 수 있음)
        }
        private void Application_Exit(object sender, ExitEventArgs e)
        {
            _host?.Dispose();
            try
            {
                _mutex?.ReleaseMutex();
                _mutex?.Dispose();
            }
            catch { /* ignore */ }
        }
    }
}
