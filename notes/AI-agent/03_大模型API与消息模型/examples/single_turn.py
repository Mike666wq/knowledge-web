"""发送一次非流式聊天请求。"""

from __future__ import annotations

import sys
from typing import Any

from client_factory import ModelConfig, build_client, load_config


SYSTEM_PROMPT = "你是严谨的 AI Agent 技术助教。回答简洁；不确定时明确说明。"


def ask_once(client: Any, config: ModelConfig, question: str) -> str:
    question = question.strip()
    if not question:
        raise ValueError("问题不能为空")

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    if not response.choices:
        raise RuntimeError("模型响应中没有 choices")
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("模型响应中没有文本内容")
    return content


def main() -> int:
    question = " ".join(sys.argv[1:]).strip() or "用一句话解释 Agent。"
    config = load_config()
    print(ask_once(build_client(config), config, question))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

