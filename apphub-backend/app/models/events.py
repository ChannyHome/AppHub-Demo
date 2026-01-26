import enum
from sqlalchemy import String, BigInteger, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class HubEventType(str, enum.Enum):
    page_open = "page_open"
    search = "search"
    filter_change = "filter_change"
    sort_change = "sort_change"
    open_notice = "open_notice"
    open_app_detail = "open_app_detail"
    open_permission_request = "open_permission_request"
    app_action = "app_action"

class HubPage(str, enum.Enum):
    home = "home"
    apps = "apps"
    upload = "upload"
    library = "library"
    permission = "permission"
    notices = "notices"

class HubEvent(Base):
    __tablename__ = "hub_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    occurred_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

    event_type: Mapped[HubEventType] = mapped_column(SAEnum(HubEventType), nullable=False)
    page: Mapped[HubPage] = mapped_column(SAEnum(HubPage), nullable=False)

    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meta_json: Mapped[str | None] = mapped_column(String, nullable=True)  # JSON 컬럼이지만 문자열로 받기 OK

    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
