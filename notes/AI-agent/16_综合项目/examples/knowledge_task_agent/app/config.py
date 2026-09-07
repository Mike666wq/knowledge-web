from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    knowledge_path: Path
    rag_top_k: int = 3
    request_timeout: float = 10.0
    max_steps: int = 5
    max_tool_calls: int = 2
    max_request_cost: float = 0.05

    @classmethod
    def from_env(cls, root: Path | None = None) -> "Settings":
        base = root or Path.cwd()
        path = Path(os.getenv("KNOWLEDGE_PATH", "data/knowledge.json"))
        if not path.is_absolute():
            path = base / path
        top_k = int(os.getenv("RAG_TOP_K", "3"))
        timeout = float(os.getenv("REQUEST_TIMEOUT", "10"))
        steps = int(os.getenv("MAX_STEPS", "5"))
        tools = int(os.getenv("MAX_TOOL_CALLS", "2"))
        cost = float(os.getenv("MAX_REQUEST_COST", "0.05"))
        if not path.is_file():
            raise ValueError(f"knowledge file not found: {path}")
        if not 1 <= top_k <= 20 or not 1 <= steps <= 50 or not 0 <= tools <= 20:
            raise ValueError("RAG_TOP_K, MAX_STEPS or MAX_TOOL_CALLS is out of range")
        if not 0 < timeout <= 300:
            raise ValueError("REQUEST_TIMEOUT is out of range")
        if not 0 < cost <= 100:
            raise ValueError("MAX_REQUEST_COST is out of range")
        return cls(path, top_k, timeout, steps, tools, cost)
