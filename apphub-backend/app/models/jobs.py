import enum
from sqlalchemy import String, BigInteger, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class JobType(str, enum.Enum):
    download = "download"
    update = "update"
    upload = "upload"

class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"
    canceled = "canceled"

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    job_type: Mapped[JobType] = mapped_column(SAEnum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    started_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)

class JobItem(Base):
    __tablename__ = "job_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("jobs.id"), nullable=False)
    app_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("apps.id"), nullable=False)
    app_version_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("app_versions.id"), nullable=True)
    artifact_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("app_artifacts.id"), nullable=True)

    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
