# app/services/app_event_admin_service.py
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# -------------------------
# Run sessions (app_run_sessions)
# -------------------------
SQL_LIST_RUN_SESSIONS = """
SELECT
  s.id,
  s.user_id,
  s.knox_id_raw,
  s.app_id,
  s.app_version,
  s.started_at,
  s.ended_at,
  s.exit_code,
  s.end_reason,
  s.client_ip,
  s.created_at
FROM app_run_sessions s
WHERE 1=1
  AND (:app_id IS NULL OR s.app_id = :app_id)
  AND (:user_id IS NULL OR s.user_id = :user_id)
  AND (:knox_id_raw IS NULL OR s.knox_id_raw = :knox_id_raw)
  AND (:date_from IS NULL OR s.started_at >= CONCAT(:date_from, ' 00:00:00'))
  AND (:date_to   IS NULL OR s.started_at <  CONCAT(:date_to,   ' 00:00:00'))
ORDER BY s.started_at DESC
LIMIT :limit OFFSET :offset
"""

SQL_GET_RUN_SESSION = """
SELECT
  s.id,
  s.user_id,
  s.knox_id_raw,
  s.app_id,
  s.app_version,
  s.started_at,
  s.ended_at,
  s.exit_code,
  s.end_reason,
  s.client_ip,
  s.created_at
FROM app_run_sessions s
WHERE s.id = :session_id
"""

SQL_UPDATE_RUN_SESSION = """
UPDATE app_run_sessions
SET
  ended_at = COALESCE(:ended_at, ended_at),
  exit_code = COALESCE(:exit_code, exit_code),
  end_reason = COALESCE(:end_reason, end_reason)
WHERE id = :session_id
"""

SQL_DELETE_RUN_SESSION = """
DELETE FROM app_run_sessions
WHERE id = :session_id
"""


async def list_run_sessions(
    db: AsyncSession,
    app_id: int | None,
    user_id: int | None,
    knox_id_raw: str | None,
    date_from: str | None,
    date_to: str | None,
    limit: int,
    offset: int,
) -> list[dict]:
    res = await db.execute(
        text(SQL_LIST_RUN_SESSIONS),
        {
            "app_id": app_id,
            "user_id": user_id,
            "knox_id_raw": knox_id_raw,
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit,
            "offset": offset,
        },
    )
    return [dict(r._mapping) for r in res.fetchall()]


async def get_run_session(db: AsyncSession, session_id: str) -> dict | None:
    res = await db.execute(text(SQL_GET_RUN_SESSION), {"session_id": session_id})
    row = res.mappings().first()
    return dict(row) if row else None


async def update_run_session(
    db: AsyncSession,
    session_id: str,
    ended_at,
    exit_code,
    end_reason,
) -> None:
    await db.execute(
        text(SQL_UPDATE_RUN_SESSION),
        {
            "session_id": session_id,
            "ended_at": ended_at,
            "exit_code": exit_code,
            "end_reason": end_reason,
        },
    )
    await db.commit()


async def delete_run_session(db: AsyncSession, session_id: str) -> None:
    await db.execute(text(SQL_DELETE_RUN_SESSION), {"session_id": session_id})
    await db.commit()


# -------------------------
# Action events (app_action_events)
# -------------------------
SQL_LIST_ACTION_EVENTS = """
SELECT
  e.id,
  e.session_id,
  e.occurred_at,
  e.action_type,
  e.action_name,
  e.description,
  e.duration_ms,
  e.severity,
  e.meta_json,
  e.created_at
FROM app_action_events e
LEFT JOIN app_run_sessions s ON s.id = e.session_id
WHERE 1=1
  AND (:session_id IS NULL OR e.session_id = :session_id)
  AND (:app_id IS NULL OR s.app_id = :app_id)
  AND (:action_type IS NULL OR e.action_type = :action_type)
  AND (:severity IS NULL OR e.severity = :severity)
  AND (:date_from IS NULL OR e.occurred_at >= CONCAT(:date_from, ' 00:00:00'))
  AND (:date_to   IS NULL OR e.occurred_at <  CONCAT(:date_to,   ' 00:00:00'))
ORDER BY e.occurred_at DESC
LIMIT :limit OFFSET :offset
"""

SQL_GET_ACTION_EVENT = """
SELECT
  e.id,
  e.session_id,
  e.occurred_at,
  e.action_type,
  e.action_name,
  e.description,
  e.duration_ms,
  e.severity,
  e.meta_json,
  e.created_at
FROM app_action_events e
WHERE e.id = :event_id
"""

SQL_UPDATE_ACTION_EVENT = """
UPDATE app_action_events
SET
  description = COALESCE(:description, description),
  duration_ms = COALESCE(:duration_ms, duration_ms),
  severity = COALESCE(:severity, severity),
  meta_json = COALESCE(:meta_json, meta_json)
WHERE id = :event_id
"""

SQL_DELETE_ACTION_EVENT = """
DELETE FROM app_action_events
WHERE id = :event_id
"""


async def list_action_events(
    db: AsyncSession,
    session_id: str | None,
    app_id: int | None,
    action_type: str | None,
    severity: str | None,
    date_from: str | None,
    date_to: str | None,
    limit: int,
    offset: int,
) -> list[dict]:
    res = await db.execute(
        text(SQL_LIST_ACTION_EVENTS),
        {
            "session_id": session_id,
            "app_id": app_id,
            "action_type": action_type,
            "severity": severity,
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit,
            "offset": offset,
        },
    )
    return [dict(r._mapping) for r in res.fetchall()]


async def get_action_event(db: AsyncSession, event_id: int) -> dict | None:
    res = await db.execute(text(SQL_GET_ACTION_EVENT), {"event_id": event_id})
    row = res.mappings().first()
    return dict(row) if row else None


async def update_action_event(
    db: AsyncSession,
    event_id: int,
    description: str | None = None,
    duration_ms: int | None = None,
    severity: str | None = None,
    meta_json=None,
) -> None:
    await db.execute(
        text(SQL_UPDATE_ACTION_EVENT),
        {
            "event_id": event_id,
            "description": description,
            "duration_ms": duration_ms,
            "severity": severity,
            "meta_json": meta_json,
        },
    )
    await db.commit()


async def delete_action_event(db: AsyncSession, event_id: int) -> None:
    await db.execute(text(SQL_DELETE_ACTION_EVENT), {"event_id": event_id})
    await db.commit()
