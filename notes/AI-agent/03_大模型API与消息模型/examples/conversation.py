"""在客户端内存中维护多轮消息历史。"""

from __future__ import annotations

import os
from typing import Any

from client_factory import ModelConfig, build_client, load_config


class Conversation:
    def __init__(self, client: Any, config: ModelConfig, system_prompt: str) -> None:
        self.client = client
        self.config = config
        self.messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def ask(self, question: str) -> str:
        question = question.strip()
        if not question:
            raise ValueError("问题不能为空")

        pending_messages = [
            *self.messages,
            {"role": "user", "content": question},
        ]
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=pending_messages,
        )
        if not response.choices or not response.choices[0].message.content:
            raise RuntimeError("模型没有返回文本内容")

        answer = response.choices[0].message.content
        self.messages.extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ]
        )
        return answer


def main() -> int:
    config = load_config()
    conversation = Conversation(
        build_client(config),
        config,
        "你是 AI Agent 技术助教。结合对话历史回答。",
    )
    print("输入 exit 结束。")
    max_turns = int(os.getenv("MAX_CONVERSATION_TURNS", "100"))
    if max_turns <= 0:
        raise ValueError("MAX_CONVERSATION_TURNS 必须大于 0")
    for _ in range(max_turns):
        question = input("你：").strip()
        if question.lower() in {"exit", "quit"}:
            return 0
        try:
            print(f"助手：{conversation.ask(question)}")
        except ValueError as exc:
            print(f"输入错误：{exc}")
    print("已达到最大对话轮次，程序自动结束。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
