from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_knox_id_optional
from app.services.user_service import get_user_by_knox_id
from app.services.app_event_service import (
    create_run_session,
    end_run_session,
    get_run_session,
    add_action_event,
)
from app.schemas.app_events import (
    RunSessionStart,
    RunSessionStartResponse,
    RunSessionEnd,
    ActionEventCreate,
    ActionEventResponse,
)

router = APIRouter(prefix="/app-events")


def _now_utc() -> datetime:
    return datetime.utcnow()


@router.post("/sessions/start", response_model=RunSessionStartResponse)
async def start_session(
    body: RunSessionStart,
    request: Request,
    db: AsyncSession = Depends(get_db),
    knox_header: str | None = Depends(get_knox_id_optional),
):
    # knox_id 우선순위: 헤더 > body
    knox_id = knox_header or body.knox_id

    user_id = None
    knox_id_raw = None
    if knox_id:
        u = await get_user_by_knox_id(db, knox_id)
        if u:
            user_id = u["id"]
        else:
            knox_id_raw = knox_id  # 매핑 실패한 값은 raw로 저장

    started_at = body.started_at or _now_utc()
    client_ip = body.client_ip or (request.client.host if request.client else None)

    session_id = await create_run_session(
        db,
        user_id=user_id,
        knox_id_raw=knox_id_raw,
        app_id=body.app_id,
        app_version=body.app_version,
        started_at=started_at,
        client_ip=client_ip,
    )
    return RunSessionStartResponse(session_id=session_id)


@router.post("/sessions/{session_id}/end", response_model=dict)
async def end_session(
    session_id: str,
    body: RunSessionEnd,
    db: AsyncSession = Depends(get_db),
):
    # 존재 확인
    sess = await get_run_session(db, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    ended_at = body.ended_at or _now_utc()
    await end_run_session(
        db,
        session_id=session_id,
        ended_at=ended_at,
        exit_code=body.exit_code,
        end_reason=body.end_reason,
    )
    return {"ok": True}


@router.post("/sessions/{session_id}/actions", response_model=ActionEventResponse)
async def post_action(
    session_id: str,
    body: ActionEventCreate,
    db: AsyncSession = Depends(get_db),
):
    # 존재 확인
    sess = await get_run_session(db, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    occurred_at = body.occurred_at or _now_utc()

    new_id = await add_action_event(
        db,
        session_id=session_id,
        occurred_at=occurred_at,
        action_type=body.action_type,
        action_name=body.action_name,
        description=body.description,
        duration_ms=body.duration_ms,
        severity=body.severity,
        meta_json=body.meta_json,
    )
    return ActionEventResponse(action_event_id=new_id)
