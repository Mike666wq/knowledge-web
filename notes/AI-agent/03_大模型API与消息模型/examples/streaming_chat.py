"""逐块读取并打印流式聊天响应。"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Iterator
from typing import Any

from client_factory import ModelConfig, build_client, load_config


def iter_text_chunks(chunks: Iterable[Any]) -> Iterator[str]:
    for chunk in chunks:
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            yield content


def stream_answer(client: Any, config: ModelConfig, question: str) -> Iterator[str]:
    question = question.strip()
    if not question:
        raise ValueError("问题不能为空")
    chunks = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": "你是简洁、严谨的技术助教。"},
            {"role": "user", "content": question},
        ],
        stream=True,
    )
    yield from iter_text_chunks(chunks)


def main() -> int:
    question = " ".join(sys.argv[1:]).strip() or "列出三个 Agent 风险。"
    config = load_config()
    for text in stream_answer(build_client(config), config, question):
        print(text, end="", flush=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

