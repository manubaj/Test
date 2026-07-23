"""Agent runtime helpers: timing, keyword hits, JSON extraction."""

from __future__ import annotations

import json
import re
import time
from contextlib import contextmanager
from typing import Any, Iterator, Optional

from app.agents.contracts import AgentMeta, AgentState


def find_keyword_hits(text: str, keywords: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [kw for kw in keywords if kw.lower() in lowered]


def evidence_snippet(text: str, needle: str, radius: int = 60) -> str:
    lowered = text.lower()
    idx = lowered.find(needle.lower())
    if idx < 0:
        return ""
    start = max(0, idx - radius)
    end = min(len(text), idx + len(needle) + radius)
    return text[start:end].strip().replace("\n", " ")


def safe_json_loads(raw: Optional[str]) -> Optional[dict[str, Any]]:
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


@contextmanager
def timed_agent(agent_id: str, agent_name: str, version: str = "2.0.0") -> Iterator[dict[str, Any]]:
    """Collect duration/status metadata for agent_trace."""
    started = time.perf_counter()
    bag: dict[str, Any] = {
        "agent_id": agent_id,
        "agent_name": agent_name,
        "version": version,
        "status": "completed",
        "notes": [],
    }
    try:
        yield bag
    except Exception as exc:  # noqa: BLE001
        bag["status"] = "failed"
        bag["notes"] = list(bag.get("notes") or []) + [str(exc)]
        raise
    finally:
        bag["duration_ms"] = int((time.perf_counter() - started) * 1000)


def append_trace(state: AgentState, meta: dict[str, Any]) -> AgentState:
    trace = list(state.get("agent_trace") or [])
    payload: AgentMeta = {
        "agent_id": meta["agent_id"],
        "agent_name": meta["agent_name"],
        "version": meta.get("version", "2.0.0"),
        "status": meta.get("status", "completed"),
        "duration_ms": int(meta.get("duration_ms") or 0),
        "notes": list(meta.get("notes") or []),
    }
    trace.append(dict(payload))
    return {**state, "agent_trace": trace}
