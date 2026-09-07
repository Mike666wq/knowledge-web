"""纯 Python Agent 循环：模拟模型依次查天气、计算并回答。"""

from __future__ import annotations

import ast
import json
import operator
from dataclasses import dataclass, field
from typing import Any, Callable


class AgentLoopError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass(frozen=True)
class Decision:
    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()


@dataclass(frozen=True)
class Observation:
    tool_call_id: str
    name: str
    result: dict[str, Any]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    function: Callable[..., Any]
    required_args: frozenset[str] = field(default_factory=frozenset)

    def invoke(self, args: dict[str, Any]) -> dict[str, Any]:
        missing = self.required_args - args.keys()
        if missing:
            return {
                "ok": False,
                "error_code": "INVALID_ARGUMENTS",
                "message": f"缺少参数：{sorted(missing)}",
            }
        try:
            return {"ok": True, "data": self.function(**args)}
        except (TypeError, ValueError) as exc:
            return {
                "ok": False,
                "error_code": "INVALID_ARGUMENTS",
                "message": str(exc),
            }
        except Exception:
            # 生产环境在服务端日志记录堆栈，不把内部细节返回模型。
            return {
                "ok": False,
                "error_code": "TOOL_FAILURE",
                "message": "工具暂时不可用",
            }


ALLOWED_BINARY_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_calculate(expression: str) -> float:
    """只计算数字和 + - * /，避免对模型输出使用 eval。"""

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BINARY_OPS:
            return ALLOWED_BINARY_OPS[type(node.op)](
                evaluate(node.left), evaluate(node.right)
            )
        raise ValueError("表达式只允许数字和 + - * /")

    parsed = ast.parse(expression, mode="eval")
    return evaluate(parsed)


def get_weather(city: str) -> dict[str, Any]:
    data = {"北京": 26.5, "上海": 28.0}
    if city not in data:
        raise ValueError(f"没有城市 {city!r} 的模拟数据")
    return {"city": city, "temperature_c": data[city]}


TOOLS = {
    "get_weather": ToolSpec(
        name="get_weather",
        description="查询城市的模拟气温，只读",
        function=get_weather,
        required_args=frozenset({"city"}),
    ),
    "calculate": ToolSpec(
        name="calculate",
        description="计算仅包含数字和 + - * / 的表达式",
        function=safe_calculate,
        required_args=frozenset({"expression"}),
    ),
}


class ScriptedModel:
    """可预测的测试替身；真实模型也应返回同类结构化决策。"""

    def decide(
        self, question: str, observations: list[Observation]
    ) -> Decision:
        if not observations:
            return Decision(
                tool_calls=(
                    ToolCall("call-weather", "get_weather", {"city": "北京"}),
                )
            )

        if len(observations) == 1:
            weather = observations[0].result
            if not weather["ok"]:
                return Decision(content=f"天气查询失败：{weather['message']}")
            temperature = weather["data"]["temperature_c"]
            return Decision(
                tool_calls=(
                    ToolCall(
                        "call-calculate",
                        "calculate",
                        {"expression": f"{temperature} + 3"},
                    ),
                )
            )

        calculation = observations[-1].result
        if not calculation["ok"]:
            return Decision(content=f"计算失败：{calculation['message']}")
        return Decision(
            content=f"{question}：结果是 {calculation['data']:.1f} 摄氏度。"
        )


def call_signature(call: ToolCall) -> str:
    return f"{call.name}:{json.dumps(call.args, sort_keys=True, ensure_ascii=False)}"


def run_agent(question: str, *, max_steps: int = 6) -> str:
    model = ScriptedModel()
    observations: list[Observation] = []
    previous_signatures: set[str] = set()

    for _step in range(max_steps):
        decision = model.decide(question, observations)
        if not decision.tool_calls:
            if not decision.content.strip():
                raise AgentLoopError("模型结束循环但没有给出最终答复")
            return decision.content

        for call in decision.tool_calls:
            signature = call_signature(call)
            if signature in previous_signatures:
                raise AgentLoopError(f"检测到重复工具调用：{signature}")
            previous_signatures.add(signature)

            tool = TOOLS.get(call.name)
            if tool is None:
                result = {
                    "ok": False,
                    "error_code": "UNKNOWN_TOOL",
                    "message": f"工具 {call.name!r} 不在白名单中",
                }
            else:
                result = tool.invoke(call.args)
            observations.append(Observation(call.id, call.name, result))

    raise AgentLoopError(f"达到最大步骤数 {max_steps}，任务未完成")


if __name__ == "__main__":
    print(run_agent("把北京当前模拟气温加 3"))
