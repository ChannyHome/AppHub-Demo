from pydantic import BaseModel

class MeResponse(BaseModel):
    user_id: int
    knox_id: str
    name: str
    dept_name: str
    role_name: str
    role_rank: int
