from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

SQL_USER_BY_KNOX = text("""
SELECT
  u.id,
  u.knox_id,
  u.name,
  u.dept_name,
  u.description,
  u.role_id,
  u.is_active,
  r.name AS role_name,
  r.role_rank AS role_rank
FROM users u
JOIN roles r ON r.id = u.role_id
WHERE u.knox_id = :knox_id
LIMIT 1
""")

async def get_user_by_knox_id(db: AsyncSession, knox_id: str) -> dict | None:
    res = await db.execute(SQL_USER_BY_KNOX, {"knox_id": knox_id})
    row = res.mappings().first()
    return dict(row) if row else None
