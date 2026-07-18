#!/usr/bin/env python3
"""
Offline smoke test for the agent pipeline (no database required).

    python scripts/smoke_agents.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agents.workflow.graph import run_analysis_workflow  # noqa: E402


async def main() -> int:
    # Use example.com for a fast public crawl during smoke tests
    state = await run_analysis_workflow(
        company_name="Example Co",
        website="https://example.com",
        industry="Technology",
    )
    print("Lead score:", (state.get("lead_score") or {}).get("score"))
    print("Technologies:", [t.get("name") for t in state.get("technologies") or []])
    print("Opportunities:", (state.get("erp_opportunity") or {}).get("opportunities"))
    print("Report priority:", (state.get("report") or {}).get("priority"))
    print("SMOKE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
