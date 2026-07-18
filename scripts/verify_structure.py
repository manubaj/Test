#!/usr/bin/env python3
"""
Module 1 verification script.

Checks that the clean-architecture folder layout exists and that
Python packages under app/ and tests/ are importable as namespaces.
Run from the repository root:

    python3 scripts/verify_structure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Repository root (parent of scripts/)
ROOT = Path(__file__).resolve().parent.parent

# Required directories for Module 1
REQUIRED_DIRS: list[str] = [
    "app",
    "app/api",
    "app/api/deps",
    "app/api/v1",
    "app/api/v1/endpoints",
    "app/services",
    "app/services/crawler",
    "app/services/analysis",
    "app/services/export",
    "app/agents",
    "app/agents/website_intelligence",
    "app/agents/erp_opportunity",
    "app/agents/technology_detection",
    "app/agents/hiring_intelligence",
    "app/agents/decision_maker",
    "app/agents/lead_scoring",
    "app/agents/report_generator",
    "app/agents/workflow",
    "app/repositories",
    "app/models",
    "app/database",
    "app/schemas",
    "app/utils",
    "app/core",
    "alembic",
    "alembic/versions",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/mocks",
    "frontend",
    "frontend/src",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/services",
    "frontend/src/hooks",
    "frontend/src/types",
    "frontend/src/assets",
    "frontend/public",
    "docs",
    "scripts",
    "data/faiss",
    "data/uploads",
    "docker/backend",
    "docker/frontend",
    "docker/ollama",
]

# Packages that must contain __init__.py
REQUIRED_PACKAGES: list[str] = [
    "app",
    "app/api",
    "app/api/deps",
    "app/api/v1",
    "app/api/v1/endpoints",
    "app/services",
    "app/services/crawler",
    "app/services/analysis",
    "app/services/export",
    "app/agents",
    "app/agents/website_intelligence",
    "app/agents/erp_opportunity",
    "app/agents/technology_detection",
    "app/agents/hiring_intelligence",
    "app/agents/decision_maker",
    "app/agents/lead_scoring",
    "app/agents/report_generator",
    "app/agents/workflow",
    "app/repositories",
    "app/models",
    "app/database",
    "app/schemas",
    "app/utils",
    "app/core",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/mocks",
]


def main() -> int:
    """Validate structure and return process exit code (0 = success)."""
    missing_dirs: list[str] = []
    missing_inits: list[str] = []

    print("AI Sales Intelligence Platform — Module 1 Structure Check")
    print("=" * 60)

    for relative in REQUIRED_DIRS:
        path = ROOT / relative
        ok = path.is_dir()
        status = "OK" if ok else "MISSING"
        print(f"[{status}] dir  {relative}")
        if not ok:
            missing_dirs.append(relative)

    print("-" * 60)

    for relative in REQUIRED_PACKAGES:
        init_file = ROOT / relative / "__init__.py"
        ok = init_file.is_file()
        status = "OK" if ok else "MISSING"
        print(f"[{status}] init {relative}/__init__.py")
        if not ok:
            missing_inits.append(relative)

    print("=" * 60)

    # Ensure app package is importable from repo root
    sys.path.insert(0, str(ROOT))
    try:
        import app  # noqa: WPS433 — intentional import for smoke test

        print(f"Import OK: {app.__app_name__} v{app.__version__}")
    except Exception as exc:  # pragma: no cover - defensive for setup errors
        print(f"Import FAILED: {exc}")
        return 1

    if missing_dirs or missing_inits:
        print("\nStructure check FAILED.")
        if missing_dirs:
            print(f"  Missing directories: {len(missing_dirs)}")
        if missing_inits:
            print(f"  Missing __init__.py: {len(missing_inits)}")
        return 1

    print("\nStructure check PASSED. Ready for Module 2 after approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
