"""
Agent 4 — Hiring Intelligence Agent

Analyzes careers pages and detects hiring for ERP, SAP, IFS, Oracle,
Infor, Cloud, DevOps, Database. Generates hiring score.
"""

from __future__ import annotations

from typing import Any

from app.agents.catalogs import HIRING_KEYWORDS
from app.agents.contracts import AgentState, corpus_text
from app.agents.runtime import append_trace, evidence_snippet, find_keyword_hits, timed_agent
from app.core.logging import get_logger
from app.services.crawler.engine import WebsiteCrawler

logger = get_logger(__name__)

AGENT_ID = "agent_4_hiring_intelligence"
AGENT_NAME = "Hiring Intelligence Agent"

CATEGORY_WEIGHTS = {
    "ERP": 20,
    "SAP": 18,
    "IFS": 18,
    "Oracle": 15,
    "Infor": 12,
    "Cloud": 10,
    "DevOps": 8,
    "Database": 8,
}


class HiringIntelligenceAgent:
    name = AGENT_ID

    async def run(self, state: AgentState) -> AgentState:
        with timed_agent(AGENT_ID, AGENT_NAME) as meta:
            crawl = state.get("crawl") or {}
            text = corpus_text(state)
            careers_urls = list(crawl.get("careers_urls") or [])

            careers_text = ""
            careers_pages = 0
            if careers_urls:
                try:
                    result = await WebsiteCrawler().crawl(careers_urls[0], max_pages=4)
                    careers_text = result.combined_text
                    careers_pages = len(result.pages)
                    meta["notes"].append(f"Careers crawl pages={careers_pages}")
                except Exception as exc:  # noqa: BLE001
                    meta["notes"].append(f"Careers crawl failed: {exc}")

            corpus = f"{text}\n{careers_text}"
            categories: dict[str, Any] = {}
            for category, keywords in HIRING_KEYWORDS.items():
                hits = find_keyword_hits(corpus, keywords)
                if hits:
                    categories[category] = {
                        "matched_keywords": hits,
                        "evidence": evidence_snippet(corpus, hits[0]),
                        "points": CATEGORY_WEIGHTS.get(category, 5),
                    }

            score = 0
            for category in categories:
                score += CATEGORY_WEIGHTS.get(category, 5)
            score = min(score, 100)

            erp_hiring = any(
                k in categories for k in ("ERP", "SAP", "IFS", "Oracle", "Infor")
            )
            payload = {
                "agent": AGENT_NAME,
                "hiring_score": score,
                "erp_related_hiring": erp_hiring,
                "categories": categories,
                "careers_urls": careers_urls,
                "careers_pages_analyzed": careers_pages,
                "open_roles_estimated": max(len(categories) * 2, 0),
                "summary": (
                    f"Hiring score {score}/100. "
                    + (
                        f"Signals in: {', '.join(categories.keys())}."
                        if categories
                        else "No strong ERP/cloud hiring signals detected."
                    )
                ),
            }
            state = {**state, "hiring_analysis": payload}
            return append_trace(state, meta)


async def hiring_intelligence_node(state: AgentState) -> AgentState:
    return await HiringIntelligenceAgent().run(state)
