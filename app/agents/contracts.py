"""
Shared contracts for the ERP Sales Intelligence multi-agent tool.

Each agent returns a typed JSON payload so the unified tool, API, and UI
can display six distinct agent results (plus a final report).
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class AgentMeta(TypedDict):
    agent_id: str
    agent_name: str
    version: str
    status: str  # completed | skipped | failed
    duration_ms: int
    notes: list[str]


class AgentState(TypedDict, total=False):
    """LangGraph / pipeline shared state."""

    company_name: str
    website: str
    country: Optional[str]
    industry: Optional[str]
    crawl: dict[str, Any]
    # Six analysis agents
    website_intelligence: dict[str, Any]
    technologies: list[dict[str, Any]]
    technology_detection: dict[str, Any]
    erp_opportunity: dict[str, Any]
    hiring_analysis: dict[str, Any]
    decision_makers: list[dict[str, Any]]
    decision_maker_finder: dict[str, Any]
    lead_score: dict[str, Any]
    # Final synthesis
    report: dict[str, Any]
    news: list[dict[str, Any]]
    agent_trace: list[dict[str, Any]]
    errors: list[str]


def new_state(
    *,
    company_name: str,
    website: str,
    country: str | None = None,
    industry: str | None = None,
) -> AgentState:
    return {
        "company_name": company_name,
        "website": website,
        "country": country,
        "industry": industry,
        "errors": [],
        "agent_trace": [],
        "news": [],
        "technologies": [],
        "decision_makers": [],
    }


def corpus_text(state: AgentState) -> str:
    """Primary text corpus used by agents after crawl."""
    crawl = state.get("crawl") or {}
    return (crawl.get("combined_text") or "")[:80000]
