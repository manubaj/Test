"""Backward-compatible re-exports. Prefer app.agents.contracts / runtime. """

from app.agents.contracts import AgentState
from app.agents.runtime import find_keyword_hits, safe_json_loads

__all__ = ["AgentState", "find_keyword_hits", "safe_json_loads"]
