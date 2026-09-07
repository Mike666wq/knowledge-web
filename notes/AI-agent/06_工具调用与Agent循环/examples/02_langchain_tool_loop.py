"""LangChain 手动工具循环；需要配置 OpenAI 兼容模型。"""

from __future__ import annotations

import ast
import json
import operator
import os
from typing import Any

from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI


try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    # 仍可使用系统环境变量；项目 requirements.txt 已列出 python-dotenv。
    pass
else:
    load_dotenv()

ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def evaluate_expression(expression: str) -> float:
    def walk(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
            return ALLOWED_OPS[type(node.op)](walk(node.left), walk(node.right))
        raise ValueError("只允许数字和 + - * /")

    return walk(ast.parse(expression, mode="eval"))


@tool
def get_weather(city: str) -> dict[str, Any]:
    """查询指定城市的模拟天气；只读，不访问真实天气服务。"""
    temperatures = {"北京": 26.5, "上海": 28.0, "深圳": 30.0}
    if city not in temperatures:
        raise ValueError(f"没有 {city} 的模拟天气")
    return {"city": city, "temperature_c": temperatures[city]}


@tool
def calculate(expression: str) -> dict[str, float]:
    """计算只含数字和 + - * / 的算术表达式。"""
    return {"value": evaluate_expression(expression)}


TOOLS = [get_weather, calculate]
TOOLS_BY_NAME = {item.name: item for item in TOOLS}


def build_model() -> ChatOpenAI:
    model_name = os.getenv("LLM_MODEL")
    if not model_name:
        raise RuntimeError("请在 .env 中设置 LLM_MODEL")
    return ChatOpenAI(
        model=model_name,
        api_key=os.getenv("OPENAI_API_KEY", "not-needed"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        temperature=0,
        timeout=30,
        max_retries=2,
    )


def safe_tool_result(call: dict[str, Any]) -> dict[str, Any]:
    tool_name = call.get("name", "")
    selected = TOOLS_BY_NAME.get(tool_name)
    if selected is None:
        return {
            "ok": False,
            "error_code": "UNKNOWN_TOOL",
            "message": f"工具 {tool_name!r} 不在白名单中",
        }
    try:
        return {"ok": True, "data": selected.invoke(call.get("args", {}))}
    except (TypeError, ValueError) as exc:
        return {
            "ok": False,
            "error_code": "INVALID_ARGUMENTS",
            "message": str(exc),
        }
    except Exception:
        return {
            "ok": False,
            "error_code": "TOOL_FAILURE",
            "message": "工具暂时不可用",
        }


def run(question: str, *, max_steps: int = 8) -> str:
    model_with_tools = build_model().bind_tools(TOOLS)
    messages = [
        SystemMessage(
            content=(
                "你是数据助手。需要模拟天气或算术时使用工具；"
                "工具失败时不要伪造结果。"
            )
        ),
        HumanMessage(content=question),
    ]
    seen_calls: set[str] = set()

    for _step in range(max_steps):
        response: AIMessage = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            content = str(response.content).strip()
            if not content:
                raise RuntimeError("模型结束循环但没有返回答案")
            return content

        for call in response.tool_calls:
            signature = f"{call['name']}:{json.dumps(call.get('args', {}), sort_keys=True, ensure_ascii=False)}"
            if signature in seen_calls:
                raise RuntimeError(f"检测到重复调用：{signature}")
            seen_calls.add(signature)

            result = safe_tool_result(call)
            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=call["id"],
                    name=call["name"],
                )
            )

    raise RuntimeError(f"达到最大步骤数 {max_steps}，任务仍未完成")


if __name__ == "__main__":
    print(run("查询北京的模拟气温，再加 3，并说明计算过程。"))
