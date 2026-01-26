import os
import time
import json
from typing import Callable, Optional

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import ORJSONResponse

from app.core.config import settings


def setup_logging() -> None:
    """
    - logs/apphub.log      : 일반 앱 로그
    - logs/access.log      : 요청/응답(액세스) 로그
    - logs/error.log       : 에러 로그(스택 포함)
    """
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    # 기본 핸들러 제거
    logger.remove()

    # 일반 로그
    logger.add(
        os.path.join(settings.LOG_DIR, "apphub.log"),
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="14 days",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    # 에러 로그
    logger.add(
        os.path.join(settings.LOG_DIR, "error.log"),
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # access 로그 (extra.access=True 인 것만)
    logger.add(
        os.path.join(settings.LOG_DIR, "access.log"),
        level="INFO",
        rotation="50 MB",
        retention="14 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("access") is True,
    )


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    요청/응답 요약을 access.log에 남긴다.
    - body는 너무 크면 MAX_BODY까지만 기록
    - 예외가 터져도 access.log에 500 에러 로그가 남도록 처리
    """
    MAX_BODY = 2048

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()

        # request body는 한 번 읽으면 stream 소모되므로 복구해줘야 함
        body_bytes = await request.body()
        if body_bytes:
            request._receive = _receive_with_body(body_bytes)

        try:
            response = await call_next(request)
        except Exception as e:
            took_ms = int((time.time() - start) * 1000)
            _log_access(
                request=request,
                status_code=500,
                took_ms=took_ms,
                request_body_bytes=body_bytes,
                error=str(e),
            )
            # 에러는 error.log에도 스택으로 남김
            logger.exception(f"Unhandled exception: {e}")

            # 응답은 JSON으로 통일 (프론트/Swagger 확인 편함)
            return ORJSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        took_ms = int((time.time() - start) * 1000)
        _log_access(
            request=request,
            status_code=response.status_code,
            took_ms=took_ms,
            request_body_bytes=body_bytes,
            error=None,
        )
        return response


def _log_access(
    request: Request,
    status_code: int,
    took_ms: int,
    request_body_bytes: bytes,
    error: Optional[str],
) -> None:
    # body 잘라서 기록
    req_body = None
    if request_body_bytes:
        req_body = request_body_bytes[: RequestResponseLoggingMiddleware.MAX_BODY].decode(
            "utf-8", errors="ignore"
        )

    payload = {
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "status_code": status_code,
        "took_ms": took_ms,
        "client": request.client.host if request.client else None,
        "knox_id": request.headers.get(settings.AUTH_KNOX_HEADER),
        "request_body": req_body if req_body else None,
        "error": error,
    }

    # 한 줄 JSON 로그로 남김
    logger.bind(access=True).info(json.dumps(payload, ensure_ascii=False))


def _receive_with_body(body: bytes):
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return receive
