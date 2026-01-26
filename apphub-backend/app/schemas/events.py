# app/schemas/events.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# -------------------------
# Hub Events (hub_events)
# -------------------------
HubEventType = Literal[
    "page_open",
    "search",
    "filter_change",
    "sort_change",
    "open_notice",
    "open_app_detail",
    "open_permission_request",
    "app_action",
]

HubPage = Literal["home", "apps", "upload", "library", "permission", "notices"]


class HubEventCreate(BaseModel):
    occurred_at: datetime
    event_type: HubEventType
    page: HubPage
    description: str | None = None
    meta_json: dict[str, Any] | None = None


class HubEventOut(BaseModel):
    id: int
    occurred_at: datetime
    user_id: int
    event_type: str
    page: str
    description: str | None = None
    meta_json: dict[str, Any] | None = None
    created_at: datetime


class HubEventUpdate(BaseModel):
    occurred_at: datetime | None = None
    description: str | None = None
    meta_json: dict[str, Any] | None = None


# -------------------------
# Native App Run Sessions (app_run_sessions)
# -------------------------
EndReason = Literal["user_exit", "crash", "killed", "unknown"]


class AppRunSessionCreate(BaseModel):
    """
    Native App이 AppHub 서버에 '시작'을 알릴 때 사용
    - session_id는 앱에서 생성한 UUID(str)로 보냄 (char(36))
    - knox_id_raw는 앱이 받은 knox_id(없으면 None)
    """
    session_id: str = Field(..., min_length=8, max_length=64)
    app_id: int
    app_version: str = Field(..., min_length=1, max_length=40)
    started_at: datetime
    knox_id_raw: str | None = Field(default=None, max_length=64)
    client_ip: str | None = Field(default=None, max_length=64)


class AppRunSessionEnd(BaseModel):
    """
    Native App이 종료를 알릴 때
    """
    ended_at: datetime
    exit_code: int | None = None
    end_reason: EndReason = "unknown"


class AppRunSessionOut(BaseModel):
    id: str
    user_id: int | None = None
    knox_id_raw: str | None = None
    app_id: int
    app_version: str
    started_at: datetime
    ended_at: datetime | None = None
    exit_code: int | None = None
    end_reason: str
    client_ip: str | None = None
    created_at: datetime


class AppEventUpdate(BaseModel):
    """
    (Admin/Maintainer) 세션/액션 이벤트를 정정할 때 공통 사용 (MVP)
    - 세션: ended_at/exit_code/end_reason 사용
    - 액션: ended_at/exit_code/end_reason는 안 쓰지만, router 코드 단순화를 위해 공통 형태 유지
    """
    ended_at: datetime | None = None
    exit_code: int | None = None
    end_reason: EndReason | None = None


# -------------------------
# Native App Action Events (app_action_events)
# -------------------------
Severity = Literal["info", "warn", "error"]


class AppActionEventCreate(BaseModel):
    """
    Native App이 작업(action)을 로그로 남길 때
    """
    session_id: str = Field(..., min_length=8, max_length=64)
    occurred_at: datetime
    action_type: str = Field(..., min_length=1, max_length=50)
    action_name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    duration_ms: int | None = Field(default=None, ge=0)
    severity: Severity = "info"
    meta_json: dict[str, Any] | None = None


class AppActionEventOut(BaseModel):
    id: int
    session_id: str
    occurred_at: datetime
    action_type: str
    action_name: str
    description: str | None = None
    duration_ms: int | None = None
    severity: str
    meta_json: dict[str, Any] | None = None
    created_at: datetime
