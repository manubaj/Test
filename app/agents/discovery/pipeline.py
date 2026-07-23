"""
Discovery multi-agent pipeline — find companies seeking ERP solutions.

Agent 1 — Demand Discovery (LinkedIn-indexed + web search)
Agent 2 — Company Website Enrichment
Agent 3 — ERP Demand Confirmation
Agent 4 — Hiring Signal Analysis
Agent 5 — Decision Maker & Contact Finder (name, title, location, email, phone)
Agent 6 — Lead Scoring & Ranking (top 100)
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any
from urllib.parse import urlparse

from app.agents.catalogs import DECISION_MAKER_PATTERNS, HIRING_KEYWORDS, INDUSTRY_KEYWORDS
from app.agents.erp_catalog import ERP_OFFERINGS, default_discovery_queries, offerings_by_key
from app.agents.runtime import evidence_snippet, find_keyword_hits, timed_agent
from app.core.logging import get_logger
from app.services.crawler.engine import WebsiteCrawler
from app.services.search.web_search import (
    PublicWebSearch,
    infer_company_name,
    extract_linkedin_company_url,
)
from app.utils.text import extract_emails, normalize_url, normalize_whitespace

logger = get_logger(__name__)

PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,4}\)?[\s\-.]?)?\d{3,4}[\s\-.]?\d{3,4}"
)
LOCATION_RE = re.compile(
    r"\b([A-Z][a-zA-Z]+(?:[\s\-][A-Z][a-zA-Z]+)*),\s*"
    r"([A-Z]{2}|[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?)\b"
)


class DemandDiscoveryAgent:
    """Agent 1 — Search web/LinkedIn-indexed pages for ERP demand signals."""

    name = "agent_1_demand_discovery"

    def __init__(self, *, max_queries: int = 48, results_per_query: int = 8) -> None:
        self.max_queries = max_queries
        self.results_per_query = results_per_query
        self.search = PublicWebSearch()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with timed_agent(self.name, "Demand Discovery Agent") as meta:
            queries = default_discovery_queries(max_per_offering=1)[: self.max_queries]
            all_hits: list[dict[str, Any]] = []
            for offering_key, query in queries:
                batch = await self.search.search(
                    query,
                    offering_key=offering_key,
                    max_results=self.results_per_query,
                )
                all_hits.extend(h.to_dict() for h in batch.hits)

            # Cluster hits into company candidates
            candidates: dict[str, dict[str, Any]] = {}
            catalog = offerings_by_key()
            for hit in all_hits:
                name = infer_company_name(hit.get("title") or "", hit.get("snippet") or "")
                if not name:
                    continue
                key = name.lower().strip()
                bucket = candidates.setdefault(
                    key,
                    {
                        "company_name": name,
                        "matched_offerings": set(),
                        "demand_signals": [],
                        "source_urls": [],
                        "linkedin_url": None,
                        "snippets": [],
                    },
                )
                ok = hit.get("offering_key")
                if ok and ok in catalog:
                    bucket["matched_offerings"].add(catalog[ok].label)
                bucket["demand_signals"].append(
                    {
                        "title": hit.get("title"),
                        "snippet": hit.get("snippet"),
                        "url": hit.get("url"),
                        "source": hit.get("source"),
                        "offering_key": ok,
                    }
                )
                url = hit.get("url") or ""
                if url and url not in bucket["source_urls"]:
                    bucket["source_urls"].append(url)
                li = extract_linkedin_company_url(url)
                if li:
                    bucket["linkedin_url"] = li
                if "linkedin.com" in url.lower() and not bucket["linkedin_url"]:
                    bucket["linkedin_url"] = url.split("?")[0]
                if hit.get("snippet"):
                    bucket["snippets"].append(hit["snippet"])

            companies = []
            for data in candidates.values():
                data["matched_offerings"] = sorted(data["matched_offerings"])
                companies.append(data)

            meta["notes"].append(
                f"queries={len(queries)} hits={len(all_hits)} companies={len(companies)}"
            )
            state["discovery_hits"] = all_hits
            state["candidates"] = companies
            state["query_count"] = len(queries)
            state.setdefault("agent_trace", []).append(
                {
                    "agent_id": meta["agent_id"],
                    "agent_name": meta["agent_name"],
                    "version": meta.get("version", "2.0.0"),
                    "status": meta.get("status", "completed"),
                    "duration_ms": meta.get("duration_ms", 0),
                    "notes": meta.get("notes") or [],
                }
            )
            return state


class CompanyWebsiteEnrichmentAgent:
    """Agent 2 — Visit company website (guessed or from links) for enrichment."""

    name = "agent_2_website_enrichment"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with timed_agent(self.name, "Company Website Enrichment Agent") as meta:
            crawler = WebsiteCrawler()
            enriched = []
            candidates = state.get("candidates") or []
            # Cap crawl volume for a single run
            for candidate in candidates[:160]:
                website = self._guess_website(candidate)
                crawl_text = ""
                industry = None
                location = None
                if website:
                    try:
                        result = await crawler.crawl(website, max_pages=4)
                        crawl_text = result.combined_text
                        candidate["website"] = website
                        candidate["crawl"] = {
                            "success": result.success,
                            "pages": len(result.pages),
                            "careers_urls": result.careers_urls,
                        }
                        industry = self._detect_industry(crawl_text)
                        location = self._detect_location(crawl_text)
                    except Exception as exc:  # noqa: BLE001
                        candidate["website_error"] = str(exc)
                candidate["website"] = website or candidate.get("website")
                candidate["site_text"] = crawl_text[:30000]
                candidate["industry"] = industry
                candidate["location"] = location or candidate.get("location")
                enriched.append(candidate)

            meta["notes"].append(f"enriched={len(enriched)}")
            state["candidates"] = enriched
            state.setdefault("agent_trace", []).append(
                {
                    "agent_id": meta["agent_id"],
                    "agent_name": meta["agent_name"],
                    "version": "2.0.0",
                    "status": meta.get("status", "completed"),
                    "duration_ms": meta.get("duration_ms", 0),
                    "notes": meta.get("notes") or [],
                }
            )
            return state

    def _guess_website(self, candidate: dict[str, Any]) -> str | None:
        for url in candidate.get("source_urls") or []:
            low = url.lower()
            if "linkedin.com" in low or "google." in low or "bing.com" in low:
                continue
            if low.startswith("http"):
                parsed = urlparse(url)
                if parsed.netloc:
                    return f"{parsed.scheme}://{parsed.netloc}"
        # Fallback guess from company name
        name = re.sub(r"[^a-z0-9]+", "", (candidate.get("company_name") or "").lower())
        if len(name) >= 3:
            return f"https://www.{name}.com"
        return None

    def _detect_industry(self, text: str) -> str | None:
        lowered = text.lower()
        best = None
        best_score = 0
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in lowered)
            if score > best_score:
                best, best_score = industry, score
        return best

    def _detect_location(self, text: str) -> str | None:
        m = LOCATION_RE.search(text[:8000] if text else "")
        if m:
            return f"{m.group(1)}, {m.group(2)}"
        for marker in ("headquartered in ", "based in ", "located in "):
            idx = (text or "").lower().find(marker)
            if idx >= 0:
                frag = text[idx + len(marker) : idx + len(marker) + 60]
                return normalize_whitespace(frag.split(".")[0])[:120]
        return None


class ERPDemandConfirmationAgent:
    """Agent 3 — Confirm which ERP offerings the company appears to need."""

    name = "agent_3_erp_demand_confirmation"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with timed_agent(self.name, "ERP Demand Confirmation Agent") as meta:
            catalog = list(ERP_OFFERINGS)
            for candidate in state.get("candidates") or []:
                blob = " ".join(
                    [
                        candidate.get("company_name") or "",
                        " ".join(candidate.get("snippets") or []),
                        candidate.get("site_text") or "",
                        " ".join(
                            s.get("title") or ""
                            for s in (candidate.get("demand_signals") or [])
                        ),
                    ]
                ).lower()
                confirmed = list(candidate.get("matched_offerings") or [])
                for offering in catalog:
                    if any(term.lower() in blob for term in offering.search_terms):
                        if offering.label not in confirmed:
                            confirmed.append(offering.label)
                candidate["matched_offerings"] = confirmed
                candidate["demand_strength"] = min(100, 20 + 15 * len(confirmed))
            meta["notes"].append("confirmed offerings against site+signal text")
            state.setdefault("agent_trace", []).append(
                {
                    "agent_id": meta["agent_id"],
                    "agent_name": meta["agent_name"],
                    "version": "2.0.0",
                    "status": "completed",
                    "duration_ms": meta.get("duration_ms", 0),
                    "notes": meta.get("notes") or [],
                }
            )
            return state


class HiringSignalAgent:
    """Agent 4 — Score ERP-related hiring intensity."""

    name = "agent_4_hiring_signals"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with timed_agent(self.name, "Hiring Signal Analysis Agent") as meta:
            for candidate in state.get("candidates") or []:
                text = " ".join(
                    [
                        " ".join(candidate.get("snippets") or []),
                        candidate.get("site_text") or "",
                    ]
                )
                cats = {
                    cat: find_keyword_hits(text, kws)
                    for cat, kws in HIRING_KEYWORDS.items()
                    if find_keyword_hits(text, kws)
                }
                score = min(100, sum(12 for _ in cats))
                # Job-board / LinkedIn sources boost hiring confidence
                if any(
                    (s.get("source") or "").startswith("linkedin")
                    for s in (candidate.get("demand_signals") or [])
                ):
                    score = min(100, score + 25)
                candidate["hiring"] = {
                    "hiring_score": score,
                    "categories": cats,
                    "erp_related": any(
                        c in cats for c in ("ERP", "SAP", "IFS", "Oracle", "Infor")
                    ),
                }
            state.setdefault("agent_trace", []).append(
                {
                    "agent_id": meta["agent_id"],
                    "agent_name": meta["agent_name"],
                    "version": "2.0.0",
                    "status": "completed",
                    "duration_ms": meta.get("duration_ms", 0),
                    "notes": ["hiring signals scored"],
                }
            )
            return state


class DecisionMakerContactAgent:
    """Agent 5 — Extract decision makers with name, title, location, email, phone."""

    name = "agent_5_decision_maker_contacts"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with timed_agent(self.name, "Decision Maker & Contact Finder Agent") as meta:
            for candidate in state.get("candidates") or []:
                text = candidate.get("site_text") or ""
                emails = extract_emails(text)
                phones = self._extract_phones(text)
                location = candidate.get("location")
                people: list[dict[str, Any]] = []

                for role_key, pattern, title_hint in DECISION_MAKER_PATTERNS:
                    for match in re.finditer(pattern, text, flags=re.I):
                        window = text[max(0, match.start() - 90) : match.end() + 90]
                        name = self._guess_name(window)
                        if not name:
                            continue
                        if any(p["name"] == name and p["role"] == role_key for p in people):
                            continue
                        people.append(
                            {
                                "name": name,
                                "designation": title_hint,
                                "role": role_key,
                                "location": location,
                                "email": self._match_email(name, emails),
                                "phone": phones[0] if phones else None,
                                "linkedin_search": (
                                    "https://www.linkedin.com/search/results/people/"
                                    f"?keywords={name}%20{title_hint}"
                                ),
                                "source": candidate.get("website"),
                            }
                        )

                # Always expose any public switchboard contacts found
                if not people and (emails or phones):
                    people.append(
                        {
                            "name": "General / IT contact",
                            "designation": "Company contact",
                            "role": "other",
                            "location": location,
                            "email": emails[0] if emails else None,
                            "phone": phones[0] if phones else None,
                            "linkedin_search": candidate.get("linkedin_url"),
                            "source": candidate.get("website"),
                        }
                    )

                candidate["decision_makers"] = people[:12]
                candidate["emails_public"] = emails[:8]
                candidate["phones_public"] = phones[:5]

            state.setdefault("agent_trace", []).append(
                {
                    "agent_id": meta["agent_id"],
                    "agent_name": meta["agent_name"],
                    "version": "2.0.0",
                    "status": "completed",
                    "duration_ms": meta.get("duration_ms", 0),
                    "notes": ["contacts extracted from public pages"],
                }
            )
            return state

    def _extract_phones(self, text: str) -> list[str]:
        found = []
        for m in PHONE_RE.findall(text or ""):
            digits = re.sub(r"\D", "", m)
            if 10 <= len(digits) <= 15:
                val = normalize_whitespace(m)
                if val not in found:
                    found.append(val)
            if len(found) >= 5:
                break
        return found

    def _guess_name(self, window: str) -> str | None:
        candidates = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", window)
        stop = {
            "Chief", "Information", "Officer", "Director", "Vice", "President",
            "Digital", "Transformation", "Application", "Manager", "Technology",
        }
        for c in candidates:
            if not any(p in stop for p in c.split()):
                return c
        return None

    def _match_email(self, name: str, emails: list[str]) -> str | None:
        parts = [p.lower() for p in name.split() if p]
        for email in emails:
            local = email.split("@", 1)[0].lower()
            if len(parts) >= 2 and parts[0][:3] in local and parts[-1][:3] in local:
                return email
        return emails[0] if emails else None


class LeadRankingAgent:
    """Agent 6 — Score and keep top N leads (default 100)."""

    name = "agent_6_lead_ranking"

    def __init__(self, *, target_count: int = 100) -> None:
        self.target_count = target_count

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with timed_agent(self.name, "Lead Scoring & Ranking Agent") as meta:
            ranked = []
            for candidate in state.get("candidates") or []:
                score = 0
                factors = []
                offerings = candidate.get("matched_offerings") or []
                if offerings:
                    pts = min(40, 15 + 8 * len(offerings))
                    score += pts
                    factors.append(f"ERP demand offerings (+{pts})")
                hiring = candidate.get("hiring") or {}
                if hiring.get("erp_related"):
                    score += 25
                    factors.append("ERP-related hiring (+25)")
                elif hiring.get("hiring_score", 0) >= 20:
                    score += 10
                    factors.append("General tech hiring (+10)")
                if candidate.get("website"):
                    score += 10
                    factors.append("Website identified (+10)")
                if candidate.get("decision_makers"):
                    score += 15
                    factors.append("Decision makers found (+15)")
                if any(
                    (s.get("source") or "").startswith("linkedin")
                    for s in (candidate.get("demand_signals") or [])
                ):
                    score += 10
                    factors.append("LinkedIn-indexed signal (+10)")
                score = min(100, score)
                if score < 25 and not offerings:
                    continue
                candidate["lead_score"] = score
                candidate["score_explanation"] = "; ".join(factors) or "Weak signals"
                candidate["company_summary"] = (
                    f"{candidate.get('company_name')} appears to need "
                    f"{', '.join(offerings) if offerings else 'ERP services'}. "
                    f"Location: {candidate.get('location') or 'unspecified'}."
                )
                ranked.append(candidate)

            ranked.sort(key=lambda c: c.get("lead_score", 0), reverse=True)
            top = ranked[: self.target_count]
            meta["notes"].append(f"ranked={len(ranked)} kept={len(top)}")
            state["leads"] = top
            state.setdefault("agent_trace", []).append(
                {
                    "agent_id": meta["agent_id"],
                    "agent_name": meta["agent_name"],
                    "version": "2.0.0",
                    "status": "completed",
                    "duration_ms": meta.get("duration_ms", 0),
                    "notes": meta.get("notes") or [],
                }
            )
            return state


class ERPDiscoveryTool:
    """One tool: hardcoded ERPs → ~100 global leads with decision-maker contacts."""

    name = "erp_demand_discovery_tool"
    version = "3.0.0"

    def __init__(self, *, target_lead_count: int = 100) -> None:
        self.target_lead_count = target_lead_count

    def list_agents(self) -> list[dict[str, str]]:
        return [
            {"id": "1", "name": "Demand Discovery Agent",
             "responsibility": "Search LinkedIn-indexed jobs + web for ERP demand"},
            {"id": "2", "name": "Company Website Enrichment Agent",
             "responsibility": "Crawl company sites for industry/location/context"},
            {"id": "3", "name": "ERP Demand Confirmation Agent",
             "responsibility": "Map companies to hardcoded ERP offerings"},
            {"id": "4", "name": "Hiring Signal Analysis Agent",
             "responsibility": "Score ERP/cloud hiring intensity"},
            {"id": "5", "name": "Decision Maker & Contact Finder Agent",
             "responsibility": "Name, designation, location, email, phone (public)"},
            {"id": "6", "name": "Lead Scoring & Ranking Agent",
             "responsibility": f"Score and return top {self.target_lead_count} leads"},
        ]

    async def run(self) -> dict[str, Any]:
        state: dict[str, Any] = {"agent_trace": [], "errors": []}
        state = await DemandDiscoveryAgent().run(state)
        state = await CompanyWebsiteEnrichmentAgent().run(state)
        state = await ERPDemandConfirmationAgent().run(state)
        state = await HiringSignalAgent().run(state)
        state = await DecisionMakerContactAgent().run(state)
        state = await LeadRankingAgent(target_count=self.target_lead_count).run(state)

        leads = state.get("leads") or []
        return {
            "tool": self.name,
            "tool_version": self.version,
            "target_lead_count": self.target_lead_count,
            "leads_found": len(leads),
            "offerings": [o.label for o in ERP_OFFERINGS],
            "query_count": state.get("query_count") or 0,
            "agents": self.list_agents(),
            "agent_trace": state.get("agent_trace") or [],
            "leads": [
                {
                    "company_name": lead.get("company_name"),
                    "website": lead.get("website"),
                    "linkedin_url": lead.get("linkedin_url"),
                    "country": None,
                    "location": lead.get("location"),
                    "industry": lead.get("industry"),
                    "matched_offerings": lead.get("matched_offerings") or [],
                    "demand_signals": (lead.get("demand_signals") or [])[:5],
                    "source_urls": (lead.get("source_urls") or [])[:8],
                    "lead_score": lead.get("lead_score") or 0,
                    "score_explanation": lead.get("score_explanation"),
                    "company_summary": lead.get("company_summary"),
                    "decision_makers": lead.get("decision_makers") or [],
                    "emails_public": lead.get("emails_public") or [],
                    "phones_public": lead.get("phones_public") or [],
                }
                for lead in leads
            ],
            "errors": state.get("errors") or [],
        }
