"""
FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __app_name__, __version__
from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import get_logger, setup_logging
from app.core.security import hash_api_key, hash_password
from app.database.session import AsyncSessionLocal, init_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import UserRepository

logger = get_logger(__name__)


async def bootstrap_admin() -> None:
    """
    Ensure the demo admin account always exists with the configured password.

    Password is reset on every startup so Docker image upgrades cannot leave
    an unusable hash in Postgres volumes.
    """
    settings = get_settings()
    email = settings.bootstrap_admin_email.lower().strip()
    password = settings.bootstrap_admin_password

    async with AsyncSessionLocal() as session:
        users = UserRepository(session)
        existing = await users.get_by_email(email)
        password_hash = hash_password(password)
        api_hash = hash_api_key(settings.bootstrap_admin_api_key)

        if existing:
            existing.hashed_password = password_hash
            existing.api_key_hash = api_hash
            existing.is_active = True
            existing.role = UserRole.ADMIN
            existing.username = settings.bootstrap_admin_username
            await session.commit()
            logger.info("Bootstrap admin updated email=%s", email)
            return

        admin = User(
            email=email,
            username=settings.bootstrap_admin_username,
            hashed_password=password_hash,
            full_name="Platform Admin",
            role=UserRole.ADMIN,
            api_key_hash=api_hash,
            is_active=True,
        )
        await users.add(admin)
        await session.commit()
        logger.info("Bootstrap admin created email=%s", email)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    setup_logging("DEBUG" if settings.debug else "INFO", app_name=settings.app_name)
    logger.info(
        "Starting %s v%s db=%s",
        settings.app_name,
        __version__,
        settings.database_url.split("@")[-1] if "@" in settings.database_url else "(set)",
    )
    # Retry DB init — Postgres may still be accepting connections during boot
    import asyncio

    last_error: Exception | None = None
    for attempt in range(1, 16):
        try:
            await init_db()
            await bootstrap_admin()
            last_error = None
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("DB bootstrap attempt %s failed: %s", attempt, exc)
            await asyncio.sleep(2)
    if last_error:
        logger.error("DB bootstrap failed after retries: %s", last_error)
        raise last_error

    yield
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "AI Sales Intelligence Platform for ERP opportunities "
            "(IFS, SAP, Oracle, Infor, Microsoft Dynamics). "
            "Local/open-source inference via Ollama by default."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # In development allow any localhost / 127.0.0.1 origin to avoid CORS login blocks
    cors_kwargs: dict = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if settings.is_development:
        cors_kwargs["allow_origin_regex"] = (
            r"https?://(localhost|127\.0\.0\.1|frontend)(:\d+)?"
        )
    else:
        cors_kwargs["allow_origins"] = settings.cors_origin_list

    application.add_middleware(CORSMiddleware, **cors_kwargs)

    @application.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    @application.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": "internal_error",
                "message": str(exc) if settings.debug else "Internal server error",
                "details": None,
            },
        )

    application.include_router(api_router, prefix=settings.api_prefix)

    @application.get("/")
    async def root() -> dict:
        return {
            "name": __app_name__,
            "version": __version__,
            "docs": "/docs",
            "api": settings.api_prefix,
            "login": {
                "email": settings.bootstrap_admin_email,
                "password_hint": "see BOOTSTRAP_ADMIN_PASSWORD / Admin123!",
            },
        }

    return application


app = create_app()
