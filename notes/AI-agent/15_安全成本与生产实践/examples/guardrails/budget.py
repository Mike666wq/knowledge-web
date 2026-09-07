from __future__ import annotations

from dataclasses import dataclass


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class Limits:
    max_steps: int
    max_model_calls: int
    max_tool_calls: int
    max_cost: float


class BudgetLedger:
    """Single-process teaching ledger; use atomic shared storage in production."""

    def __init__(self, limits: Limits) -> None:
        self.limits = limits
        self.steps = 0
        self.model_calls = 0
        self.tool_calls = 0
        self.reserved_cost = 0.0
        self.actual_cost = 0.0

    def reserve(self, *, kind: str, estimated_cost: float) -> None:
        if estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")
        next_steps = self.steps + 1
        next_models = self.model_calls + int(kind == "model")
        next_tools = self.tool_calls + int(kind == "tool")
        next_reserved = self.reserved_cost + estimated_cost
        if next_steps > self.limits.max_steps:
            raise BudgetExceeded("step_budget_exceeded")
        if next_models > self.limits.max_model_calls:
            raise BudgetExceeded("model_call_budget_exceeded")
        if next_tools > self.limits.max_tool_calls:
            raise BudgetExceeded("tool_call_budget_exceeded")
        if self.actual_cost + next_reserved > self.limits.max_cost:
            raise BudgetExceeded("cost_budget_exceeded")
        self.steps = next_steps
        self.model_calls = next_models
        self.tool_calls = next_tools
        self.reserved_cost = next_reserved

    def settle(self, *, estimated_cost: float, actual_cost: float) -> None:
        if not 0 <= actual_cost:
            raise ValueError("actual_cost must be non-negative")
        self.reserved_cost = max(0.0, self.reserved_cost - estimated_cost)
        self.actual_cost += actual_cost
        if self.actual_cost + self.reserved_cost > self.limits.max_cost:
            raise BudgetExceeded("actual_cost_budget_exceeded")
