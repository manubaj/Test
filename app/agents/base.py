"""Shared agent state typing and helper utilities."""

from __future__ import annotations

import json
import re
from typing import Any, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """LangGraph shared state passed between agent nodes."""

    company_name: str
    website: str
    country: Optional[str]
    industry: Optional[str]
    crawl: dict[str, Any]
    website_intelligence: dict[str, Any]
    technologies: list[dict[str, Any]]
    erp_opportunity: dict[str, Any]
    hiring_analysis: dict[str, Any]
    decision_makers: list[dict[str, Any]]
    lead_score: dict[str, Any]
    report: dict[str, Any]
    news: list[dict[str, Any]]
    errors: list[str]


def find_keyword_hits(text: str, keywords: tuple[str, ...]) -> list[str]:
    """Return keywords found in text (case-insensitive)."""
    lowered = text.lower()
    return [kw for kw in keywords if kw.lower() in lowered]


def safe_json_loads(raw: Optional[str]) -> Optional[dict[str, Any]]:
    """Best-effort JSON extraction from LLM text."""
    if not raw:
        return None
    raw = raw.strip()
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
