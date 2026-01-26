from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


# 목록(필터 + 노출기간 + 우선순위) 조회
SQL_LIST_NOTICES = text("""
SELECT
  n.id,
  n.scope,
  n.category_id,
  n.app_id,
  n.title,
  n.body,
  n.kind,
  n.start_at,
  n.end_at,
  n.priority,
  n.created_by,
  n.created_at
FROM notices n
WHERE 1=1
  AND (:scope IS NULL OR n.scope = :scope)
  AND (:category_id IS NULL OR n.category_id = :category_id)
  AND (:app_id IS NULL OR n.app_id = :app_id)
  -- 슬라이드/노출용 기간 필터 (now 기준)
  AND (n.start_at IS NULL OR n.start_at <= :now)
  AND (n.end_at IS NULL OR n.end_at >= :now)
ORDER BY
  n.priority DESC,
  n.created_at DESC
LIMIT :limit OFFSET :offset
""")


SQL_GET_NOTICE = text("""
SELECT
  n.id,
  n.scope,
  n.category_id,
  n.app_id,
  n.title,
  n.body,
  n.kind,
  n.start_at,
  n.end_at,
  n.priority,
  n.created_by,
  n.created_at
FROM notices n
WHERE n.id = :id
LIMIT 1
""")


SQL_CREATE_NOTICE = text("""
INSERT INTO notices
(scope, category_id, app_id, title, body, kind, start_at, end_at, priority, created_by)
VALUES
(:scope, :category_id, :app_id, :title, :body, :kind, :start_at, :end_at, :priority, :created_by)
""")


SQL_UPDATE_NOTICE = text("""
UPDATE notices
SET
  scope = :scope,
  category_id = :category_id,
  app_id = :app_id,
  title = :title,
  body = :body,
  kind = :kind,
  start_at = :start_at,
  end_at = :end_at,
  priority = :priority
WHERE id = :id
""")


SQL_DELETE_NOTICE = text("""
DELETE FROM notices WHERE id = :id
""")


async def list_notices(
    db: AsyncSession,
    *,
    scope: Optional[str] = None,        # all/apphub/category/app
    category_id: Optional[int] = None,
    app_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    now: Optional[datetime] = None,
) -> list[dict]:
    if now is None:
        now = datetime.utcnow()

    res = await db.execute(
        SQL_LIST_NOTICES,
        {
            "scope": scope,
            "category_id": category_id,
            "app_id": app_id,
            "now": now,
            "limit": int(limit),
            "offset": int(offset),
        },
    )
    rows = res.mappings().all()
    return [dict(r) for r in rows]


async def get_notice(db: AsyncSession, notice_id: int) -> dict | None:
    res = await db.execute(SQL_GET_NOTICE, {"id": int(notice_id)})
    row = res.mappings().first()
    return dict(row) if row else None


async def create_notice(
    db: AsyncSession,
    *,
    scope: str,
    title: str,
    body: str,
    kind: str,
    created_by: int,
    category_id: Optional[int] = None,
    app_id: Optional[int] = None,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    priority: int = 0,
) -> int:
    await db.execute(
        SQL_CREATE_NOTICE,
        {
            "scope": scope,
            "category_id": category_id,
            "app_id": app_id,
            "title": title,
            "body": body,
            "kind": kind,
            "start_at": start_at,
            "end_at": end_at,
            "priority": int(priority),
            "created_by": int(created_by),
        },
    )
    res = await db.execute(text("SELECT LAST_INSERT_ID()"))
    notice_id = int(res.scalar_one())
    await db.commit()
    return notice_id


async def update_notice(
    db: AsyncSession,
    notice_id: int,
    *,
    scope: str,
    title: str,
    body: str,
    kind: str,
    category_id: Optional[int] = None,
    app_id: Optional[int] = None,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    priority: int = 0,
) -> None:
    await db.execute(
        SQL_UPDATE_NOTICE,
        {
            "id": int(notice_id),
            "scope": scope,
            "category_id": category_id,
            "app_id": app_id,
            "title": title,
            "body": body,
            "kind": kind,
            "start_at": start_at,
            "end_at": end_at,
            "priority": int(priority),
        },
    )
    await db.commit()


async def delete_notice(db: AsyncSession, notice_id: int) -> None:
    await db.execute(SQL_DELETE_NOTICE, {"id": int(notice_id)})
    await db.commit()
