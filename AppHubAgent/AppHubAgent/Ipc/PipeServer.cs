using System;
using System.IO.Pipes;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Runtime.InteropServices.WindowsRuntime;

namespace AppHubAgent.Ipc
{
    public sealed class PipeServer : IDisposable
    {
        public const string PipeName = "AppHubAgentPipe_v1";

        private CancellationTokenSource _cts;

        public event Action<string> MessageReceived;

        public void Start()
        {
            if (_cts != null) return;   
            _cts = new CancellationTokenSource();
            Task.Run(() => ListenLoop(_cts.Token));
        }

        private async Task ListenLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    using (var server = new System.IO.Pipes.NamedPipeServerStream(
                       pipeName: PipeName,
                       direction: PipeDirection.In,
                       maxNumberOfServerInstances: 10,
                       transmissionMode: PipeTransmissionMode.Message,
                       options: PipeOptions.Asynchronous))

                    {
                        await server.WaitForConnectionAsync(ct).ConfigureAwait(false);
                        using (var reader = new StreamReader(server, Encoding.UTF8))
                        {
                            var msg = await reader.ReadToEndAsync().ConfigureAwait(false);

                            //권장 :빈/개행 제거(FromWire가 Trim하기 하지만 여기서 한번 더 깔끔)
                            msg = msg?.Trim();

                            if(!string.IsNullOrWhiteSpace(msg))
                                MessageReceived?.Invoke(msg);
                        }
                    }
                }
                catch (OperationCanceledException)
                {
                    // Graceful shutdown
                    return;
                }
                catch (Exception)
                {
                    // Log or handle exceptions as needed
                    await Task.Delay(150, ct).ConfigureAwait(false); // Prevent tight loop on failure
                }
            }

        }

        public void Dispose()
        {
            try { _cts?.Cancel(); } catch { }
            try { _cts?.Dispose(); } catch { }
            _cts = null;
        }
    }
}
