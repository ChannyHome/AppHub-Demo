from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_min_role_rank
from app.schemas.events import HubEventOut, HubEventUpdate
from app.services.hub_event_service import list_hub_events, get_hub_event, update_hub_event, delete_hub_event

router = APIRouter(prefix="/hub-events")


@router.get("/", response_model=list[HubEventOut], dependencies=[Depends(require_min_role_rank(40))])
async def list_hub_events_api(
    user_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    rows = await list_hub_events(db, user_id=user_id, limit=limit, offset=offset)
    return [HubEventOut(**r) for r in rows]


@router.get("/{event_id}", response_model=HubEventOut, dependencies=[Depends(require_min_role_rank(40))])
async def get_hub_event_api(event_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    row = await get_hub_event(db, event_id)
    if not row:
        raise HTTPException(404, "Hub event not found")
    return HubEventOut(**row)


@router.put("/{event_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(50))])
async def update_hub_event_api(event_id: int, body: HubEventUpdate, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_hub_event(db, event_id):
        raise HTTPException(404, "Hub event not found")
    await update_hub_event(db, event_id, body.description, body.meta_json)
    return {"ok": True}


@router.delete("/{event_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(50))])
async def delete_hub_event_api(event_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_hub_event(db, event_id):
        raise HTTPException(404, "Hub event not found")
    await delete_hub_event(db, event_id)
    return {"ok": True}
