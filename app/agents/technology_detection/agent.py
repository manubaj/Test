"""
Agent 3 — Technology Detection Agent

Detects: IFS, IFS Apps, IFS Cloud, SAP ECC, SAP S4, Infor LN, Infor M3,
Oracle ERP, Microsoft Dynamics, Salesforce, Azure, AWS, GCP,
SQL Server, Oracle Database, PostgreSQL, Kubernetes, Docker.
"""

from __future__ import annotations

from typing import Any

from app.agents.catalogs import TECHNOLOGY_CATALOG
from app.agents.contracts import AgentState, corpus_text
from app.agents.runtime import append_trace, evidence_snippet, timed_agent
from app.core.logging import get_logger

logger = get_logger(__name__)

AGENT_ID = "agent_3_technology_detection"
AGENT_NAME = "Technology Detection Agent"


class TechnologyDetectionAgent:
    name = AGENT_ID

    async def run(self, state: AgentState) -> AgentState:
        with timed_agent(AGENT_ID, AGENT_NAME) as meta:
            text = corpus_text(state)
            lowered = text.lower()
            detections: list[dict[str, Any]] = []

            for name, category, aliases in TECHNOLOGY_CATALOG:
                matched = None
                if name.lower() in lowered:
                    matched = name.lower()
                else:
                    for alias in aliases:
                        if alias in lowered:
                            matched = alias
                            break
                if not matched:
                    continue

                hits = lowered.count(matched)
                confidence = 68.0
                if name.lower() in lowered:
                    confidence += 12
                if hits > 1:
                    confidence += min(15.0, hits * 3)
                # Stronger confidence for ERP category (sales focus)
                if category == "erp":
                    confidence += 5
                confidence = min(round(confidence, 2), 99.0)

                detections.append(
                    {
                        "name": name,
                        "category": category,
                        "confidence": confidence,
                        "evidence": evidence_snippet(text, matched),
                        "version_hint": self._version_hint(text, name),
                        "hit_count": hits,
                    }
                )

            # Merge ERP from Agent 1 if missing
            wi = state.get("website_intelligence") or {}
            for erp_name in wi.get("erp_detected") or []:
                if not any(d["name"] == erp_name for d in detections):
                    detections.append(
                        {
                            "name": erp_name,
                            "category": "erp",
                            "confidence": 62.0,
                            "evidence": "Propagated from Website Intelligence Agent",
                            "version_hint": None,
                            "hit_count": 1,
                        }
                    )

            detections.sort(key=lambda d: (-float(d["confidence"]), d["name"]))

            summary = {
                "agent": AGENT_NAME,
                "total_detected": len(detections),
                "by_category": self._by_category(detections),
                "erp_stack": [d["name"] for d in detections if d["category"] == "erp"],
                "cloud_stack": [d["name"] for d in detections if d["category"] == "cloud"],
                "database_stack": [
                    d["name"] for d in detections if d["category"] == "database"
                ],
                "devops_stack": [
                    d["name"] for d in detections if d["category"] == "devops"
                ],
                "technologies": detections,
            }
            meta["notes"].append(f"Detected {len(detections)} technologies")
            state = {
                **state,
                "technologies": detections,
                "technology_detection": summary,
            }
            return append_trace(state, meta)

    def _by_category(self, detections: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for d in detections:
            counts[d["category"]] = counts.get(d["category"], 0) + 1
        return counts

    def _version_hint(self, text: str, name: str) -> str | None:
        import re

        patterns = {
            "IFS Apps": r"IFS Apps?\s*([0-9]{1,2})",
            "SAP ECC": r"ECC\s*([0-9](?:\.[0-9])?)",
            "SAP S/4HANA": r"S/?4HANA(?:\s*([0-9]{4}))?",
        }
        pat = patterns.get(name)
        if not pat:
            return None
        m = re.search(pat, text, flags=re.IGNORECASE)
        return m.group(0) if m else None


async def technology_detection_node(state: AgentState) -> AgentState:
    return await TechnologyDetectionAgent().run(state)
