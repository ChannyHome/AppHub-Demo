from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.auth import MeResponse

router = APIRouter(prefix="/auth")

@router.get("/me", response_model=MeResponse)
async def me(current=Depends(get_current_user)):
    # current는 dict
    return MeResponse(
        user_id=current["id"],
        knox_id=current["knox_id"],
        name=current["name"],
        dept_name=current["dept_name"],
        role_name=current["role_name"],
        role_rank=current["role_rank"],
    )
