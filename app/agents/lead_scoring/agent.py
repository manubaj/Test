"""
Agent 6 — Lead Scoring Agent

Score 0–100 with weighted factors:
ERP Detected=30, Manufacturing=10, Hiring ERP=20,
Cloud Migration=20, Expansion=20. Returns explanation.
"""

from __future__ import annotations

from typing import Any

from app.agents.catalogs import LEAD_SCORE_WEIGHTS
from app.agents.contracts import AgentState
from app.agents.runtime import append_trace, timed_agent
from app.core.logging import get_logger

logger = get_logger(__name__)

AGENT_ID = "agent_6_lead_scoring"
AGENT_NAME = "Lead Scoring Agent"


class LeadScoringAgent:
    name = AGENT_ID
    MODEL_VERSION = "rules-v2"

    async def run(self, state: AgentState) -> AgentState:
        with timed_agent(AGENT_ID, AGENT_NAME) as meta:
            factors: list[dict[str, Any]] = []
            score = 0

            technologies = state.get("technologies") or []
            erp = [t for t in technologies if t.get("category") == "erp"]
            if erp:
                points = LEAD_SCORE_WEIGHTS["ERP Detected"]
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
                points = LEAD_SCORE_WEIGHTS["Manufacturing"]
                score += points
                factors.append(
                    {
                        "name": "Manufacturing",
                        "points": points,
                        "reason": "Manufacturing footprint or keywords detected",
                    }
                )

            hiring = state.get("hiring_analysis") or {}
            if hiring.get("erp_related_hiring") or any(
                k in (hiring.get("categories") or {})
                for k in ("ERP", "SAP", "IFS", "Oracle", "Infor")
            ):
                points = LEAD_SCORE_WEIGHTS["Hiring ERP"]
                score += points
                factors.append(
                    {
                        "name": "Hiring ERP",
                        "points": points,
                        "reason": f"Hiring score {hiring.get('hiring_score', 0)}/100 with ERP-related roles",
                    }
                )

            if "cloud_migration" in signals or "migration" in signals:
                points = LEAD_SCORE_WEIGHTS["Cloud Migration"]
                score += points
                factors.append(
                    {
                        "name": "Cloud Migration",
                        "points": points,
                        "reason": "Migration / cloud modernization language found",
                    }
                )

            if "expansion" in signals or "new_plant" in signals or "acquisition" in signals:
                points = LEAD_SCORE_WEIGHTS["Expansion"]
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

            band = (
                "hot"
                if score >= 70
                else "warm"
                if score >= 40
                else "cold"
            )
            payload = {
                "agent": AGENT_NAME,
                "score": score,
                "band": band,
                "explanation": explanation,
                "factors": factors,
                "max_possible": sum(LEAD_SCORE_WEIGHTS.values()),
                "weights": LEAD_SCORE_WEIGHTS,
                "model_version": self.MODEL_VERSION,
            }
            meta["notes"].append(f"Score {score} ({band})")
            state = {**state, "lead_score": payload}
            return append_trace(state, meta)


async def lead_scoring_node(state: AgentState) -> AgentState:
    return await LeadScoringAgent().run(state)
