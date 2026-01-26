from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_min_role_rank
from app.schemas.access import AccessRowOut, AccessDecision
from app.services.access_service import (
    list_category_access, get_category_access, decide_category_access, delete_category_access,
    list_app_access, get_app_access, decide_app_access, delete_app_access,
)

router = APIRouter(prefix="/access")


# ---- Category Access (관리용) ----
@router.get("/category", response_model=list[AccessRowOut], dependencies=[Depends(require_min_role_rank(40))])
async def list_category_access_api(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    rows = await list_category_access(db, limit=limit, offset=offset)
    return [AccessRowOut(**r) for r in rows]


@router.put("/category/{row_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(40))])
async def decide_category_access_api(
    row_id: int,
    body: AccessDecision,
    db: AsyncSession = Depends(get_db),
    me: dict = Depends(get_current_user),
):
    row = await get_category_access(db, row_id)
    if not row:
        raise HTTPException(404, "Category access row not found")
    await decide_category_access(db, row_id, status=body.status, approved_by=me["id"], note=body.note)
    return {"ok": True}


@router.delete("/category/{row_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(40))])
async def delete_category_access_api(row_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_category_access(db, row_id):
        raise HTTPException(404, "Category access row not found")
    await delete_category_access(db, row_id)
    return {"ok": True}


# ---- App Access (관리용) ----
@router.get("/app", response_model=list[AccessRowOut], dependencies=[Depends(require_min_role_rank(40))])
async def list_app_access_api(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    rows = await list_app_access(db, limit=limit, offset=offset)
    return [AccessRowOut(**r) for r in rows]


@router.put("/app/{row_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(40))])
async def decide_app_access_api(
    row_id: int,
    body: AccessDecision,
    db: AsyncSession = Depends(get_db),
    me: dict = Depends(get_current_user),
):
    row = await get_app_access(db, row_id)
    if not row:
        raise HTTPException(404, "App access row not found")
    await decide_app_access(db, row_id, status=body.status, approved_by=me["id"], note=body.note)
    return {"ok": True}


@router.delete("/app/{row_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(40))])
async def delete_app_access_api(row_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_app_access(db, row_id):
        raise HTTPException(404, "App access row not found")
    await delete_app_access(db, row_id)
    return {"ok": True}
