from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class UserContext:
    user_id: str
    roles: frozenset[str]


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    chunk_id: str
    title: str
    text: str
    roles: frozenset[str]


@dataclass(frozen=True)
class Citation:
    doc_id: str
    chunk_id: str
    title: str


@dataclass(frozen=True)
class RunRequest:
    question: str
    user: UserContext
    approved_fingerprint: str | None = None


@dataclass(frozen=True)
class RunMetrics:
    steps: int
    tool_calls: int
    estimated_cost: float


@dataclass(frozen=True)
class RunResult:
    status: Literal["answered", "completed", "approval_required", "denied"]
    answer: str
    citations: tuple[Citation, ...] = field(default_factory=tuple)
    approval_fingerprint: str | None = None
    metrics: RunMetrics = field(default_factory=lambda: RunMetrics(0, 0, 0.0))
