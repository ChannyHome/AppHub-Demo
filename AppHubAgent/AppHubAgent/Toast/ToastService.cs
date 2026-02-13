using System;
using System.Windows;
using System.Threading.Tasks;
using System.Windows.Threading;

namespace AppHubAgent.Toast
{
    public static class ToastService
    {
        //Toast용 png
        private const string IconPackUri = "pack://application:,,,/Assets/AgentTray.png";

        private static readonly object _lock = new object();    
        private static ToastWindow _current; //마지막 토스트만 유지
        
        public static void Show(string title, string message, ToastKind kind = ToastKind.Info)
        {
            var disp = Application.Current?.Dispatcher ?? Dispatcher.CurrentDispatcher;

            disp.BeginInvoke(new Action(() => 
            {
                lock (_lock)
                {
                    try { _current?.ForceClose(); } catch { /* 무시 */ }
                    _current = null;
                    _current = new ToastWindow(title, message, IconPackUri, kind);
                    _current.ShowToast();
                }
            }));
        }

        public static void ShowSuccess(string title, string message)
            => Show(title, message, ToastKind.Success);

        public static void ShowError(string title, string message)
            => Show(title, message, ToastKind.Error);

    }
}
