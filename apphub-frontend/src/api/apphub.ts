// src/api/apphub.ts
import { fileUrl } from "./http";
// import type { AppItem } from "../types/app";
export const apphubApi = {
  // 백엔드 헬스체크 (예: GET /health)
  // health: () => request<{ status: string }>("/health"),
  // Agent 설치파일 다운로드 URL
  agentDownloadUrl: () => fileUrl("/agent/download-setup"),
  ShowImageUrl: (fileName: string): string => {
    if (!fileName) return "";
    // 혹시 / 붙어서 들어와도 제거
    const cleanName = fileName.replace(/^\/+/, "");
    return fileUrl(`/static/images/${cleanName}`);
  },
};
