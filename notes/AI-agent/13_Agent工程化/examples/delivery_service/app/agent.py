from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol

from .retry import RetryPolicy, call_with_retry


class ModelClient(Protocol):
    async def generate(self, question: str) -> str: ...


class MockModelClient:
    async def generate(self, question: str) -> str:
        await asyncio.sleep(0)
        return f"mock answer: {question}"


@dataclass(frozen=True)
class Answer:
    text: str
    model: str


class AgentService:
    def __init__(
        self,
        client: ModelClient,
        *,
        model: str,
        request_timeout: float,
        max_concurrency: int,
        retry_policy: RetryPolicy,
    ) -> None:
        self._client = client
        self._model = model
        self._request_timeout = request_timeout
        self._slots = asyncio.Semaphore(max_concurrency)
        self._retry_policy = retry_policy

    async def answer(self, question: str) -> Answer:
        normalized = question.strip()
        if not normalized:
            raise ValueError("question must not be empty")

        async def invoke() -> str:
            async with self._slots:
                return await self._client.generate(normalized)

        async with asyncio.timeout(self._request_timeout):
            text = await call_with_retry(invoke, self._retry_policy)
        return Answer(text=text, model=self._model)
