from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core.security import require
from app.schemas.metrics import BatchRunRequest
from app.services.metrics_service import run_daily_batch

router = APIRouter(prefix="/metrics")

@router.post("/daily/run")
async def run_daily(payload: BatchRunRequest, me=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Maintainer/Admin만 배치 실행 허용(정책은 조정 가능)
    require(me["role_name"] in ("Maintainer", "Admin"), "Only Maintainer/Admin can run batch")
    await run_daily_batch(db, payload.metric_date)
    return {"ok": True, "metric_date": payload.metric_date}
