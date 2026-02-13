using System;
using System.Diagnostics;
using System.IO;
using System.Text;

namespace AppHubAgent.Ipc
{
    public static class AgentLogger
    {
        public static void Log(string rootDir, string tag, string message)
        {
            try
            {
                var logDir = Path.Combine(rootDir, "Logs");
                Directory.CreateDirectory(logDir);

                var pid = Process.GetCurrentProcess().Id;
                var logpath = Path.Combine(logDir, "agent-ipc.log");

                File.AppendAllText(
                    logpath, 
                    $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} PID={pid} {tag} {message}{Environment.NewLine}]", 
                    Encoding.UTF8
                    );                
            }
            catch (Exception ex)
            {
                // ignore
                Debug.WriteLine($"Failed to log message: {ex.Message}");
            }
        }
        //URL이 너무 길면 로그가 지저분해지니까 축약용(원하면 사용)
        public static string ShortUrl(string url, int max = 240)
        {
            if (string.IsNullOrWhiteSpace(url)) return "";
            url = url.Trim();
            return url.Length <= max ? url : url.Substring(0, max) + "...";
        }
    }
}
