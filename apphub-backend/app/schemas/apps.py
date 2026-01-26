from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class AppOut(BaseModel):
    id: int
    category_id: int
    app_key: str
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    manual: Optional[str] = None
    voc: Optional[str] = None
    app_kind: str
    web_launch_url: Optional[str] = None
    is_active: int
    requires_app_approval: int
    latest_version_id: Optional[int] = None
    created_by: int

class AppCreate(BaseModel):
    category_id: int
    app_key: str = Field(..., max_length=80)
    name: str = Field(..., max_length=120)
    summary: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=512)
    manual: Optional[str] = Field(default=None, max_length=512)
    voc: Optional[str] = Field(default=None, max_length=512)
    app_kind: str = Field(..., description="native/web")
    web_launch_url: Optional[str] = Field(default=None, max_length=512)
    is_active: int = 1
    requires_app_approval: int = 0

class AppUpdate(BaseModel):
    category_id: int
    name: str = Field(..., max_length=120)
    summary: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=512)
    manual: Optional[str] = Field(default=None, max_length=512)
    voc: Optional[str] = Field(default=None, max_length=512)
    app_kind: str = Field(..., description="native/web")
    web_launch_url: Optional[str] = Field(default=None, max_length=512)
    is_active: int = 1
    requires_app_approval: int = 0
    latest_version_id: Optional[int] = None
