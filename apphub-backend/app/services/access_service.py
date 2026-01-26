from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# category_access
SQL_LIST_CAT = text("""
SELECT * FROM category_access
ORDER BY id DESC
LIMIT :limit OFFSET :offset
""")
SQL_GET_CAT = text("SELECT * FROM category_access WHERE id=:id LIMIT 1")
SQL_DECIDE_CAT = text("""
UPDATE category_access
SET status=:status, approved_by=:approved_by, approved_at=NOW(), note=:note
WHERE id=:id
""")
SQL_DELETE_CAT = text("DELETE FROM category_access WHERE id=:id")

# app_access
SQL_LIST_APP = text("""
SELECT * FROM app_access
ORDER BY id DESC
LIMIT :limit OFFSET :offset
""")
SQL_GET_APP = text("SELECT * FROM app_access WHERE id=:id LIMIT 1")
SQL_DECIDE_APP = text("""
UPDATE app_access
SET status=:status, approved_by=:approved_by, approved_at=NOW(), note=:note
WHERE id=:id
""")
SQL_DELETE_APP = text("DELETE FROM app_access WHERE id=:id")

async def list_category_access(db: AsyncSession, limit: int, offset: int) -> list[dict]:
    res = await db.execute(SQL_LIST_CAT, {"limit": int(limit), "offset": int(offset)})
    return [dict(r) for r in res.mappings().all()]

async def get_category_access(db: AsyncSession, row_id: int) -> dict | None:
    res = await db.execute(SQL_GET_CAT, {"id": int(row_id)})
    row = res.mappings().first()
    return dict(row) if row else None

async def decide_category_access(db: AsyncSession, row_id: int, status: str, approved_by: int, note: str | None):
    await db.execute(SQL_DECIDE_CAT, {"id": int(row_id), "status": status, "approved_by": int(approved_by), "note": note})
    await db.commit()

async def delete_category_access(db: AsyncSession, row_id: int):
    await db.execute(SQL_DELETE_CAT, {"id": int(row_id)})
    await db.commit()

async def list_app_access(db: AsyncSession, limit: int, offset: int) -> list[dict]:
    res = await db.execute(SQL_LIST_APP, {"limit": int(limit), "offset": int(offset)})
    return [dict(r) for r in res.mappings().all()]

async def get_app_access(db: AsyncSession, row_id: int) -> dict | None:
    res = await db.execute(SQL_GET_APP, {"id": int(row_id)})
    row = res.mappings().first()
    return dict(row) if row else None

async def decide_app_access(db: AsyncSession, row_id: int, status: str, approved_by: int, note: str | None):
    await db.execute(SQL_DECIDE_APP, {"id": int(row_id), "status": status, "approved_by": int(approved_by), "note": note})
    await db.commit()

async def delete_app_access(db: AsyncSession, row_id: int):
    await db.execute(SQL_DELETE_APP, {"id": int(row_id)})
    await db.commit()
