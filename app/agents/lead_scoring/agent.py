"""
Agent 6 — Lead Scoring Agent.

Produces a 0–100 score with weighted factor explanations.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)


class LeadScoringAgent:
    """
    Default weights (configurable later via settings table):
    ERP Detected=30, Manufacturing=10, Hiring ERP=20,
    Cloud Migration=20, Expansion=20.
    """

    name = "lead_scoring"
    MODEL_VERSION = "rules-v1"

    async def run(self, state: AgentState) -> AgentState:
        factors: list[dict[str, Any]] = []
        score = 0

        technologies = state.get("technologies") or []
        erp = [t for t in technologies if t.get("category") == "erp"]
        if erp:
            points = 30
            score += points
            factors.append(
                {
                    "name": "ERP Detected",
                    "points": points,
                    "reason": f"Detected: {', '.join(t['name'] for t in erp)}",
                }
            )

        industry = (state.get("website_intelligence") or {}).get("industry") or state.get(
            "industry"
        )
        opportunity = state.get("erp_opportunity") or {}
        signals = opportunity.get("signals") or {}

        if industry == "Manufacturing" or "manufacturing" in signals:
            points = 10
            score += points
            factors.append(
                {
                    "name": "Manufacturing",
                    "points": points,
                    "reason": "Company shows manufacturing footprint",
                }
            )

        hiring = state.get("hiring_analysis") or {}
        hiring_cats = hiring.get("categories") or {}
        if any(k in hiring_cats for k in ("ERP", "SAP", "IFS", "Oracle", "Infor")):
            points = 20
            score += points
            factors.append(
                {
                    "name": "Hiring ERP",
                    "points": points,
                    "reason": "Active ERP-related hiring signals",
                }
            )

        if "cloud_migration" in signals or "migration" in signals:
            points = 20
            score += points
            factors.append(
                {
                    "name": "Cloud Migration",
                    "points": points,
                    "reason": "Migration / cloud modernization language found",
                }
            )

        if "expansion" in signals or "new_plant" in signals or "acquisition" in signals:
            points = 20
            score += points
            factors.append(
                {
                    "name": "Expansion",
                    "points": points,
                    "reason": "Expansion, new plant, or acquisition signals",
                }
            )

        score = min(score, 100)
        explanation = (
            "; ".join(f"{f['name']} (+{f['points']})" for f in factors)
            if factors
            else "Insufficient ERP opportunity signals for a high score."
        )

        payload = {
            "score": score,
            "explanation": explanation,
            "factors": factors,
            "model_version": self.MODEL_VERSION,
        }
        return {**state, "lead_score": payload}


async def lead_scoring_node(state: AgentState) -> AgentState:
    return await LeadScoringAgent().run(state)
