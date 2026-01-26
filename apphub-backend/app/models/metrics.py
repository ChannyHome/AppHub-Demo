from sqlalchemy import BigInteger, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class HubDailyMetric(Base):
    __tablename__ = "hub_daily_metrics"

    metric_date: Mapped[str] = mapped_column(Date, primary_key=True)
    dau: Mapped[int] = mapped_column(Integer, nullable=False)
    page_open_count: Mapped[int] = mapped_column(Integer, nullable=False)
    search_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)

class AppDailyMetric(Base):
    __tablename__ = "app_daily_metrics"

    metric_date: Mapped[str] = mapped_column(Date, primary_key=True)
    app_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("apps.id"), primary_key=True)

    unique_users: Mapped[int] = mapped_column(Integer, nullable=False)
    launch_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_runtime_sec: Mapped[int] = mapped_column(BigInteger, nullable=False)
    action_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
