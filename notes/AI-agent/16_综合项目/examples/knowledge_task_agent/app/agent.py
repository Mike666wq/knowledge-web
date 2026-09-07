from __future__ import annotations

from .domain import RunMetrics, RunRequest, RunResult
from .retrieval import EvidenceGenerator, PermissionAwareRetriever
from .runtime import EventRecorder, RequestBudget
from .tools import ToolDenied, ToolExecutor


class KnowledgeTaskAgent:
    def __init__(
        self,
        retriever: PermissionAwareRetriever,
        generator: EvidenceGenerator,
        tools: ToolExecutor,
        *,
        top_k: int = 3,
        max_steps: int = 5,
        max_tool_calls: int = 2,
        max_cost: float = 0.05,
    ) -> None:
        self.retriever = retriever
        self.generator = generator
        self.tools = tools
        self.top_k = top_k
        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls
        self.max_cost = max_cost

    def run(self, request: RunRequest, recorder: EventRecorder | None = None) -> RunResult:
        question = request.question.strip()
        if not 1 <= len(question) <= 4000:
            raise ValueError("question length is invalid")
        events = recorder or EventRecorder()
        budget = RequestBudget(
            max_steps=self.max_steps,
            max_tool_calls=self.max_tool_calls,
            max_cost=self.max_cost,
        )

        if question.startswith("计算 "):
            budget.reserve(kind="tool", estimated_cost=0.0)
            events.record("route_selected", route="calculate")
            value = self.tools.calculate(question.removeprefix("计算 ").strip())
            events.record("tool_completed", tool="calculate", status="ok")
            return self._result("completed", f"计算结果：{value}", budget)

        if question.startswith("创建任务：") or question.startswith("创建任务:"):
            budget.reserve(kind="decision", estimated_cost=0.0)
            events.record("route_selected", route="create_task")
            title = question.split(":" if ":" in question else "：", 1)[1].strip()
            try:
                task, fingerprint = self.tools.create_task(
                    user=request.user,
                    title=title,
                    approved_fingerprint=request.approved_fingerprint,
                )
            except ToolDenied as error:
                events.record("tool_denied", tool="create_task", reason=str(error))
                return self._result("denied", "当前身份无权创建任务。", budget)
            if task is None:
                events.record("approval_required", tool="create_task", status="pending")
                return self._result(
                    "approval_required",
                    f"请确认创建任务：{title}",
                    budget,
                    approval_fingerprint=fingerprint,
                )
            budget.reserve(kind="tool", estimated_cost=0.0)
            events.record("tool_completed", tool="create_task", status="ok")
            return self._result("completed", f"任务已创建，编号 {task.task_id}。", budget)

        budget.reserve(kind="retrieval", estimated_cost=0.001)
        events.record("route_selected", route="knowledge")
        chunks = self.retriever.retrieve(question, request.user, self.top_k)
        events.record(
            "retrieval_completed",
            count=len(chunks),
            doc_ids=[chunk.doc_id for chunk in chunks],
        )
        budget.reserve(kind="generation", estimated_cost=0.005)
        answer, citations = self.generator.generate(question, chunks)
        return self._result("answered", answer, budget, citations=citations)

    @staticmethod
    def _result(status, answer, budget, *, citations=(), approval_fingerprint=None):
        return RunResult(
            status=status,
            answer=answer,
            citations=tuple(citations),
            approval_fingerprint=approval_fingerprint,
            metrics=RunMetrics(
                steps=budget.steps,
                tool_calls=budget.tool_calls,
                estimated_cost=round(budget.estimated_cost, 6),
            ),
        )
