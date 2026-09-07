from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
import operator
from typing import Any

from .domain import UserContext


class ToolDenied(RuntimeError):
    pass


class SafeCalculator:
    _binary = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _unary = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def evaluate(self, expression: str) -> int | float:
        if not 0 < len(expression) <= 100:
            raise ValueError("expression length is invalid")
        tree = ast.parse(expression, mode="eval")
        return self._visit(tree.body, depth=0)

    def _visit(self, node: ast.AST, depth: int) -> int | float:
        if depth > 12:
            raise ValueError("expression is too complex")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in self._unary:
            return self._unary[type(node.op)](self._visit(node.operand, depth + 1))
        if isinstance(node, ast.BinOp) and type(node.op) in self._binary:
            left = self._visit(node.left, depth + 1)
            right = self._visit(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("exponent is too large")
            return self._binary[type(node.op)](left, right)
        raise ValueError(f"unsupported expression node: {type(node).__name__}")


def request_fingerprint(user_id: str, tool: str, arguments: dict[str, Any]) -> str:
    payload = json.dumps(
        {"user_id": user_id, "tool": tool, "arguments": arguments},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class Task:
    task_id: int
    owner_id: str
    title: str


class TaskStore:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def create(self, owner_id: str, title: str) -> Task:
        task = Task(len(self.tasks) + 1, owner_id, title)
        self.tasks.append(task)
        return task


class ToolExecutor:
    def __init__(self, task_store: TaskStore | None = None) -> None:
        self.calculator = SafeCalculator()
        self.task_store = task_store or TaskStore()

    def calculate(self, expression: str) -> int | float:
        return self.calculator.evaluate(expression)

    def create_task(
        self, *, user: UserContext, title: str, approved_fingerprint: str | None
    ) -> tuple[Task | None, str]:
        normalized = title.strip()
        if "editor" not in user.roles:
            raise ToolDenied("editor_role_required")
        if not 1 <= len(normalized) <= 200:
            raise ValueError("task title length is invalid")
        fingerprint = request_fingerprint(user.user_id, "create_task", {"title": normalized})
        if approved_fingerprint != fingerprint:
            return None, fingerprint
        return self.task_store.create(user.user_id, normalized), fingerprint
