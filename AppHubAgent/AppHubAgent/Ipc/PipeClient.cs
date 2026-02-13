using System;
using System.IO;
using System.IO.Pipes ;
using System.Text;

namespace AppHubAgent.Ipc
{
    public static class PipeClient
    {

        //ex. pipeName : "AppHubAgentPipe", payload : "apphub://open?app=WCT"
        public static bool TrySend(string pipeName, string payload, int timeoutMs = 300)
        {
            // rootDir 계산: ...\AppHubAgent\Agent\AppHubAgent.exe-> ...\AppHubAgent
            string rootDir = "";
            try
            {
                var exePath = System.Reflection.Assembly.GetExecutingAssembly().Location;
                var agentDir = Path.GetDirectoryName(exePath);
                rootDir = Directory.GetParent(agentDir).FullName;
            }
            catch 
            { /* ignore */}

            string shortPayload = payload;
            if(!string.IsNullOrWhiteSpace(shortPayload) && shortPayload.Length > 260)
                shortPayload = shortPayload.Substring(0, 260) + "...";
            try
            {
                AgentLogger.Log(rootDir, "PIPECLIENT", 
                    $"TrySend BEGIN pipe={pipeName} timeoutMs={timeoutMs} payload={shortPayload}");

                using (var client = new NamedPipeClientStream(".", pipeName, PipeDirection.Out))
                {
                    client.Connect(timeoutMs);

                    using (var writer = new StreamWriter(client, Encoding.UTF8) { AutoFlush = true })
                    {
                        writer.Write(payload ?? "");
                    }
                }
                AgentLogger.Log(rootDir, "PIPECLIENT",
                    $"TrySend OK pipe={pipeName} payload={shortPayload}");

                return true;
            }
            catch(Exception ex)
            { 
                AgentLogger.Log(rootDir, "PIPECLIENT",
                    $"TrySend FAIL pipe={pipeName} err={ex.GetType().Name}:{ex.Message} payload={shortPayload}");
                return false;
            }
        }
    }
}
