import enum
from sqlalchemy import String, BigInteger, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base

class AccessStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    revoked = "revoked"

class CategoryAccess(Base):
    __tablename__ = "category_access"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("app_categories.id"), nullable=False)

    status: Mapped[AccessStatus] = mapped_column(SAEnum(AccessStatus), nullable=False)
    requested_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    approved_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

class AppAccess(Base):
    __tablename__ = "app_access"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    app_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("apps.id"), nullable=False)

    status: Mapped[AccessStatus] = mapped_column(SAEnum(AccessStatus), nullable=False)
    requested_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    approved_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
