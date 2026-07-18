"""
AI Sales Intelligence Platform — application package root.

This package follows clean architecture:
- api/          HTTP layer (FastAPI routers, dependencies)
- services/     Business logic and orchestration helpers
- agents/       Independent AI agents and LangGraph workflow
- repositories/ Data access (repository pattern)
- models/       SQLAlchemy ORM models
- database/     Engine, session, and migration helpers
- schemas/      Pydantic request/response schemas
- utils/        Shared helpers (logging, NLP, export)
- core/         Configuration, security, and cross-cutting concerns
"""

__version__ = "0.1.0"
__app_name__ = "AI Sales Intelligence Platform"
