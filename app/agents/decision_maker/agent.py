"""
Agent 5 — Decision Maker Finder

Extracts CEO, CIO, CTO, VP IT, IT Director, ERP Manager,
Application Manager, Digital Transformation Lead with public profile links.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

from app.agents.catalogs import DECISION_MAKER_PATTERNS
from app.agents.contracts import AgentState, corpus_text
from app.agents.runtime import append_trace, timed_agent
from app.core.logging import get_logger
from app.utils.text import extract_emails

logger = get_logger(__name__)

AGENT_ID = "agent_5_decision_maker_finder"
AGENT_NAME = "Decision Maker Finder Agent"


class DecisionMakerAgent:
    name = AGENT_ID

    async def run(self, state: AgentState) -> AgentState:
        with timed_agent(AGENT_ID, AGENT_NAME) as meta:
            text = corpus_text(state)
            website = state.get("website") or ""
            emails = extract_emails(text)
            people: list[dict[str, Any]] = []

            for role_key, pattern, title_hint in DECISION_MAKER_PATTERNS:
                role_re = re.compile(pattern, re.IGNORECASE)
                for match in role_re.finditer(text):
                    window = text[max(0, match.start() - 100) : match.end() + 100]
                    name = self._guess_name(window, match.group(0))
                    if not name:
                        continue
                    if any(
                        p["full_name"] == name and p["role_category"] == role_key
                        for p in people
                    ):
                        continue
                    people.append(
                        {
                            "full_name": name,
                            "title": title_hint,
                            "title_raw": match.group(0).strip(),
                            "role_category": role_key,
                            "email": self._match_email(name, emails),
                            "profile_url": self._profile_links(website, name),
                            "linkedin_search_url": (
                                "https://www.linkedin.com/search/results/people/"
                                f"?keywords={quote(name + ' ' + title_hint)}"
                            ),
                            "source": website,
                            "confidence": 70 if name else 40,
                        }
                    )

            # Leadership page fallback
            if not people and any(
                k in text.lower()
                for k in ("leadership", "executive team", "management team", "cio", "cto")
            ):
                people.append(
                    {
                        "full_name": "Leadership team (individual names not publicly listed)",
                        "title": "IT / Executive Leadership",
                        "title_raw": "leadership",
                        "role_category": "other",
                        "email": emails[0] if emails else None,
                        "profile_url": website.rstrip("/") + "/about" if website else None,
                        "linkedin_search_url": None,
                        "source": website,
                        "confidence": 35,
                    }
                )

            payload = {
                "agent": AGENT_NAME,
                "count": len(people),
                "decision_makers": people[:20],
                "emails_found": emails[:10],
                "roles_covered": sorted({p["role_category"] for p in people}),
            }
            meta["notes"].append(f"Found {len(people)} contacts")
            state = {
                **state,
                "decision_makers": people[:20],
                "decision_maker_finder": payload,
            }
            return append_trace(state, meta)

    def _guess_name(self, window: str, role_match: str) -> str | None:
        candidates = re.findall(
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", window
        )
        stop = {
            "Chief",
            "Information",
            "Officer",
            "Director",
            "Vice",
            "President",
            "Digital",
            "Transformation",
            "Application",
            "Manager",
            "Technology",
            "Executive",
            "Team",
            "About",
            "Our",
        }
        role_tokens = {t.capitalize() for t in re.findall(r"[A-Za-z]+", role_match)}
        for candidate in candidates:
            parts = candidate.split()
            if any(part in stop or part in role_tokens for part in parts):
                continue
            return candidate
        return None

    def _match_email(self, name: str, emails: list[str]) -> str | None:
        parts = [p.lower() for p in name.split() if p]
        for email in emails:
            local = email.split("@", 1)[0].lower()
            if len(parts) >= 2 and parts[0][:3] in local and parts[-1][:3] in local:
                return email
        return None

    def _profile_links(self, website: str, name: str) -> str | None:
        if not website:
            return None
        slug = "-".join(name.lower().split())
        base = website.rstrip("/")
        return f"{base}/about/{slug}"


async def decision_maker_node(state: AgentState) -> AgentState:
    return await DecisionMakerAgent().run(state)
