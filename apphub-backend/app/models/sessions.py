import enum
from sqlalchemy import String, BigInteger, DateTime, ForeignKey, Enum as SAEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class EndReason(str, enum.Enum):
    user_exit = "user_exit"
    crash = "crash"
    killed = "killed"
    unknown = "unknown"

class Severity(str, enum.Enum):
    info = "info"
    warn = "warn"
    error = "error"

class AppRunSession(Base):
    __tablename__ = "app_run_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    knox_id_raw: Mapped[str | None] = mapped_column(String(64), nullable=True)

    app_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("apps.id"), nullable=False)
    app_version: Mapped[str] = mapped_column(String(40), nullable=False)

    started_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)

    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_reason: Mapped[EndReason] = mapped_column(SAEnum(EndReason), nullable=False, default=EndReason.unknown)

    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)

class AppActionEvent(Base):
    __tablename__ = "app_action_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("app_run_sessions.id"), nullable=False)

    occurred_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_name: Mapped[str] = mapped_column(String(120), nullable=False)

    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    severity: Mapped[Severity] = mapped_column(SAEnum(Severity), nullable=False, default=Severity.info)
    meta_json: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
