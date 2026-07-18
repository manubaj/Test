"""
Agent 5 — Decision Maker Finder.

Extracts CEO/CIO/CTO/VP IT/IT Director/ERP Manager/etc. from public pages.
"""

from __future__ import annotations

import re
from typing import Any

from app.agents.base import AgentState
from app.agents.catalogs import DECISION_MAKER_PATTERNS
from app.core.logging import get_logger
from app.utils.text import extract_emails

logger = get_logger(__name__)


class DecisionMakerAgent:
    name = "decision_maker"

    async def run(self, state: AgentState) -> AgentState:
        text = (state.get("crawl") or {}).get("combined_text") or ""
        website = state.get("website") or ""
        emails = extract_emails(text)
        people: list[dict[str, Any]] = []

        # Pattern: "Jane Doe, Chief Information Officer" / "CIO: Jane Doe"
        for role_key, pattern in DECISION_MAKER_PATTERNS:
            role_re = re.compile(pattern, re.IGNORECASE)
            for match in role_re.finditer(text):
                window = text[max(0, match.start() - 80) : match.end() + 80]
                name = self._guess_name(window)
                if not name:
                    continue
                if any(p["full_name"] == name and p["role_category"] == role_key for p in people):
                    continue
                people.append(
                    {
                        "full_name": name,
                        "title": match.group(0).strip().title(),
                        "role_category": role_key,
                        "email": self._match_email(name, emails),
                        "profile_url": self._profile_guess(website, name),
                        "source": website,
                    }
                )

        # Fallback placeholders when no public names found but leadership pages exist
        if not people and any(k in text.lower() for k, _ in DECISION_MAKER_PATTERNS):
            people.append(
                {
                    "full_name": "Leadership team (name not publicly listed)",
                    "title": "IT / Executive Leadership",
                    "role_category": "other",
                    "email": emails[0] if emails else None,
                    "profile_url": website,
                    "source": website,
                }
            )

        return {**state, "decision_makers": people[:15]}

    def _guess_name(self, window: str) -> str | None:
        # Capture 2–3 capitalized tokens near the role mention
        candidates = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", window)
        stop = {"Chief", "Information", "Officer", "Director", "Vice", "President", "Digital"}
        for candidate in candidates:
            if not any(part in stop for part in candidate.split()):
                return candidate
        return candidates[0] if candidates else None

    def _match_email(self, name: str, emails: list[str]) -> str | None:
        parts = [p.lower() for p in name.split() if p]
        for email in emails:
            local = email.split("@", 1)[0].lower()
            if parts and all(p[:3] in local for p in parts[:2]):
                return email
        return None

    def _profile_guess(self, website: str, name: str) -> str | None:
        if not website:
            return None
        slug = "-".join(name.lower().split())
        return f"{website.rstrip('/')}/about/{slug}"


async def decision_maker_node(state: AgentState) -> AgentState:
    return await DecisionMakerAgent().run(state)
