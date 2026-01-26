from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NoticeOut(BaseModel):
    id: int
    scope: str
    category_id: Optional[int] = None
    app_id: Optional[int] = None
    title: str
    body: str
    kind: str
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    priority: int
    created_by: int
    created_at: datetime


class NoticeCreate(BaseModel):
    scope: str = Field(..., description="all/apphub/category/app")
    title: str
    body: str
    kind: str = Field(..., description="release/upload/maintenance/manual/general")
    category_id: Optional[int] = None
    app_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    priority: int = 0


class NoticeUpdate(BaseModel):
    scope: str = Field(..., description="all/apphub/category/app")
    title: str
    body: str
    kind: str = Field(..., description="release/upload/maintenance/manual/general")
    category_id: Optional[int] = None
    app_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    priority: int = 0
