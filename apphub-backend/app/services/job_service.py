from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

SQL_LIST = text("""
SELECT * FROM jobs
WHERE (:user_id IS NULL OR user_id = :user_id)
ORDER BY id DESC
LIMIT :limit OFFSET :offset
""")

SQL_GET = text("SELECT * FROM jobs WHERE id=:id LIMIT 1")

SQL_INSERT = text("""
INSERT INTO jobs (user_id, job_type, status, progress, message)
VALUES (:user_id, :job_type, :status, :progress, :message)
""")

SQL_UPDATE = text("""
UPDATE jobs
SET status=:status, progress=:progress, message=:message
WHERE id=:id
""")

SQL_DELETE = text("DELETE FROM jobs WHERE id=:id")

async def list_jobs(db: AsyncSession, user_id: int | None, limit: int, offset: int) -> list[dict]:
    res = await db.execute(SQL_LIST, {"user_id": user_id, "limit": int(limit), "offset": int(offset)})
    return [dict(r) for r in res.mappings().all()]

async def get_job(db: AsyncSession, job_id: int) -> dict | None:
    res = await db.execute(SQL_GET, {"id": int(job_id)})
    row = res.mappings().first()
    return dict(row) if row else None

async def create_job(db: AsyncSession, payload: dict) -> int:
    await db.execute(SQL_INSERT, payload)
    res = await db.execute(text("SELECT LAST_INSERT_ID()"))
    new_id = int(res.scalar_one())
    await db.commit()
    return new_id

async def update_job(db: AsyncSession, job_id: int, payload: dict) -> None:
    payload = dict(payload)
    payload["id"] = int(job_id)
    await db.execute(SQL_UPDATE, payload)
    await db.commit()

async def delete_job(db: AsyncSession, job_id: int) -> None:
    await db.execute(SQL_DELETE, {"id": int(job_id)})
    await db.commit()
