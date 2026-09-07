from __future__ import annotations

import asyncio
from dataclasses import dataclass
import random
from typing import Awaitable, Callable, TypeVar


T = TypeVar("T")


class TransientUpstreamError(RuntimeError):
    """The operation may succeed later and is safe to retry."""


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 2
    base_delay: float = 0.05
    max_delay: float = 1.0
    jitter_ratio: float = 0.1

    def delay_for(self, retry_index: int) -> float:
        base = min(self.max_delay, self.base_delay * (2**retry_index))
        jitter = base * self.jitter_ratio * random.random()
        return base + jitter


async def call_with_retry(
    operation: Callable[[], Awaitable[T]],
    policy: RetryPolicy,
    *,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Retry only an explicitly transient and idempotent operation."""
    for attempt in range(policy.max_retries + 1):
        try:
            return await operation()
        except TransientUpstreamError:
            if attempt >= policy.max_retries:
                raise
            await sleep(policy.delay_for(attempt))
    raise AssertionError("unreachable")
