"""
Agent 4 — Hiring Intelligence Agent.

Analyzes careers pages / crawl text for ERP, SAP, IFS, Oracle, Infor,
Cloud, DevOps, and Database hiring signals.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentState, find_keyword_hits
from app.agents.catalogs import HIRING_KEYWORDS
from app.core.logging import get_logger
from app.services.crawler.engine import WebsiteCrawler

logger = get_logger(__name__)


class HiringIntelligenceAgent:
    name = "hiring_intelligence"

    async def run(self, state: AgentState) -> AgentState:
        crawl = state.get("crawl") or {}
        text = crawl.get("combined_text") or ""
        careers_urls = crawl.get("careers_urls") or []

        # Deep-dive a careers URL when available
        careers_text = ""
        if careers_urls:
            try:
                result = await WebsiteCrawler().crawl(careers_urls[0], max_pages=3)
                careers_text = result.combined_text
            except Exception as exc:  # noqa: BLE001
                logger.warning("Careers crawl failed: %s", exc)

        corpus = f"{text}\n{careers_text}"
        categories: dict[str, Any] = {}
        for category, keywords in HIRING_KEYWORDS.items():
            hits = find_keyword_hits(corpus, keywords)
            if hits:
                categories[category] = hits

        # Hiring score 0–100
        score = 0
        weights = {
            "ERP": 20,
            "SAP": 18,
            "IFS": 18,
            "Oracle": 15,
            "Infor": 12,
            "Cloud": 10,
            "DevOps": 8,
            "Database": 8,
        }
        for category, points in weights.items():
            if category in categories:
                score += points
        score = min(score, 100)

        payload = {
            "hiring_score": score,
            "categories": categories,
            "careers_urls": careers_urls,
            "open_roles_estimated": len(categories) * 2 if categories else 0,
            "summary": (
                f"Detected hiring signals in {', '.join(categories.keys())}."
                if categories
                else "No strong ERP/cloud hiring signals detected."
            ),
        }
        return {**state, "hiring_analysis": payload}


async def hiring_intelligence_node(state: AgentState) -> AgentState:
    return await HiringIntelligenceAgent().run(state)
