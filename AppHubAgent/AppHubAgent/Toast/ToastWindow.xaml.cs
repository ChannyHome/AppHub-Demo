using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;
using System.Windows.Threading;

namespace AppHubAgent.Toast
{
    /// <summary>
    /// ToastWindow.xaml에 대한 상호 작용 논리
    /// </summary>
    public partial class ToastWindow : Window
    {
        private readonly string _title;
        private readonly string _message;
        private readonly string _iconPackUri;
        private readonly ToastKind _kind;

        private const int MarginRight = 16;
        private const int MarginBottom = 16;
        private const double ShowDurationMs = 220;
        private const double HideDurationMs = 220;
        private const int StayMs = 1800;

        private DispatcherTimer _timer;
        private bool _closing;


        public ToastWindow(string title, string message, string iconPackUri, ToastKind kind)
        {
            InitializeComponent();
            _title = title ?? "";
            _message = message ?? "";
            _iconPackUri = iconPackUri ?? "";
            _kind = kind;
        }

        public void ShowToast()
        {
            TitleText.Text = _title;
            MessageText.Text = _message;
            ApplyStyle(_kind);
            LoadIcon(_iconPackUri);

            Show();
        }

        public void ForceClose()
        {
            if (_closing) return;
            _closing = true;
            try { _timer?.Stop(); } catch { }
            try { Close(); } catch { }
        }

        private void Root_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            try 
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = AppConfig.PortalUrl,
                    UseShellExecute = true
                });
            } 
            catch { /* 실패해도 토스트 닫기만*/}
            finally
            {
                ForceClose();
            }
        }
        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            ForceClose();
        }

        private void LoadIcon(string packUri)
        {
            try
            {
                var img = new BitmapImage();
                img.BeginInit();
                img.UriSource = new Uri(packUri, UriKind.Absolute);
                img.CacheOption = BitmapCacheOption.OnLoad;
                img.EndInit();
                IconImage.Source = img;
            }
            catch
            {
                //아이콘 로드 실패 무시
            }
        }
        
        public void ApplyStyle(ToastKind kind)
        {
            //default 
            string bg = "#CC1E1E1E";
            string border = "#33FFFFFF";

            if (kind == ToastKind.Success)
            {
                bg = "#CC0F2A1C"; // green
                border = "#556BFFB2";
            }
            else if (kind == ToastKind.Error)
            {
                bg = "#CC2A0F0F"; // red
                border = "#55FF9B9B";
            }

            Root.Background = (SolidColorBrush)(new BrushConverter().ConvertFrom(bg));
            Root.BorderBrush = (SolidColorBrush)(new BrushConverter().ConvertFrom(border));
        }


        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            var work = SystemParameters.WorkArea;
            var finalLeft = work.Right - Width - MarginRight;
            var finalTop = work.Bottom - Height - MarginBottom;

            Left = finalLeft;
            Top = work.Bottom + 6;
            Opacity = 0.0;

            var show = new Storyboard();

            var topIn = new DoubleAnimation
            {
                From = Top,
                To = finalTop,
                Duration = TimeSpan.FromMilliseconds(ShowDurationMs),
                EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut }
            };
            Storyboard.SetTarget(topIn, this);
            Storyboard.SetTargetProperty(topIn, new PropertyPath(Window.TopProperty));

            var opacityIn = new DoubleAnimation
            {
                From = 0.0,
                To = 1.0,
                Duration = TimeSpan.FromMilliseconds(ShowDurationMs)
            };
            Storyboard.SetTarget(opacityIn, this);
            Storyboard.SetTargetProperty(opacityIn, new PropertyPath(Window.OpacityProperty));

            show.Children.Add(topIn);
            show.Children.Add(opacityIn);

            show.Completed += (_, __) =>
            {
                if(_closing) return;

                _timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(StayMs) };
                _timer.Tick += (s, ev) =>
                {
                    _timer.Stop();
                    HideWithAnimation(work.Bottom + 6);                    
                };
                _timer.Start();
            };
            show.Begin();
        }

        private void HideWithAnimation(double endTop)
        {
            if (_closing) return;
            _closing = true;
            var hide = new Storyboard();
            var topOut = new DoubleAnimation
            {
                From = Top,
                To = endTop,
                Duration = TimeSpan.FromMilliseconds(HideDurationMs),
                EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseIn }
            };
            Storyboard.SetTarget(topOut, this);
            Storyboard.SetTargetProperty(topOut, new PropertyPath(Window.TopProperty));
            
            var opacityOut = new DoubleAnimation
            {
                From = 1.0,
                To = 0.0,
                Duration = TimeSpan.FromMilliseconds(HideDurationMs)
            };
            Storyboard.SetTarget(opacityOut, this);
            Storyboard.SetTargetProperty(opacityOut, new PropertyPath(Window.OpacityProperty));
            
            hide.Children.Add(topOut);
            hide.Children.Add(opacityOut);

            hide.Completed += (_, __) =>
            {
                try { Close(); } catch { }
            };

            hide.Begin();
        }
    }
}
