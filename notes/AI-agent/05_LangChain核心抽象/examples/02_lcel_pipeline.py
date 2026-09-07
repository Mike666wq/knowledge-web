"""使用 LangChain Runnable 构建无网络、可重复运行的工单分析链。"""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)


def validate(raw: dict[str, str]) -> dict[str, str]:
    text = raw.get("text", "").strip()
    if not text:
        raise ValueError("text 不能为空")
    return {"text": text, "customer": raw.get("customer", "anonymous")}


def category(ticket: dict[str, str]) -> str:
    text = ticket["text"]
    if any(word in text for word in ("退款", "扣款", "发票")):
        return "billing"
    if any(word in text for word in ("报错", "失败", "无法")):
        return "technical"
    return "general"


def summary(ticket: dict[str, str]) -> str:
    text = ticket["text"]
    return text if len(text) <= 24 else text[:24] + "…"


def priority(ticket: dict[str, str]) -> str:
    urgent_words = ("紧急", "生产", "全部", "严重")
    return "high" if any(word in ticket["text"] for word in urgent_words) else "normal"


def render(data: dict[str, Any]) -> dict[str, str]:
    original = data["original"]
    return {
        "customer": original["customer"],
        "category": data["category"],
        "priority": data["priority"],
        "summary": data["summary"],
    }


validate_step = RunnableLambda(validate).with_config(run_name="validate_ticket")

analysis = RunnableParallel(
    original=RunnablePassthrough(),
    category=RunnableLambda(category),
    summary=RunnableLambda(summary),
    priority=RunnableLambda(priority),
)

ticket_chain = validate_step | analysis | RunnableLambda(render)


def main() -> None:
    one = ticket_chain.invoke(
        {"customer": "u-100", "text": "生产环境全部用户支付失败，紧急处理"},
        config={"tags": ["tutorial", "ticket"]},
    )
    print(one)

    many = ticket_chain.batch(
        [
            {"customer": "u-101", "text": "申请退款"},
            {"customer": "u-102", "text": "如何修改头像"},
        ],
        config={"max_concurrency": 2},
    )
    for item in many:
        print(item)


if __name__ == "__main__":
    main()
