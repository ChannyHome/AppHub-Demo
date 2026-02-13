using System.Configuration;

namespace AppHubAgent
{
    public static class AppConfig
    {
        public static string Envionment => ConfigurationManager.AppSettings["Environment"] ?? "Dev";

        public static string PortalUrl => ConfigurationManager.AppSettings["PortalUrl"] ?? "http://127.0.0.1/";
        
    }
}
