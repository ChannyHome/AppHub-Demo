import enum
from sqlalchemy import String, BigInteger, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class NoticeScope(str, enum.Enum):
    all = "all"
    apphub = "apphub"
    category = "category"
    app = "app"

class NoticeKind(str, enum.Enum):
    release = "release"
    upload = "upload"
    maintenance = "maintenance"
    manual = "manual"
    general = "general"

class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    scope: Mapped[NoticeScope] = mapped_column(SAEnum(NoticeScope), nullable=False)

    category_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("app_categories.id"), nullable=True)
    app_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("apps.id"), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)  # MEDIUMTEXT는 String/Text로 OK

    kind: Mapped[NoticeKind] = mapped_column(SAEnum(NoticeKind), nullable=False)

    start_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)
    end_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
