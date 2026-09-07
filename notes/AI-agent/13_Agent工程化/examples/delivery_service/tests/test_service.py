import asyncio
import unittest

from app.agent import AgentService, MockModelClient
from app.retry import RetryPolicy


class SlowClient:
    async def generate(self, question: str) -> str:
        await asyncio.sleep(0.05)
        return question


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_mock_answer_needs_no_key(self):
        service = AgentService(
            MockModelClient(),
            model="mock-model",
            request_timeout=1,
            max_concurrency=2,
            retry_policy=RetryPolicy(max_retries=0),
        )
        result = await service.answer(" hello ")
        self.assertEqual("mock answer: hello", result.text)

    async def test_request_timeout(self):
        service = AgentService(
            SlowClient(),
            model="slow",
            request_timeout=0.001,
            max_concurrency=1,
            retry_policy=RetryPolicy(max_retries=0),
        )
        with self.assertRaises(TimeoutError):
            await service.answer("hello")


if __name__ == "__main__":
    unittest.main()
