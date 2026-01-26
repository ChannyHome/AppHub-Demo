from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_min_role_rank
from app.schemas.jobs import JobOut, JobCreate, JobUpdate
from app.services.job_service import list_jobs, get_job, create_job, update_job, delete_job

router = APIRouter(prefix="/jobs")


@router.get("/", response_model=list[JobOut])
async def list_jobs_api(
    user_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _me: dict = Depends(get_current_user),
):
    rows = await list_jobs(db, user_id=user_id, limit=limit, offset=offset)
    return [JobOut(**r) for r in rows]


@router.get("/{job_id}", response_model=JobOut)
async def get_job_api(job_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    row = await get_job(db, job_id)
    if not row:
        raise HTTPException(404, "Job not found")
    return JobOut(**row)


@router.post("", response_model=dict)
async def create_job_api(body: JobCreate, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    new_id = await create_job(db, body.model_dump())
    return {"ok": True, "job_id": new_id}


@router.put("/{job_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(40))])
async def update_job_api(job_id: int, body: JobUpdate, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_job(db, job_id):
        raise HTTPException(404, "Job not found")
    await update_job(db, job_id, body.model_dump())
    return {"ok": True}


@router.delete("/{job_id}", response_model=dict, dependencies=[Depends(require_min_role_rank(40))])
async def delete_job_api(job_id: int, db: AsyncSession = Depends(get_db), _me: dict = Depends(get_current_user)):
    if not await get_job(db, job_id):
        raise HTTPException(404, "Job not found")
    await delete_job(db, job_id)
    return {"ok": True}
