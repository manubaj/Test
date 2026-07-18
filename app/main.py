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
    """Ensure a default admin user exists for first-run demos."""
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        users = UserRepository(session)
        existing = await users.get_by_email(settings.bootstrap_admin_email.lower())
        if existing:
            return
        admin = User(
            email=settings.bootstrap_admin_email.lower(),
            username=settings.bootstrap_admin_username,
            hashed_password=hash_password(settings.bootstrap_admin_password),
            full_name="Platform Admin",
            role=UserRole.ADMIN,
            api_key_hash=hash_api_key(settings.bootstrap_admin_api_key),
            is_active=True,
        )
        await users.add(admin)
        await session.commit()
        logger.info(
            "Bootstrap admin created email=%s api_key_configured=true",
            settings.bootstrap_admin_email,
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    setup_logging("DEBUG" if settings.debug else "INFO", app_name=settings.app_name)
    logger.info("Starting %s v%s", settings.app_name, __version__)
    await init_db()
    await bootstrap_admin()
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

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    application.include_router(api_router, prefix=settings.api_prefix)

    @application.get("/")
    async def root() -> dict:
        return {
            "name": __app_name__,
            "version": __version__,
            "docs": "/docs",
            "api": settings.api_prefix,
        }

    return application


app = create_app()
