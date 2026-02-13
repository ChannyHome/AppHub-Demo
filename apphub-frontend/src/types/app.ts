// src/types/app.ts
export type AppItem = {
  id?: number;
  app_key: string;
  name: string;
  icon?: string; // 예: "/apps/wmo.png" 처럼 public 경로 or 서버 url
  domain?: string; // 예: "hawk"
  web_launch_url?: string;
};
