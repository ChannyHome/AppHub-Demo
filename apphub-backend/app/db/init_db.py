from pathlib import Path
import re

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# 모델 import (create_all 위해 필요)
from app.models import auth, apps, access, notices, jobs, events, sessions, metrics  # noqa: F401


_DB_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _split_sql(sql: str) -> list[str]:
    # init.sql은 "DDL만"이고 DELIMITER가 없다는 전제 -> ; split로 충분
    lines = []
    for line in sql.splitlines():
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        lines.append(line)
    cleaned = "\n".join(lines)
    return [p.strip() for p in cleaned.split(";") if p.strip()]


async def _run_init_sql_if_db_missing() -> None:
    sql_path = Path(settings.APP_INIT_SQL_PATH)
    if not sql_path.exists():
        raise RuntimeError(f"init.sql not found: {sql_path}")

    bootstrap_engine = create_async_engine(
        settings.DATABASE_URL_ASYNC_BOOTSTRAP,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
    )

    try:
        async with bootstrap_engine.begin() as conn:
            r = await conn.execute(
                text("SELECT 1 FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME=:db"),
                {"db": settings.DB_NAME},
            )
            exists = r.first() is not None
            if exists:
                logger.info(f"[INIT_SQL] DB '{settings.DB_NAME}' exists -> skip init.sql")
                return

            logger.warning(f"[INIT_SQL] DB '{settings.DB_NAME}' missing -> executing init.sql")

            raw = sql_path.read_text(encoding="utf-8", errors="replace")
            for stmt in _split_sql(raw):
                await conn.execute(text(stmt))

            logger.warning("[INIT_SQL] init.sql done (DB + tables created)")
    finally:
        # DB가 존재해서 return하더라도 항상 dispose
        await bootstrap_engine.dispose()


async def _ensure_database_for_create_all() -> None:
    """APP_INIT_DB=true일 때 DB가 없으면 생성해 create_all()이 실패하지 않게 한다."""
    if not _DB_NAME_RE.fullmatch(settings.DB_NAME):
        raise RuntimeError("DB_NAME must contain only letters, numbers, underscores")

    bootstrap_engine = create_async_engine(
        settings.DATABASE_URL_ASYNC_BOOTSTRAP,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
    )

    try:
        async with bootstrap_engine.begin() as conn:
            await conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` "
                    "DEFAULT CHARACTER SET utf8mb4 "
                    "COLLATE utf8mb4_0900_ai_ci"
                )
            )
        logger.info(f"[INIT_DB] ensured DB '{settings.DB_NAME}' exists")
    finally:
        await bootstrap_engine.dispose()


async def init_db_if_needed() -> None:
    # 1) DB가 없으면 init.sql로 생성
    if settings.APP_INIT_SQL:
        await _run_init_sql_if_db_missing()
    else:
        logger.info("APP_INIT_SQL=false -> skip init.sql")

    # 2) 모델 기반 create_all() 옵션
    if not settings.APP_INIT_DB:
        logger.info("APP_INIT_DB=false -> skip create_all()")
        return

    logger.warning("APP_INIT_DB=true -> creating tables via SQLAlchemy (DEV ONLY)")
    await _ensure_database_for_create_all()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.warning("create_all() done")
