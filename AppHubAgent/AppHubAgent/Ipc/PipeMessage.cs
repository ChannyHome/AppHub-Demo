using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AppHubAgent.Ipc
{
    public enum PipeMessageKind
    {
        None = 0,
        Command = 1,
        Url = 2
    }
    public sealed class PipeMessage
    {
        public PipeMessageKind Kind { get; private set; }
        public string CommandText { get; private set; }
        public string Url { get; private set; }

        public static PipeMessage CreateCommand(string cmd)
            => new PipeMessage { Kind = PipeMessageKind.Command, CommandText = cmd ?? ""};

        public static PipeMessage CreateUrl(string url)
            => new PipeMessage { Kind = PipeMessageKind.Url, Url = url ?? "" };

        public static PipeMessage FromArgs(string[] args)
        {
            if(args == null || args.Length == 0)
                return new PipeMessage { Kind = PipeMessageKind.None };
            
            var first = args[0];

            if ((!string.IsNullOrWhiteSpace(first) && first.Contains("://")))
                return CreateUrl(first);

            if(args.Any(a => a.Equals("--open--portal", StringComparison.OrdinalIgnoreCase)))
                return CreateCommand("open");

            if (args.Any(a => a.Equals("--exit", StringComparison.OrdinalIgnoreCase)))
                return CreateCommand("exit");

            return new PipeMessage { Kind = PipeMessageKind.None };
        }

        public string ToWire()
        { 
            if (Kind == PipeMessageKind.Command)
                return "CMD|" + (CommandText ?? "");
            if (Kind == PipeMessageKind.Url)
                return "URL|" + (Url ?? "");            
            return "NONE|";
        }

        public static PipeMessage FromWire(string wire)
        {
            if (string.IsNullOrWhiteSpace(wire))
                return new PipeMessage { Kind = PipeMessageKind.None };

            wire = wire.Trim();

            var idx = wire.IndexOf('|');
            if (idx < 0)
            {
                if(wire.Contains("://"))
                    return CreateUrl(wire);
                return new PipeMessage { Kind = PipeMessageKind.None };
            }

            var head = wire.Substring(0, idx).Trim().ToUpperInvariant();
            var body = wire.Substring(idx + 1);

            if(head == "CMD")
                return CreateCommand(body);
            if(head == "URL")
                return CreateUrl(body);
            return new PipeMessage { Kind = PipeMessageKind.None };
        }
    }
}
