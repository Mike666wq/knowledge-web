from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import hashlib
import json
from typing import Any


class Risk(IntEnum):
    READ_ONLY = 1
    REVERSIBLE_WRITE = 2
    EXTERNAL_OR_DESTRUCTIVE = 3
    FORBIDDEN = 4


@dataclass(frozen=True)
class ToolRule:
    risk: Risk
    allowed_roles: frozenset[str]


@dataclass(frozen=True)
class ToolRequest:
    name: str
    arguments: dict[str, Any]

    @property
    def fingerprint(self) -> str:
        canonical = json.dumps(
            {"name": self.name, "arguments": self.arguments},
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass(frozen=True)
class Approval:
    user_id: str
    request_fingerprint: str


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    needs_approval: bool = False


class ToolPolicy:
    def __init__(self, rules: dict[str, ToolRule]) -> None:
        self._rules = rules

    def decide(
        self,
        *,
        user_id: str,
        roles: set[str],
        request: ToolRequest,
        approval: Approval | None = None,
    ) -> Decision:
        rule = self._rules.get(request.name)
        if rule is None:
            return Decision(False, "tool_not_allowlisted")
        if rule.risk is Risk.FORBIDDEN:
            return Decision(False, "tool_permanently_forbidden")
        if not roles.intersection(rule.allowed_roles):
            return Decision(False, "role_not_authorized")
        if rule.risk >= Risk.REVERSIBLE_WRITE:
            valid = (
                approval is not None
                and approval.user_id == user_id
                and approval.request_fingerprint == request.fingerprint
            )
            if not valid:
                return Decision(False, "parameter_bound_approval_required", needs_approval=True)
        return Decision(True, "allowed")
