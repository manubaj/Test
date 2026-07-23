"""Aggregate API v1 routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import agents, analysis, auth, companies, discovery, export, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(discovery.router)
api_router.include_router(companies.router)
api_router.include_router(analysis.router)
api_router.include_router(agents.router)
api_router.include_router(export.router)
