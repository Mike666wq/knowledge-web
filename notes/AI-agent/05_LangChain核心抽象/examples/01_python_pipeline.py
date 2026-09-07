"""不依赖第三方库的可组合数据流水线。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterable, TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class PipelineError(RuntimeError):
    """保留失败步骤和原始异常的流水线错误。"""

    def __init__(self, step: str, cause: Exception) -> None:
        super().__init__(f"步骤 {step!r} 执行失败：{cause}")
        self.step = step
        self.cause = cause


@dataclass(frozen=True)
class Step(Generic[InputT, OutputT]):
    name: str
    function: Callable[[InputT], OutputT]

    def invoke(self, value: InputT) -> OutputT:
        try:
            return self.function(value)
        except Exception as exc:
            raise PipelineError(self.name, exc) from exc


class Pipeline:
    """按顺序执行步骤；每一步的输出成为下一步的输入。"""

    def __init__(self, *steps: Step[Any, Any]) -> None:
        if not steps:
            raise ValueError("流水线至少需要一个步骤")
        self.steps = steps

    def invoke(self, value: Any) -> Any:
        current = value
        for step in self.steps:
            current = step.invoke(current)
        return current

    def batch(
        self, inputs: Iterable[Any], *, return_exceptions: bool = False
    ) -> list[Any]:
        results: list[Any] = []
        for item in inputs:
            try:
                results.append(self.invoke(item))
            except PipelineError as exc:
                if not return_exceptions:
                    raise
                results.append(exc)
        return results


def validate_ticket(raw: dict[str, str]) -> dict[str, str]:
    text = raw.get("text", "").strip()
    if not text:
        raise ValueError("text 不能为空")
    return {"text": text, "customer": raw.get("customer", "anonymous")}


def classify_ticket(ticket: dict[str, str]) -> dict[str, str]:
    text = ticket["text"]
    if any(word in text for word in ("退款", "扣款", "发票")):
        category = "billing"
    elif any(word in text for word in ("报错", "失败", "无法")):
        category = "technical"
    else:
        category = "general"
    return {**ticket, "category": category}


def build_report(ticket: dict[str, str]) -> str:
    return (
        f"客户={ticket['customer']} | 分类={ticket['category']} | "
        f"内容={ticket['text'][:40]}"
    )


def main() -> None:
    pipeline = Pipeline(
        Step("validate", validate_ticket),
        Step("classify", classify_ticket),
        Step("render", build_report),
    )

    print(pipeline.invoke({"customer": "u-001", "text": "支付后重复扣款"}))

    results = pipeline.batch(
        [
            {"customer": "u-002", "text": "客户端启动报错"},
            {"customer": "u-003", "text": "  "},
        ],
        return_exceptions=True,
    )
    for result in results:
        print(type(result).__name__, result)


if __name__ == "__main__":
    main()
