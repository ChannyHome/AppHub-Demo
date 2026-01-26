from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_min_role_rank
from app.schemas.apps import AppOut, AppCreate, AppUpdate
from app.services.app_service import list_apps, get_app, create_app, update_app, delete_app

router = APIRouter(prefix="/apps")


@router.get("/", response_model=list[AppOut])
async def list_apps_api(db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    rows = await list_apps(db, active_only=False)
    return [AppOut(**r) for r in rows]


@router.get("/{app_id}", response_model=AppOut)
async def get_app_api(app_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    row = await get_app(db, app_id)
    if not row:
        raise HTTPException(404, "App not found")
    return AppOut(**row)


@router.post("/", response_model=dict, dependencies=[Depends(require_min_role_rank(30))])
async def create_app_api(body: AppCreate, db: AsyncSession = Depends(get_db), me: dict = Depends(get_current_user)):
    new_id = await create_app(db, {**body.model_dump(), "latest_version_id": None, "created_by": me["id"]})
    return {"ok": True, "app_id": new_id}


@router.put("/{app_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(30))])
async def update_app_api(app_id: int, body: AppUpdate, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_app(db, app_id):
        raise HTTPException(404, "App not found")
    await update_app(db, app_id, body.model_dump())
    return {"ok": True}


@router.delete("/{app_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(40))])
async def delete_app_api(app_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_app(db, app_id):
        raise HTTPException(404, "App not found")
    await delete_app(db, app_id)  # soft delete
    return {"ok": True}
