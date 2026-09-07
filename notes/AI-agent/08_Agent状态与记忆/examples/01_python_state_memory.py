"""纯 Python：区分 thread 状态与跨 thread 用户记忆。"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ThreadState:
    messages: list[dict[str, str]] = field(default_factory=list)
    step_count: int = 0
    status: str = "running"


class ThreadStateRepository:
    def __init__(self) -> None:
        self._states: dict[str, ThreadState] = {}

    def load(self, thread_id: str) -> ThreadState:
        return deepcopy(self._states.get(thread_id, ThreadState()))

    def save(self, thread_id: str, state: ThreadState) -> None:
        if state.step_count < 0:
            raise ValueError("step_count 不能为负数")
        self._states[thread_id] = deepcopy(state)


class UserMemoryRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], dict[str, Any]] = {}

    def put(self, user_id: str, key: str, value: dict[str, Any]) -> None:
        if not user_id or not key:
            raise ValueError("user_id 和 key 不能为空")
        self._items[(user_id, key)] = deepcopy(value)

    def get(self, user_id: str, key: str) -> dict[str, Any] | None:
        item = self._items.get((user_id, key))
        return deepcopy(item) if item is not None else None


def handle_message(
    *,
    thread_id: str,
    user_id: str,
    text: str,
    threads: ThreadStateRepository,
    memories: UserMemoryRepository,
    max_steps: int = 8,
) -> str:
    state = threads.load(thread_id)
    if state.status != "running":
        raise RuntimeError(f"thread 已终止：{state.status}")
    if state.step_count >= max_steps:
        state.status = "budget_exceeded"
        threads.save(thread_id, state)
        return "本会话已达到步骤上限。"

    state.messages.append({"role": "user", "content": text})
    state.step_count += 1

    if text.startswith("记住语言="):
        language = text.split("=", 1)[1].strip()
        if not language:
            answer = "语言不能为空。"
        else:
            memories.put(
                user_id,
                "language",
                {"value": language, "source": "explicit_user_request"},
            )
            answer = f"已保存长期偏好：{language}。"
    else:
        preference = memories.get(user_id, "language")
        language = preference["value"] if preference else "未设置"
        answer = (
            f"当前 thread 已有 {len(state.messages)} 条用户消息；"
            f"跨 thread 语言偏好为 {language}。"
        )

    state.messages.append({"role": "assistant", "content": answer})
    threads.save(thread_id, state)
    return answer


def main() -> None:
    threads = ThreadStateRepository()
    memories = UserMemoryRepository()

    print(
        handle_message(
            thread_id="thread-a",
            user_id="user-42",
            text="记住语言=中文",
            threads=threads,
            memories=memories,
        )
    )
    print(
        handle_message(
            thread_id="thread-b",
            user_id="user-42",
            text="这是一个新会话",
            threads=threads,
            memories=memories,
        )
    )


if __name__ == "__main__":
    main()
