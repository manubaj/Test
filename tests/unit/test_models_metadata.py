"""Ensure ORM metadata still registers all required tables."""

from __future__ import annotations

from app.database import Base
from app.models import EXPECTED_TABLES
import app.models  # noqa: F401


def test_all_expected_tables_registered() -> None:
    registered = set(Base.metadata.tables.keys())
    for table in EXPECTED_TABLES:
        assert table in registered
