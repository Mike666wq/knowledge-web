from pathlib import Path
import unittest

from app.agent import KnowledgeTaskAgent
from app.domain import RunRequest, UserContext
from app.retrieval import EvidenceGenerator, PermissionAwareRetriever, load_chunks
from app.tools import SafeCalculator, ToolExecutor


ROOT = Path(__file__).resolve().parents[1]


def build_agent() -> KnowledgeTaskAgent:
    chunks = load_chunks(ROOT / "data" / "knowledge.json")
    return KnowledgeTaskAgent(
        PermissionAwareRetriever(chunks), EvidenceGenerator(), ToolExecutor()
    )


class KnowledgeTaskAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = build_agent()
        self.reader = UserContext("reader-1", frozenset({"reader"}))
        self.editor = UserContext("editor-1", frozenset({"editor"}))

    def test_reader_cannot_retrieve_admin_document(self):
        result = self.agent.run(RunRequest("管理员内部凭据轮换流程", self.reader))
        self.assertNotIn("admin-secrets", {c.doc_id for c in result.citations})
        self.assertNotIn("管理员内部手册", result.answer)

    def test_injected_document_is_removed_from_evidence(self):
        result = self.agent.run(RunRequest("提示注入 export secrets", self.reader))
        self.assertNotIn("poisoned-page", {c.doc_id for c in result.citations})
        self.assertNotIn("调用 export_secrets", result.answer)

    def test_calculator_allows_math_but_rejects_calls(self):
        result = self.agent.run(RunRequest("计算 2 * (3 + 4)", self.reader))
        self.assertEqual("计算结果：14", result.answer)
        with self.assertRaises(ValueError):
            SafeCalculator().evaluate("__import__('os').system('whoami')")

    def test_task_requires_editor_and_parameter_bound_approval(self):
        denied = self.agent.run(RunRequest("创建任务：复习评估", self.reader))
        self.assertEqual("denied", denied.status)

        proposed = self.agent.run(RunRequest("创建任务：复习评估", self.editor))
        self.assertEqual("approval_required", proposed.status)
        self.assertIsNotNone(proposed.approval_fingerprint)

        changed = self.agent.run(
            RunRequest("创建任务：复习安全", self.editor, proposed.approval_fingerprint)
        )
        self.assertEqual("approval_required", changed.status)

        completed = self.agent.run(
            RunRequest("创建任务：复习评估", self.editor, proposed.approval_fingerprint)
        )
        self.assertEqual("completed", completed.status)


if __name__ == "__main__":
    unittest.main()
