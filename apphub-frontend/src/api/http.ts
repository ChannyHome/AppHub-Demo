// src/api/http.ts
function ensureLeadingSlash(p: string) {
  if (!p) return "/";
  return p.startsWith("/") ? p : `/${p}`;
}
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL.replace(/\/$/, "");
export function fileUrl(path: string) {
  return API_BASE_URL + ensureLeadingSlash(path);
}
