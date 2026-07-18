#!/usr/bin/env python3
"""
Module 2 verification script.

Validates that all required ORM tables are registered on Base.metadata,
that foreign-key relationships resolve, and that PostgreSQL DDL can be
compiled for each table (no live database required).

Run from the repository root:

    pip3 install -r requirements.txt
    python3 scripts/verify_models.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    """Run model metadata checks and return process exit code."""
    print("AI Sales Intelligence Platform — Module 2 Model Check")
    print("=" * 60)

    try:
        from sqlalchemy.dialects import postgresql
        from sqlalchemy.schema import CreateTable

        from app.database import Base
        from app.models import EXPECTED_TABLES
        import app.models  # noqa: F401 — ensure all models are imported
    except Exception as exc:
        print(f"Import FAILED: {exc}")
        print("Hint: pip3 install -r requirements.txt")
        return 1

    registered = set(Base.metadata.tables.keys())
    print(f"Registered tables: {len(registered)}")
    for name in sorted(registered):
        print(f"  - {name}")

    print("-" * 60)
    missing = [name for name in EXPECTED_TABLES if name not in registered]
    for name in EXPECTED_TABLES:
        status = "OK" if name in registered else "MISSING"
        print(f"[{status}] table {name}")

    if missing:
        print(f"\nMissing tables: {missing}")
        return 1

    # Relationship / FK sanity: every FK target must exist
    print("-" * 60)
    fk_errors: list[str] = []
    for table_name, table in Base.metadata.tables.items():
        for fk in table.foreign_keys:
            target = fk.column.table.name
            if target not in registered:
                fk_errors.append(f"{table_name}.{fk.parent.name} -> {target}")
            else:
                print(f"[OK] FK {table_name}.{fk.parent.name} -> {target}.{fk.column.name}")

    if fk_errors:
        print("Foreign key resolution FAILED:")
        for err in fk_errors:
            print(f"  - {err}")
        return 1

    # Compile PostgreSQL DDL to catch dialect-level definition errors
    print("-" * 60)
    dialect = postgresql.dialect()
    for table_name in EXPECTED_TABLES:
        table = Base.metadata.tables[table_name]
        try:
            ddl = str(CreateTable(table).compile(dialect=dialect))
            assert "CREATE TABLE" in ddl.upper()
            print(f"[OK] DDL compile {table_name} ({len(ddl)} chars)")
        except Exception as exc:
            print(f"[FAIL] DDL compile {table_name}: {exc}")
            return 1

    # Quick entity smoke: instantiate in-memory objects (not persisted)
    print("-" * 60)
    from decimal import Decimal
    from uuid import uuid4

    from app.models import (
        Company,
        LeadScore,
        User,
        UserRole,
    )

    company_id = uuid4()
    analysis_id = uuid4()
    user = User(
        id=uuid4(),
        email="analyst@example.com",
        username="analyst",
        hashed_password="not-a-real-hash",
        role=UserRole.ANALYST,
    )
    company = Company(
        id=company_id,
        name="Acme Manufacturing",
        website="https://acme.example",
        country="US",
    )
    score = LeadScore(
        id=uuid4(),
        company_id=company_id,
        analysis_id=analysis_id,
        score=Decimal("75.00"),
        explanation="ERP detected + hiring signals",
        factors=[{"name": "ERP Detected", "points": 30}],
    )
    print(f"[OK] instantiate {user!r}")
    print(f"[OK] instantiate {company!r}")
    print(f"[OK] instantiate {score!r}")

    print("=" * 60)
    print("Model check PASSED. Ready for Module 3 after approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
