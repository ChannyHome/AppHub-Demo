from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


SQL_CREATE_SESSION = text("""
INSERT INTO app_run_sessions
(id, user_id, knox_id_raw, app_id, app_version, started_at, client_ip)
VALUES
(:id, :user_id, :knox_id_raw, :app_id, :app_version, :started_at, :client_ip)
""")

SQL_END_SESSION = text("""
UPDATE app_run_sessions
SET ended_at = :ended_at,
    exit_code = :exit_code,
    end_reason = :end_reason
WHERE id = :id
""")

SQL_GET_SESSION = text("""
SELECT id, user_id, knox_id_raw, app_id, app_version, started_at, ended_at
FROM app_run_sessions
WHERE id = :id
LIMIT 1
""")

SQL_INSERT_ACTION = text("""
INSERT INTO app_action_events
(session_id, occurred_at, action_type, action_name, description, duration_ms, severity, meta_json)
VALUES
(:session_id, :occurred_at, :action_type, :action_name, :description, :duration_ms, :severity, :meta_json)
""")

SQL_LAST_INSERT_ID = text("SELECT LAST_INSERT_ID()")


async def create_run_session(
    db: AsyncSession,
    *,
    user_id: int | None,
    knox_id_raw: str | None,
    app_id: int,
    app_version: str,
    started_at: datetime,
    client_ip: str | None,
) -> str:
    session_id = str(uuid.uuid4())
    await db.execute(
        SQL_CREATE_SESSION,
        {
            "id": session_id,
            "user_id": user_id,
            "knox_id_raw": knox_id_raw,
            "app_id": app_id,
            "app_version": app_version,
            "started_at": started_at,
            "client_ip": client_ip,
        },
    )
    await db.commit()
    return session_id


async def end_run_session(
    db: AsyncSession,
    *,
    session_id: str,
    ended_at: datetime,
    exit_code: int | None,
    end_reason: str,
) -> None:
    await db.execute(
        SQL_END_SESSION,
        {
            "id": session_id,
            "ended_at": ended_at,
            "exit_code": exit_code,
            "end_reason": end_reason,
        },
    )
    await db.commit()


async def get_run_session(db: AsyncSession, session_id: str) -> dict | None:
    res = await db.execute(SQL_GET_SESSION, {"id": session_id})
    row = res.mappings().first()
    return dict(row) if row else None


async def add_action_event(
    db: AsyncSession,
    *,
    session_id: str,
    occurred_at: datetime,
    action_type: str,
    action_name: str,
    description: str | None,
    duration_ms: int | None,
    severity: str,
    meta_json: dict | None,
) -> int:
    await db.execute(
        SQL_INSERT_ACTION,
        {
            "session_id": session_id,
            "occurred_at": occurred_at,
            "action_type": action_type,
            "action_name": action_name,
            "description": description,
            "duration_ms": duration_ms,
            "severity": severity,
            "meta_json": meta_json,
        },
    )
    res = await db.execute(SQL_LAST_INSERT_ID)
    new_id = int(res.scalar_one())
    await db.commit()
    return new_id
