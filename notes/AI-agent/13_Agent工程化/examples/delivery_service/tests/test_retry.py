import unittest

from app.retry import RetryPolicy, TransientUpstreamError, call_with_retry


class RetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_transient_failure_is_retried(self):
        attempts = 0
        delays: list[float] = []

        async def operation():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise TransientUpstreamError("temporary")
            return "ok"

        async def no_sleep(delay: float):
            delays.append(delay)

        result = await call_with_retry(
            operation,
            RetryPolicy(max_retries=2, jitter_ratio=0),
            sleep=no_sleep,
        )
        self.assertEqual("ok", result)
        self.assertEqual(3, attempts)
        self.assertEqual(2, len(delays))

    async def test_permanent_error_is_not_retried(self):
        attempts = 0

        async def operation():
            nonlocal attempts
            attempts += 1
            raise ValueError("bad request")

        with self.assertRaises(ValueError):
            await call_with_retry(operation, RetryPolicy(max_retries=3))
        self.assertEqual(1, attempts)


if __name__ == "__main__":
    unittest.main()
