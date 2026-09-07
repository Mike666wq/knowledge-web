from __future__ import annotations

from dataclasses import dataclass
import os


def _positive_float(name: str, default: str, maximum: float) -> float:
    value = float(os.getenv(name, default))
    if not 0 < value <= maximum:
        raise ValueError(f"{name} must be in (0, {maximum}]")
    return value


def _positive_int(name: str, default: str, maximum: int) -> int:
    value = int(os.getenv(name, default))
    if not 0 < value <= maximum:
        raise ValueError(f"{name} must be in [1, {maximum}]")
    return value


@dataclass(frozen=True)
class Settings:
    app_env: str
    model: str
    request_timeout: float
    max_concurrency: int
    max_retries: int
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        model = os.getenv("LLM_MODEL", "mock-model").strip()
        if not model:
            raise ValueError("LLM_MODEL must not be empty")
        retries = int(os.getenv("MAX_RETRIES", "2"))
        if not 0 <= retries <= 8:
            raise ValueError("MAX_RETRIES must be in [0, 8]")
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            model=model,
            request_timeout=_positive_float("REQUEST_TIMEOUT", "10", 300),
            max_concurrency=_positive_int("MAX_CONCURRENCY", "8", 1000),
            max_retries=retries,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
