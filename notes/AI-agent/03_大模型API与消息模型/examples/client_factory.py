"""为 OpenAI 兼容服务创建客户端，并集中校验配置。"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from dotenv import load_dotenv
from openai import OpenAI


class ClientConstructor(Protocol):
    def __call__(self, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class ModelConfig:
    api_key: str
    model: str
    base_url: str | None
    timeout: float

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ModelConfig":
        source = os.environ if env is None else env
        api_key = source.get("OPENAI_API_KEY", "").strip()
        model = source.get("LLM_MODEL", "").strip()
        if not api_key:
            raise ValueError("缺少 OPENAI_API_KEY")
        if not model:
            raise ValueError("缺少 LLM_MODEL")

        try:
            timeout = float(source.get("REQUEST_TIMEOUT", "60"))
        except ValueError as exc:
            raise ValueError("REQUEST_TIMEOUT 必须是数字") from exc
        if not 1 <= timeout <= 600:
            raise ValueError("REQUEST_TIMEOUT 必须在 1～600 秒之间")

        return cls(
            api_key=api_key,
            model=model,
            base_url=source.get("OPENAI_BASE_URL", "").strip() or None,
            timeout=timeout,
        )


def build_client(
    config: ModelConfig,
    client_cls: ClientConstructor = OpenAI,
) -> Any:
    kwargs: dict[str, Any] = {
        "api_key": config.api_key,
        "timeout": config.timeout,
        "max_retries": 2,
    }
    if config.base_url:
        kwargs["base_url"] = config.base_url
    return client_cls(**kwargs)


def load_config() -> ModelConfig:
    """程序入口调用一次；库函数和测试直接接收配置对象。"""
    load_dotenv()
    return ModelConfig.from_env()

