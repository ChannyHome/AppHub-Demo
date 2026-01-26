from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class AccessRowOut(BaseModel):
    id: int
    user_id: int
    status: str
    requested_at: str
    approved_by: Optional[int] = None
    approved_at: Optional[str] = None
    note: Optional[str] = None

class AccessDecision(BaseModel):
    status: str  # approved/rejected/revoked
    note: Optional[str] = None
