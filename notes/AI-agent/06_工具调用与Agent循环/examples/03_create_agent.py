"""使用 LangChain 1.x create_agent 构建预置工具循环。"""

from __future__ import annotations

import os
from typing import Any

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()


@tool
def get_order_status(order_id: str) -> dict[str, Any]:
    """按订单号查询模拟订单状态；只读，不会修改订单。"""
    orders = {
        "A100": {"status": "shipped", "carrier": "demo-express"},
        "A200": {"status": "processing", "carrier": None},
    }
    order = orders.get(order_id.upper())
    if order is None:
        return {"ok": False, "error_code": "NOT_FOUND", "order_id": order_id}
    return {"ok": True, "order_id": order_id.upper(), **order}


def build_agent():
    model_name = os.getenv("LLM_MODEL")
    if not model_name:
        raise RuntimeError("请在 .env 中设置 LLM_MODEL")
    model = ChatOpenAI(
        model=model_name,
        api_key=os.getenv("OPENAI_API_KEY", "not-needed"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        temperature=0,
        timeout=30,
        max_retries=2,
    )
    return create_agent(
        model=model,
        tools=[get_order_status],
        system_prompt=(
            "你是订单查询助手。只有用户提供订单号时才查询；"
            "工具返回 NOT_FOUND 时如实说明，不得编造状态。"
        ),
    )


if __name__ == "__main__":
    agent = build_agent()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "订单 A100 到哪了？"}]},
        config={"recursion_limit": 12},
    )
    print(result["messages"][-1].content)
