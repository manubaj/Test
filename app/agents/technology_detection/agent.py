"""
Agent 3 — Technology Detection Agent.

Detects ERP, CRM, cloud, database, and DevOps technologies from crawl text.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentState
from app.agents.catalogs import TECHNOLOGY_CATALOG
from app.core.logging import get_logger

logger = get_logger(__name__)


class TechnologyDetectionAgent:
    name = "technology_detection"

    async def run(self, state: AgentState) -> AgentState:
        text = (state.get("crawl") or {}).get("combined_text") or ""
        lowered = text.lower()
        detections: list[dict[str, Any]] = []

        for name, category, aliases in TECHNOLOGY_CATALOG:
            matched_alias = None
            if name.lower() in lowered:
                matched_alias = name
            else:
                for alias in aliases:
                    if alias in lowered:
                        matched_alias = alias
                        break
            if not matched_alias:
                continue

            # Confidence: base 70, +10 for exact canonical, +10 for multiple hits
            confidence = 70.0
            if name.lower() in lowered:
                confidence += 10
            if lowered.count(matched_alias.lower()) > 1:
                confidence += 10
            confidence = min(confidence, 98.0)

            idx = lowered.find(matched_alias.lower())
            evidence = text[max(0, idx - 40) : idx + len(matched_alias) + 40].strip()
            detections.append(
                {
                    "name": name,
                    "category": category,
                    "confidence": confidence,
                    "evidence": evidence,
                    "version_hint": None,
                }
            )

        # Merge ERP hints already found by website intelligence
        wi = state.get("website_intelligence") or {}
        for erp_name in wi.get("erp_detected") or []:
            if not any(d["name"] == erp_name for d in detections):
                detections.append(
                    {
                        "name": erp_name,
                        "category": "erp",
                        "confidence": 65.0,
                        "evidence": "Detected by website intelligence agent",
                        "version_hint": None,
                    }
                )

        logger.info("Detected %s technologies", len(detections))
        return {**state, "technologies": detections}


async def technology_detection_node(state: AgentState) -> AgentState:
    return await TechnologyDetectionAgent().run(state)
