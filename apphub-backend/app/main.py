from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, RequestResponseLoggingMiddleware
from app.api.routers import api_router
from app.db.init_db import init_db_if_needed
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from app.db.session import engine
import asyncio

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
        default_response_class=ORJSONResponse,
    )

    # 요청/응답 로깅 미들웨어(파일로 남김)
    # app.add_middleware(RequestResponseLoggingMiddleware)
    app.add_middleware(RequestResponseLoggingMiddleware)
    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.219.2:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    async def _startup():
        await init_db_if_needed()

    @app.on_event("shutdown")
    async def _shutdown():
        await asyncio.sleep(0)
        await engine.dispose()

    # create_app() 안에 추가
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.exception(f"DB error: {exc}")
        return ORJSONResponse(
            status_code=500,
            content={"detail": "Database connection/query failed"}
        )        

    return app

app = create_app()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)