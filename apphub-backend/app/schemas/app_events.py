from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class RunSessionStart(BaseModel):
    app_id: int
    app_version: str = Field(..., max_length=40)
    started_at: Optional[datetime] = None  # None이면 서버 NOW 처리 가능(여기선 기본값 사용)
    knox_id: Optional[str] = Field(default=None, description="헤더 없을 때 body로 보내도 됨")
    client_ip: Optional[str] = None        # 없으면 서버에서 request.client.host로 채움


class RunSessionStartResponse(BaseModel):
    ok: bool = True
    session_id: str


class RunSessionEnd(BaseModel):
    ended_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    end_reason: Literal["user_exit", "crash", "killed", "unknown"] = "unknown"
    knox_id: Optional[str] = None


class ActionEventCreate(BaseModel):
    occurred_at: Optional[datetime] = None
    action_type: str = Field(..., max_length=50)   # 예: "feature", "job", "ui"
    action_name: str = Field(..., max_length=120)  # 예: "StartPolish", "OpenRecipe"
    description: Optional[str] = Field(default=None, max_length=500)
    duration_ms: Optional[int] = None
    severity: Literal["info", "warn", "error"] = "info"
    meta_json: Optional[Dict[str, Any]] = None


class ActionEventResponse(BaseModel):
    ok: bool = True
    action_event_id: int
