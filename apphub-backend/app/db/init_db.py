from loguru import logger
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# 모델 import (create_all 위해 필요)
from app.models import auth, apps, access, notices, jobs, events, sessions, metrics  # noqa: F401

async def init_db_if_needed() -> None:
    if not settings.APP_INIT_DB:
        logger.info("APP_INIT_DB=false -> skip create_all()")
        return

    logger.warning("APP_INIT_DB=true -> creating tables via SQLAlchemy (DEV ONLY)")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.warning("create_all() done")
