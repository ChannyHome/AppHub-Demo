from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

SQL_LIST = text("""
SELECT * FROM apps
WHERE (:active_only = 0 OR is_active = 1)
ORDER BY name ASC
""")

SQL_GET = text("SELECT * FROM apps WHERE id=:id LIMIT 1")

SQL_INSERT = text("""
INSERT INTO apps
(category_id, app_key, name, summary, description, icon, manual, voc, app_kind, web_launch_url,
 is_active, requires_app_approval, latest_version_id, created_by)
VALUES
(:category_id, :app_key, :name, :summary, :description, :icon, :manual, :voc, :app_kind, :web_launch_url,
 :is_active, :requires_app_approval, :latest_version_id, :created_by)
""")

SQL_UPDATE = text("""
UPDATE apps SET
category_id=:category_id,
name=:name,
summary=:summary,
description=:description,
icon=:icon,
manual=:manual,
voc=:voc,
app_kind=:app_kind,
web_launch_url=:web_launch_url,
is_active=:is_active,
requires_app_approval=:requires_app_approval,
latest_version_id=:latest_version_id
WHERE id=:id
""")

# delete = soft delete
SQL_SOFT_DELETE = text("UPDATE apps SET is_active=0 WHERE id=:id")

async def list_apps(db: AsyncSession, active_only: bool = True) -> list[dict]:
    res = await db.execute(SQL_LIST, {"active_only": 1 if active_only else 0})
    return [dict(r) for r in res.mappings().all()]

async def get_app(db: AsyncSession, app_id: int) -> dict | None:
    res = await db.execute(SQL_GET, {"id": int(app_id)})
    row = res.mappings().first()
    return dict(row) if row else None

async def create_app(db: AsyncSession, payload: dict) -> int:
    await db.execute(SQL_INSERT, payload)
    res = await db.execute(text("SELECT LAST_INSERT_ID()"))
    new_id = int(res.scalar_one())
    await db.commit()
    return new_id

async def update_app(db: AsyncSession, app_id: int, payload: dict) -> None:
    payload = dict(payload)
    payload["id"] = int(app_id)
    await db.execute(SQL_UPDATE, payload)
    await db.commit()

async def delete_app(db: AsyncSession, app_id: int) -> None:
    await db.execute(SQL_SOFT_DELETE, {"id": int(app_id)})
    await db.commit()
