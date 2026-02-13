using System;
using System.Collections.Generic;

namespace AppHubAgent.Protocol
{
    internal static class QueryStringParser
    {
        public static Dictionary<string, string> Parse(string query)
        {
            var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (string.IsNullOrWhiteSpace(query)) return dict;
            if (query.StartsWith("?")) query = query.Substring(1);
            foreach (var part in query.Split(new[] { '&' }, StringSplitOptions.RemoveEmptyEntries))
            {
                var kv = part.Split(new[] { '=' }, 2);
                var key = Uri.UnescapeDataString(kv[0]);
                var val = kv.Length > 1 ? Uri.UnescapeDataString(kv[1]) : "";
                dict[key] = val;
            }
            return dict;
        }
    }
}
