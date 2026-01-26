from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_min_role_rank
from app.schemas.notices import NoticeOut, NoticeCreate, NoticeUpdate
from app.services.notice_service import (
    list_notices,
    get_notice,
    create_notice,
    update_notice,
    delete_notice,
)


router = APIRouter(prefix="/notices")


@router.get("/", response_model=list[NoticeOut])
async def list_notices_api(
    scope: str | None = Query(default=None, description="all/apphub/category/app"),
    category_id: int | None = Query(default=None),
    app_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    rows = await list_notices(
        db,
        scope=scope,
        category_id=category_id,
        app_id=app_id,
        limit=limit,
        offset=offset,
    )
    return [NoticeOut(**r) for r in rows]


@router.get("/{notice_id}", response_model=NoticeOut)
async def get_notice_api(
    notice_id: int,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    row = await get_notice(db, notice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Notice not found")
    return NoticeOut(**row)


@router.post(
    "/",
    response_model=dict,
    dependencies=[Depends(require_min_role_rank(40))],  # Maintainer 이상
)
async def create_notice_api(
    body: NoticeCreate,
    db: AsyncSession = Depends(get_db),
    me: dict = Depends(get_current_user),
):
    new_id = await create_notice(
        db,
        scope=body.scope,
        title=body.title,
        body=body.body,
        kind=body.kind,
        created_by=me["id"],
        category_id=body.category_id,
        app_id=body.app_id,
        start_at=body.start_at,
        end_at=body.end_at,
        priority=body.priority,
    )
    return {"ok": True, "notice_id": new_id}


@router.put(
    "/{notice_id}",
    response_model=dict,
    dependencies=[Depends(require_min_role_rank(40))],  # Maintainer 이상
)
async def update_notice_api(
    notice_id: int,
    body: NoticeUpdate,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    existing = await get_notice(db, notice_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Notice not found")

    await update_notice(
        db,
        notice_id=notice_id,
        scope=body.scope,
        title=body.title,
        body=body.body,
        kind=body.kind,
        category_id=body.category_id,
        app_id=body.app_id,
        start_at=body.start_at,
        end_at=body.end_at,
        priority=body.priority,
    )
    return {"ok": True}


@router.delete(
    "/{notice_id}",
    response_model=dict,
    dependencies=[Depends(require_min_role_rank(40))],  # Maintainer 이상
)
async def delete_notice_api(
    notice_id: int,
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    existing = await get_notice(db, notice_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Notice not found")

    await delete_notice(db, notice_id)
    return {"ok": True}
