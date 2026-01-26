from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

SQL_LIST = text("""
SELECT * FROM hub_events
WHERE (:user_id IS NULL OR user_id=:user_id)
ORDER BY id DESC
LIMIT :limit OFFSET :offset
""")
SQL_GET = text("SELECT * FROM hub_events WHERE id=:id LIMIT 1")
SQL_UPDATE = text("UPDATE hub_events SET description=:description, meta_json=:meta_json WHERE id=:id")
SQL_DELETE = text("DELETE FROM hub_events WHERE id=:id")

async def list_hub_events(db: AsyncSession, user_id: int | None, limit: int, offset: int) -> list[dict]:
    res = await db.execute(SQL_LIST, {"user_id": user_id, "limit": int(limit), "offset": int(offset)})
    return [dict(r) for r in res.mappings().all()]

async def get_hub_event(db: AsyncSession, event_id: int) -> dict | None:
    res = await db.execute(SQL_GET, {"id": int(event_id)})
    row = res.mappings().first()
    return dict(row) if row else None

async def update_hub_event(db: AsyncSession, event_id: int, description, meta_json):
    await db.execute(SQL_UPDATE, {"id": int(event_id), "description": description, "meta_json": meta_json})
    await db.commit()

async def delete_hub_event(db: AsyncSession, event_id: int):
    await db.execute(SQL_DELETE, {"id": int(event_id)})
    await db.commit()
