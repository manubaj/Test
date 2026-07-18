"""Lightweight integration checks that do not require PostgreSQL."""

from __future__ import annotations

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-characters")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://aisales:aisales_secret@localhost:5432/aisales",
)


def test_create_app_importable() -> None:
    from app.main import create_app

    app = create_app()
    schema_paths = set(app.openapi().get("paths", {}).keys())
    assert "/api/v1/health" in schema_paths
    assert "/api/v1/companies" in schema_paths
    assert "/api/v1/analysis" in schema_paths
    assert "/docs" in {getattr(r, "path", None) for r in app.routes}


def test_workflow_importable() -> None:
    from app.agents.workflow import run_analysis_workflow

    assert callable(run_analysis_workflow)
