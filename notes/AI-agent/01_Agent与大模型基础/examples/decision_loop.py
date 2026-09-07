"""一个不依赖大模型的最小 Agent 循环。

决策器故意使用确定性规则，目的是先观察 Agent 的结构；后续章节再把决策器
替换成聊天模型。该文件不访问网络，也不需要 API Key。

Agent 循环的四个核心步骤：
  1. 看到"当前状态（observations）
  2. 决策器（decide）选择下一步动作（工具调用 / 结束）
  3. 执行器（execute）安全地调用工具并记录结果
  4. 循环回到步骤 1，直到决策器返回 "finish"

整体数据流：
  AgentState(目标 + 观察列表)
    → decide()  → Decision(动作类型 + 参数)
    → execute() → observation(新观察)
    → 追加回 AgentState.observations
    → 循环...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

# ── 核心数据类型 ────────────────────────────────────────────────
# ActionKind：动作类型，只能是 "tool"（调用工具）或 "finish"（任务完成）
ActionKind = Literal["tool", "finish"]


@dataclass(frozen=True) 
class Decision:
    """决策器输出的单次决策，不可变（frozen=True）。

    Attributes:
        kind:      动作类型，"tool" 表示调用工具，"finish" 表示任务结束
        tool_name: 当 kind == "tool" 时，指定要调用的工具名称
        arguments: 传递给工具的参数，如 {"city": "北京"}
        answer:    当 kind == "finish" 时，携带最终回答文本
    """
    kind: ActionKind
    tool_name: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    answer: str | None = None


@dataclass
class AgentState:
    """Agent 的运行时状态，记录目标与执行历史。

    Attributes:
        goal:         用户给定的目标任务描述
        observations: 每一步工具调用的观察结果列表（按执行顺序追加）
    """
    goal: str
    observations: list[dict[str, Any]] = field(default_factory=list)


# ── 自定义异常 ──────────────────────────────────────────────────

class StepLimitExceeded(RuntimeError):
    """Agent 在指定步数内没有结束，触发的安全兜底异常。"""


# ═══════════════════════════════════════════════════════════════
#   工具层（教学模拟，真实场景替换为 API 调用、数据库查询等）
# ═══════════════════════════════════════════════════════════════

def get_temperature(city: str) -> int:
    """[工具函数] 获取指定城市的当前温度（教学用固定数据）。

    在真实项目中，这里可以替换为调用天气 API、读取传感器等。
    当前仅支持"北京"和"上海"两个城市。

    Args:
        city: 城市名称，如 "北京"

    Returns:
        该城市的演示温度（整数）

    Raises:
        ValueError: 当传入不支持的城市时抛出
    """
    temperatures = {"北京": 32, "上海": 28}
    if city not in temperatures:
        raise ValueError(f"没有城市 {city!r} 的演示数据")
    return temperatures[city]


def classify_temperature(value: int) -> str:
    """[工具函数] 根据温度数值给出体感分类（确定性规则）。

    这里特意使用精确的 ≥30 阈值，而非交给模型"模糊判断"，
    体现了 Agent 设计中一个重要原则：
      → 确定性业务规则应交给工具实现，而不是让模型猜测。

    Args:
        value: 温度数值（摄氏度）

    Returns:
        "炎热" 或 "舒适"
    """
    return "炎热" if value >= 30 else "舒适"


# ── 工具注册表 ─────────────────────────────────────────────────
# 白名单机制：Agent 只能调用此处注册的工具，避免任意代码执行风险。
# 键为工具名称（字符串），值为对应的 Callable 对象。
TOOLS: dict[str, Callable[..., Any]] = {
    "get_temperature": get_temperature,
    "classify_temperature": classify_temperature,
}


# ═══════════════════════════════════════════════════════════════
#   决策器（核心 —— 当前是规则引擎，后续章节替换为大模型）
# ═══════════════════════════════════════════════════════════════

def decide(state: AgentState) -> Decision:
    """[决策器] 根据当前 Agent 状态，决定下一步做什么。

    这是整个 Agent 循环的"大脑"。当前实现使用确定性规则模拟
    决策过程，后续章节将替换为调用大模型 API。

    决策逻辑（三步走，每步对应 observations 的不同长度）：
      第 0 步：observations 为空 → 发起第一次工具调用"查询温度"
      第 1 步：observations 有 1 条 → 拿到温度后，调用"温度分类"
      第 2 步：observations 有 2 条 → 汇总结果，返回最终答案

    Args:
        state: Agent 当前状态（包含目标和所有历史观察）

    Returns:
        Decision 对象，指示下一步是调用工具还是结束任务
    """
    # ── 第 0 步：还没有任何观察 → 先去查询北京的温度 ──
    if not state.observations:
        return Decision("tool", "get_temperature", {"city": "上海"})

    # ── 第 1 步：拿到了温度 → 调用分类工具判断体感 ──
    if len(state.observations) == 1:
        temperature = state.observations[0]["result"]
        return Decision(
            "tool", "classify_temperature", {"value": temperature}
        )

    # ── 第 2 步：温度和分类都有了 → 组装最终答案，结束任务 ──
    temperature = state.observations[0]["result"]   # 第 1 条：温度值
    label = state.observations[1]["result"]          # 第 2 条：分类标签
    return Decision(
        "finish",
        answer=f"上海当前演示温度为 {temperature}℃，体感分类为：{label}。",
    )


# ═══════════════════════════════════════════════════════════════
#   执行器（安全沙箱）
# ═══════════════════════════════════════════════════════════════

def execute(decision: Decision) -> dict[str, Any]:
    """[执行器] 安全地执行一个工具调用决策，返回观察结果。

    包含两层安全校验：
      1. 类型校验：只接受 kind=="tool" 的决策
      2. 白名单校验：工具名必须在 TOOLS 注册表中

    Args:
        decision: 决策器输出的 Decision 对象

    Returns:
        格式化的观察字典 {"tool": ..., "arguments": ..., "result": ...}

    Raises:
        ValueError: 决策类型不是 tool、工具名不在白名单中时抛出
    """
    # 安全检查第 1 层：确保这是 tool 类型的决策
    if decision.kind != "tool" or decision.tool_name is None:
        raise ValueError("只有 tool 决策可以执行")

    # 安全检查第 2 层：白名单校验，防止任意代码执行
    if decision.tool_name not in TOOLS:
        raise ValueError(f"工具不在白名单中：{decision.tool_name}")

    # 通过全部校验后，用 **arguments 展开参数字典调用工具
    result = TOOLS[decision.tool_name](**decision.arguments)

    # 将执行结果包装为标准化观察，方便状态追踪和调试
    return {
        "tool": decision.tool_name,
        "arguments": decision.arguments,
        "result": result,
    }


# ═══════════════════════════════════════════════════════════════
#   Agent 主循环（将决策器 + 执行器串联起来）
# ═══════════════════════════════════════════════════════════════

def run_agent(goal: str, max_steps: int = 4) -> tuple[str, AgentState]:
    """[主循环] 启动 Agent，反复"决策 → 执行"直到完成或超步数。

    核心循环流程：
      ┌─────────────────────────────────────────┐
      │  1. decide(state)  →  拿到决策          │
      │  2. 如果 kind=="finish" → 返回最终答案   │
      │  3. 否则 execute(decision) → 得到观察    │
      │  4. 观察追加到 state.observations        │
      │  5. 回到步骤 1（循环）                    │
      └─────────────────────────────────────────┘

    Args:
        goal:      用户给定的任务目标（目前仅用于状态记录）
        max_steps: 最大执行步数，防止无限循环（默认 4 步）

    Returns:
        (最终答案文本, Agent 最终状态) 的元组

    Raises:
        ValueError:          max_steps < 1 时
        StepLimitExceeded:   超过 max_steps 仍未完成时
    """
    # 参数校验
    if max_steps < 1:
        raise ValueError("max_steps 必须大于 0")

    # 初始化 Agent 状态，记录目标任务
    state = AgentState(goal=goal)

    # 主循环：每次迭代代表一个"思考-行动"回合
    for _ in range(max_steps):
        # 第 1 步：决策器根据当前状态选择动作
        decision = decide(state)

        # 第 2 步：如果决策器认为任务已完成，返回最终答案
        if decision.kind == "finish":
            if decision.answer is None:
                raise ValueError("finish 决策必须包含 answer")
            return decision.answer, state

        # 第 3 步：执行工具调用，将观察结果追加到状态中
        state.observations.append(execute(decision))

    # 超出最大步数：抛出安全兜底异常，防止死循环
    raise StepLimitExceeded(f"Agent 在 {max_steps} 步内没有完成任务")


# ═══════════════════════════════════════════════════════════════
#   入口（直接运行 python decision_loop.py 即可执行）
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 启动 Agent，目标：查询北京温度后判断体感
    final_answer, final_state = run_agent(
        "先查询上海温度，再判断是否炎热"
    )

    # 打印每一步的工具调用记录
    for index, observation in enumerate(final_state.observations, start=1):
        print(f"步骤 {index}: {observation}")

    # 打印最终汇总答案
    print(f"最终答案: {final_answer}")

