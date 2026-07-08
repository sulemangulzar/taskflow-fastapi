import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request

from app.core.config import settings

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def _comma_separated(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _allowed_hosts() -> list[str]:
    hosts = _comma_separated(settings.ALLOWED_HOSTS)
    for test_host in ("test", "testserver"):
        if test_host not in hosts:
            hosts.append(test_host)
    return hosts


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else "unknown"

        message = f"{client_host} - {client_port} - {request.method} - {request.url.path} - Processed in {processing_time:.4f}s"
        print(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_comma_separated(settings.FRONTEND_ORIGINS),
        allow_origin_regex=settings.CORS_ORIGIN_REGEX,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=_allowed_hosts(),
    )
