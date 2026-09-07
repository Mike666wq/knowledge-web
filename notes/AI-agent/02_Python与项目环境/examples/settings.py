"""集中读取并校验大模型示例所需配置。"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


class ConfigurationError(ValueError):
    """环境变量缺失或格式不正确。"""


def _required(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ConfigurationError(f"缺少必需环境变量：{name}")
    return value


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str | None = None
    timeout: float = 60.0

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        api_key = _required(source, "OPENAI_API_KEY")
        model = _required(source, "LLM_MODEL")
        base_url = source.get("OPENAI_BASE_URL", "").strip() or None

        raw_timeout = source.get("REQUEST_TIMEOUT", "60").strip()
        try:
            timeout = float(raw_timeout)
        except ValueError as exc:
            raise ConfigurationError("REQUEST_TIMEOUT 必须是数字") from exc
        if not 1 <= timeout <= 600:
            raise ConfigurationError("REQUEST_TIMEOUT 必须在 1～600 秒之间")

        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url,
            timeout=timeout,
        )

    def safe_summary(self) -> dict[str, str | float]:
        """返回适合日志展示的配置，绝不包含完整密钥。"""
        return {
            "model": self.model,
            "base_url": self.base_url or "SDK 默认地址",
            "timeout": self.timeout,
            "api_key": "<已配置>",
        }

