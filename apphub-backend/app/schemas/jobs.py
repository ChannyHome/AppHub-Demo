from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class JobOut(BaseModel):
    id: int
    user_id: int
    job_type: str
    status: str
    progress: int
    message: Optional[str] = None

class JobCreate(BaseModel):
    user_id: int
    job_type: str = Field(..., description="download/update/upload")
    status: str = Field(default="queued", description="queued/running/success/failed/canceled")
    progress: int = 0
    message: Optional[str] = None

class JobUpdate(BaseModel):
    status: str
    progress: int = Field(ge=0, le=100)
    message: Optional[str] = None
