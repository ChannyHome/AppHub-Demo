# app/api/routers/app_events_admin.py
from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_min_role_rank
from app.schemas.events import AppActionEventOut, AppRunSessionOut, AppEventUpdate
from app.services.app_event_admin_service import (
    delete_action_event,
    delete_run_session,
    get_action_event,
    get_run_session,
    list_action_events,
    list_run_sessions,
    update_action_event,
    update_run_session,
)

router = APIRouter(prefix="/app-events")


# -------------------------
# Run sessions (app_run_sessions)
# -------------------------
@router.get("/sessions", response_model=list[AppRunSessionOut])
async def list_sessions_api(
    app_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    knox_id_raw: str | None = Query(default=None),
    date_from: str | None = Query(default=None, description="YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="YYYY-MM-DD"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    rows = await list_run_sessions(
        db,
        app_id=app_id,
        user_id=user_id,
        knox_id_raw=knox_id_raw,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return [AppRunSessionOut(**r) for r in rows]


@router.get("/sessions/{session_id}", response_model=AppRunSessionOut)
async def get_session_api(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    row = await get_run_session(db, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    return AppRunSessionOut(**row)


@router.put(
    "/sessions/{session_id}",
    response_model=dict,
    dependencies=[Depends(require_min_role_rank(40))],  # Maintainer+
)
async def update_session_api(
    session_id: str,
    body: AppEventUpdate,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    existing = await get_run_session(db, session_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")

    await update_run_session(
        db,
        session_id=session_id,
        ended_at=body.ended_at,
        exit_code=body.exit_code,
        end_reason=body.end_reason,
    )
    return {"ok": True}


@router.delete(
    "/sessions/{session_id}",
    response_model=dict,
    dependencies=[Depends(require_min_role_rank(40))],  # Maintainer+
)
async def delete_session_api(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    existing = await get_run_session(db, session_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")

    await delete_run_session(db, session_id)
    return {"ok": True}


# -------------------------
# Action events (app_action_events)
# -------------------------
class AppActionUpdate(BaseModel):
    description: str | None = None
    duration_ms: int | None = None
    severity: Literal["info", "warn", "error"] | None = None
    meta_json: dict[str, Any] | None = None


@router.get("/actions", response_model=list[AppActionEventOut])
async def list_actions_api(
    session_id: str | None = Query(default=None),
    app_id: int | None = Query(default=None),
    action_type: str | None = Query(default=None),
    severity: str | None = Query(default=None, description="info|warn|error"),
    date_from: str | None = Query(default=None, description="YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="YYYY-MM-DD"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    rows = await list_action_events(
        db,
        session_id=session_id,
        app_id=app_id,
        action_type=action_type,
        severity=severity,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return [AppActionEventOut(**r) for r in rows]


@router.get("/actions/{event_id}", response_model=AppActionEventOut)
async def get_action_api(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    row = await get_action_event(db, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Action event not found")
    return AppActionEventOut(**row)


@router.put(
    "/actions/{event_id}",
    response_model=dict,
    dependencies=[Depends(require_min_role_rank(40))],  # Maintainer+
)
async def update_action_api(
    event_id: int,
    body: AppActionUpdate,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    existing = await get_action_event(db, event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Action event not found")

    await update_action_event(
        db,
        event_id=event_id,
        description=body.description,
        duration_ms=body.duration_ms,
        severity=body.severity,
        meta_json=body.meta_json,
    )
    return {"ok": True}


@router.delete(
    "/actions/{event_id}",
    response_model=dict,
    dependencies=[Depends(require_min_role_rank(40))],  # Maintainer+
)
async def delete_action_api(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    existing = await get_action_event(db, event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Action event not found")

    await delete_action_event(db, event_id)
    return {"ok": True}
