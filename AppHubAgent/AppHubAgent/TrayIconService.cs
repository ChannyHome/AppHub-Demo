using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;
using System.Windows.Resources;
using WpfApp = System.Windows.Application;

using AppHubAgent.Ipc;

namespace AppHubAgent
{
    public sealed class TrayIconService : IDisposable
    {
        private readonly string _portalUrl;
        private readonly string _iconResourcePath;

        private NotifyIcon _notifyIcon;
        private Icon _icon;

        public TrayIconService(string portalUrl, string iconResourcePath)
        {
            _portalUrl = portalUrl ?? "";
            _iconResourcePath = iconResourcePath ?? "";
        }

        public void Start()
        {
            if (_notifyIcon != null) return;

            _notifyIcon = new NotifyIcon
            {
                Text = "AppHub Agent",
                Visible = true
            };

            _icon = LoadIconFromIcoResource(_iconResourcePath);
            _notifyIcon.Icon = _icon ?? SystemIcons.Application;

            var menu = new ContextMenuStrip();

            var openItem = new ToolStripMenuItem("열기");
            openItem.Click += (_, __) => SendCommand("open");

            var exitItem = new ToolStripMenuItem("종료");

            exitItem.Click += (_, __) =>
            {
                var result = System.Windows.MessageBox.Show(
                    "정말로 종료하시겠습니까?\n(종료하면 AppHub에서 앱 실행이 동작하지 않을 수 있습니다.)",
                    "AppHubAgent",
                    System.Windows.MessageBoxButton.YesNo,
                    System.Windows.MessageBoxImage.Question);

                if (result == System.Windows.MessageBoxResult.Yes)
                    SendCommand("exit");
            };


            menu.Items.Add(openItem);
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add(exitItem);

            _notifyIcon.ContextMenuStrip = menu;
            _notifyIcon.DoubleClick += (_, __) => SendCommand("open");
        }

        private void SendCommand(string cmd)
        {
            var payload = PipeMessage.CreateCommand(cmd).ToWire();
            PipeClient.TrySend(PipeServer.PipeName, payload);
        }

        private Icon LoadIconFromIcoResource(string packUri)
        {
            try
            {
                StreamResourceInfo sri = WpfApp.GetResourceStream(new Uri(packUri, UriKind.Absolute));
                if (sri?.Stream == null) return SystemIcons.Application;

                using (var ms = new MemoryStream())
                {
                    sri.Stream.CopyTo(ms);
                    ms.Position = 0;
                    return new Icon(ms);
                }
            }
            catch
            {
                return SystemIcons.Application;
            }
        }


        public void Dispose()
        {
            if(_notifyIcon != null)
            {
                _notifyIcon.Visible = false;
                _notifyIcon.Dispose();
                _notifyIcon = null;
            }
            _icon?.Dispose();
            _icon = null;
        }
    }
}
