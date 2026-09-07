from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any


class BudgetExceeded(RuntimeError):
    pass


class RequestBudget:
    def __init__(self, *, max_steps: int, max_tool_calls: int, max_cost: float) -> None:
        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls
        self.max_cost = max_cost
        self.steps = 0
        self.tool_calls = 0
        self.estimated_cost = 0.0

    def reserve(self, *, kind: str, estimated_cost: float = 0.0) -> None:
        next_steps = self.steps + 1
        next_tools = self.tool_calls + int(kind == "tool")
        next_cost = self.estimated_cost + estimated_cost
        if next_steps > self.max_steps:
            raise BudgetExceeded("max_steps_exceeded")
        if next_tools > self.max_tool_calls:
            raise BudgetExceeded("max_tool_calls_exceeded")
        if next_cost > self.max_cost:
            raise BudgetExceeded("max_cost_exceeded")
        self.steps, self.tool_calls, self.estimated_cost = next_steps, next_tools, next_cost


@dataclass(frozen=True)
class Event:
    name: str
    elapsed_ms: float
    attributes: dict[str, Any]


class EventRecorder:
    SAFE_KEYS = {"route", "status", "doc_ids", "tool", "count", "reason"}

    def __init__(self) -> None:
        self._started = time.perf_counter()
        self.events: list[Event] = []

    def record(self, name: str, **attributes: Any) -> None:
        unsafe = set(attributes) - self.SAFE_KEYS
        if unsafe:
            raise ValueError(f"unsafe event attributes: {sorted(unsafe)}")
        self.events.append(
            Event(name, round((time.perf_counter() - self._started) * 1000, 3), attributes)
        )
