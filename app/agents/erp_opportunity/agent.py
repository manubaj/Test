"""
Agent 2 — ERP Opportunity Detection Agent

Detects opportunities using upgrade/migration/modernization/digital
transformation/cloud migration/manufacturing/new plant/expansion/
acquisition/hiring signals. Assigns confidence score.
"""

from __future__ import annotations

from typing import Any

from app.agents.catalogs import OPPORTUNITY_KEYWORDS, OPPORTUNITY_SERVICE_RULES
from app.agents.contracts import AgentState, corpus_text
from app.agents.runtime import append_trace, find_keyword_hits, timed_agent
from app.core.logging import get_logger

logger = get_logger(__name__)

AGENT_ID = "agent_2_erp_opportunity"
AGENT_NAME = "ERP Opportunity Detection Agent"


class ERPOpportunityAgent:
    name = AGENT_ID

    async def run(self, state: AgentState) -> AgentState:
        with timed_agent(AGENT_ID, AGENT_NAME) as meta:
            text = corpus_text(state)
            technologies = state.get("technologies") or []
            erp_techs = [t["name"] for t in technologies if t.get("category") == "erp"]
            if not erp_techs:
                wi = state.get("website_intelligence") or {}
                erp_techs = list(wi.get("erp_detected") or [])

            signals: dict[str, Any] = {}
            for signal, keywords in OPPORTUNITY_KEYWORDS.items():
                hits = find_keyword_hits(text, keywords)
                if hits:
                    signals[signal] = {
                        "matched_keywords": hits,
                        "count": len(hits),
                        "weight": min(1.0, 0.35 + 0.15 * len(hits)),
                    }

            opportunities = self._map_services(erp_techs, signals)
            confidence = self._confidence(erp_techs, signals)

            payload = {
                "agent": AGENT_NAME,
                "opportunities": opportunities,
                "primary_opportunity": opportunities[0] if opportunities else None,
                "signals": signals,
                "erp_systems": erp_techs,
                "confidence": confidence,
                "rationale": self._rationale(opportunities, signals, erp_techs),
            }
            meta["notes"].append(
                f"{len(opportunities)} opportunities @ confidence {confidence}"
            )
            state = {**state, "erp_opportunity": payload}
            return append_trace(state, meta)

    def _map_services(
        self, erp_techs: list[str], signals: dict[str, Any]
    ) -> list[str]:
        found: list[str] = []
        erp_blob = " ".join(erp_techs)
        for service, erp_needles, signal_keys in OPPORTUNITY_SERVICE_RULES:
            if erp_needles and not any(n in erp_blob for n in erp_needles):
                continue
            if signal_keys and not any(s in signals for s in signal_keys):
                # Allow IFS Implementation when IFS present even without expansion
                if service == "IFS Implementation" and any("IFS" in e for e in erp_techs):
                    pass
                elif service in {
                    "ERP Digital Transformation",
                    "ERP Performance Optimization",
                }:
                    continue
                else:
                    continue
            if service not in found:
                found.append(service)

        # Ensure at least one actionable label when ERP or strong digital signals exist
        if not found and erp_techs:
            if any("SAP" in e for e in erp_techs):
                found.append("SAP Support")
            elif any("IFS" in e for e in erp_techs):
                found.append("IFS Managed Support")
            elif any("Oracle" in e for e in erp_techs):
                found.append("Oracle ERP Migration")
            elif any("Infor" in e for e in erp_techs):
                found.append("Infor Upgrade")
            else:
                found.append("ERP Digital Transformation")
        if not found and (
            "digital_transformation" in signals or "modernization" in signals
        ):
            found.append("ERP Digital Transformation")
        if not found:
            found.append("ERP Digital Transformation")
        return found

    def _confidence(self, erp_techs: list[str], signals: dict[str, Any]) -> float:
        score = 12.0
        if erp_techs:
            score += 38.0
            score += min(10.0, len(erp_techs) * 4)
        score += min(35.0, len(signals) * 6.0)
        if "manufacturing" in signals or "new_plant" in signals:
            score += 8.0
        if "cloud_migration" in signals or "migration" in signals:
            score += 7.0
        return round(min(score, 96.0), 2)

    def _rationale(
        self,
        opportunities: list[str],
        signals: dict[str, Any],
        erp_techs: list[str],
    ) -> str:
        parts = []
        if erp_techs:
            parts.append(f"ERP stack: {', '.join(erp_techs)}")
        if signals:
            parts.append("Signals: " + ", ".join(sorted(signals.keys())))
        parts.append("Recommended: " + ", ".join(opportunities))
        return ". ".join(parts)


async def erp_opportunity_node(state: AgentState) -> AgentState:
    return await ERPOpportunityAgent().run(state)
