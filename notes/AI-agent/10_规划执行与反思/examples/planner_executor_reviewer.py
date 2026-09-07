"""离线可运行的 Planner–Executor–Reviewer 工作流。"""

from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class PlanState(TypedDict):
    goal: str
    plan: list[str]
    current_step: int
    results: list[str]
    review: str
    revision_count: int
    max_steps: int
    max_revisions: int
    status: Literal["running", "completed", "failed"]


def planner(state: PlanState) -> dict:
    if state["revision_count"] > 0:
        # 只规划审查指出的缺口，不重复执行已完成步骤。
        base_plan = ["根据审查反馈补充证据"]
    else:
        base_plan = ["明确验收标准", "收集必要信息", "形成并检查答案"]
    if len(base_plan) > state["max_steps"]:
        return {"status": "failed", "review": "计划超过最大步骤数"}
    return {"plan": base_plan, "current_step": 0}


def route_after_plan(state: PlanState) -> Literal["execute", "fail"]:
    return "fail" if state["status"] == "failed" else "execute"


def executor(state: PlanState) -> dict:
    index = state["current_step"]
    step = state["plan"][index]
    result = f"步骤 {index + 1} 已完成：{step}"
    return {
        "results": state["results"] + [result],
        "current_step": index + 1,
    }


def route_after_execute(state: PlanState) -> Literal["execute", "review"]:
    return "execute" if state["current_step"] < len(state["plan"]) else "review"


def reviewer(state: PlanState) -> dict:
    has_evidence = any("补充证据" in item for item in state["results"])
    if has_evidence:
        return {"review": "验收通过", "status": "completed"}
    if state["revision_count"] >= state["max_revisions"]:
        return {"review": "达到最大修订次数，仍缺少证据", "status": "failed"}
    return {
        "review": "请增加一个补充证据步骤",
        "revision_count": state["revision_count"] + 1,
    }


def route_after_review(
    state: PlanState,
) -> Literal["complete", "revise", "fail"]:
    if state["status"] == "completed":
        return "complete"
    if state["status"] == "failed":
        return "fail"
    return "revise"


def build_graph():
    builder = StateGraph(PlanState)
    builder.add_node("planner", planner)
    builder.add_node("executor", executor)
    builder.add_node("reviewer", reviewer)
    builder.add_edge(START, "planner")
    builder.add_conditional_edges(
        "planner",
        route_after_plan,
        {"execute": "executor", "fail": END},
    )
    builder.add_conditional_edges(
        "executor",
        route_after_execute,
        {"execute": "executor", "review": "reviewer"},
    )
    builder.add_conditional_edges(
        "reviewer",
        route_after_review,
        {"complete": END, "revise": "planner", "fail": END},
    )
    return builder.compile()


if __name__ == "__main__":
    initial: PlanState = {
        "goal": "生成一份可验证的 Agent 学习建议",
        "plan": [],
        "current_step": 0,
        "results": [],
        "review": "",
        "revision_count": 0,
        "max_steps": 5,
        "max_revisions": 2,
        "status": "running",
    }
    result = build_graph().invoke(initial, config={"recursion_limit": 30})
    print(result)
    assert result["status"] == "completed"
