from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SQL_ME = text("""
SELECT
  u.id AS user_id,
  u.knox_id,
  r.name AS role_name,
  r.role_rank
FROM users u
JOIN roles r ON r.id = u.role_id
WHERE u.knox_id = :knox_id
  AND u.is_active = 1
""")

async def get_me_by_knox(db: AsyncSession, knox_id: str):
    res = await db.execute(SQL_ME, {"knox_id": knox_id})
    row = res.mappings().first()
    return row
