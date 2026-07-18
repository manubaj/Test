"""
Agent 2 — ERP Opportunity Detection Agent.

Scores opportunity signals (upgrade, migration, expansion, hiring, etc.).
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentState, find_keyword_hits
from app.agents.catalogs import OPPORTUNITY_KEYWORDS
from app.core.logging import get_logger

logger = get_logger(__name__)


class ERPOpportunityAgent:
    name = "erp_opportunity"

    async def run(self, state: AgentState) -> AgentState:
        text = (state.get("crawl") or {}).get("combined_text") or ""
        technologies = state.get("technologies") or []
        erp_techs = [t["name"] for t in technologies if t.get("category") == "erp"]

        signals: dict[str, Any] = {}
        for signal, keywords in OPPORTUNITY_KEYWORDS.items():
            hits = find_keyword_hits(text, keywords)
            if hits:
                signals[signal] = {"matched": hits, "count": len(hits)}

        # Map signals to recommended opportunity labels
        opportunities: list[str] = []
        if any("IFS" in e for e in erp_techs):
            if "upgrade" in signals or "modernization" in signals:
                opportunities.append("IFS Upgrade")
            if "cloud_migration" in signals or "migration" in signals:
                opportunities.append("IFS Cloud Migration")
            if "hiring" in signals:
                opportunities.append("IFS Managed Support")
            if not opportunities:
                opportunities.append("IFS Implementation")
        if any("SAP" in e for e in erp_techs):
            if "migration" in signals or "cloud_migration" in signals:
                opportunities.append("SAP S/4HANA Migration")
            else:
                opportunities.append("SAP Support")
        if any("Infor" in e for e in erp_techs) and (
            "upgrade" in signals or "modernization" in signals
        ):
            opportunities.append("Infor Upgrade")
        if any("Oracle" in e for e in erp_techs) and (
            "migration" in signals or "cloud_migration" in signals
        ):
            opportunities.append("Oracle ERP Migration")
        if "digital_transformation" in signals:
            opportunities.append("ERP Digital Transformation")
        if "modernization" in signals or "expansion" in signals:
            opportunities.append("ERP Performance Optimization")

        # Confidence based on ERP presence + signal density
        confidence = 15.0
        if erp_techs:
            confidence += 35.0
        confidence += min(40.0, len(signals) * 8.0)
        if "manufacturing" in signals or "new_plant" in signals:
            confidence += 10.0
        confidence = min(confidence, 95.0)

        payload = {
            "opportunities": sorted(set(opportunities))
            or ["ERP Digital Transformation"],
            "signals": signals,
            "erp_systems": erp_techs,
            "confidence": round(confidence, 2),
        }
        return {**state, "erp_opportunity": payload}


async def erp_opportunity_node(state: AgentState) -> AgentState:
    return await ERPOpportunityAgent().run(state)
