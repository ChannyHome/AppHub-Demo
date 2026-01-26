from __future__ import annotations

from typing import AsyncGenerator, Optional, Callable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.user_service import get_user_by_knox_id

from typing import Optional
from fastapi import Header

def get_knox_id_optional(
    x_knox_id: Optional[str] = Header(default=None, alias="x-knox-id")
) -> Optional[str]:
    return x_knox_id

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency:
    - 요청마다 AsyncSession을 열고
    - 요청이 끝나면 자동으로 close
    """
    async with AsyncSessionLocal() as session:
        yield session


def get_knox_id(x_knox_id: Optional[str] = Header(default=None, alias="x-knox-id")) -> str:
    """
    FastAPI dependency:
    - 헤더에서 knox id 추출
    - 없으면 401
    """
    if not x_knox_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-knox-id header",
        )
    return x_knox_id


async def get_current_user(
    knox_id: str = Depends(get_knox_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    FastAPI dependency:
    - knox_id로 users 조회
    - 없으면 401
    - 비활성(is_active=0)이면 403
    반환 형태(서비스에서 dict로 받음):
      {id, knox_id, name, dept_name, role_id, role_name, role_rank, is_active}
    """
    me = await get_user_by_knox_id(db, knox_id)
    if not me:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    if int(me.get("is_active", 1)) != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return me


def require_min_role_rank(min_rank: int) -> Callable:
    """
    라우터에서 권한 제한이 필요할 때 사용.
    예: @router.post(..., dependencies=[Depends(require_min_role_rank(40))])
    """
    async def _checker(me: dict = Depends(get_current_user)) -> dict:
        if int(me["role_rank"]) < int(min_rank):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return me

    return _checker
