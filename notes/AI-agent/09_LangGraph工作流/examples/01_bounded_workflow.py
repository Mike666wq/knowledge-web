"""带业务上限与运行时上限的 LangGraph 修订工作流。"""

from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class DraftState(TypedDict):
    topic: str
    draft: str
    score: int
    attempts: int
    max_attempts: int
    status: Literal["running", "completed", "failed"]
    failure_reason: str


def create_draft(state: DraftState) -> dict:
    """真实项目可在此调用模型；教程使用确定性文本。"""
    return {
        "draft": f"{state['topic']}：核心结论",
        "score": 0,
        "attempts": 1,
        "status": "running",
        "failure_reason": "",
    }


def review_draft(state: DraftState) -> dict:
    score = min(100, 40 + len(state["draft"]) * 2)
    return {"score": score}


def route_after_review(
    state: DraftState,
) -> Literal["complete", "revise", "fail"]:
    if state["score"] >= 80:
        return "complete"
    if state["attempts"] >= state["max_attempts"]:
        return "fail"
    return "revise"


def revise_draft(state: DraftState) -> dict:
    return {
        "draft": state["draft"] + "；补充依据、限制条件与可执行建议",
        "attempts": state["attempts"] + 1,
    }


def complete(state: DraftState) -> dict:
    return {"status": "completed"}


def fail(state: DraftState) -> dict:
    return {
        "status": "failed",
        "failure_reason": (
            f"达到最大修订次数 {state['max_attempts']}，"
            f"当前分数仍为 {state['score']}"
        ),
    }


def build_graph():
    builder = StateGraph(DraftState)
    builder.add_node("create_draft", create_draft)
    builder.add_node("review_draft", review_draft)
    builder.add_node("revise_draft", revise_draft)
    builder.add_node("complete", complete)
    builder.add_node("fail", fail)

    builder.add_edge(START, "create_draft")
    builder.add_edge("create_draft", "review_draft")
    builder.add_conditional_edges(
        "review_draft",
        route_after_review,
        {
            "complete": "complete",
            "revise": "revise_draft",
            "fail": "fail",
        },
    )
    builder.add_edge("revise_draft", "review_draft")
    builder.add_edge("complete", END)
    builder.add_edge("fail", END)
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    initial_state: DraftState = {
        "topic": "为什么 Agent 循环必须有上限",
        "draft": "",
        "score": 0,
        "attempts": 0,
        "max_attempts": 3,
        "status": "running",
        "failure_reason": "",
    }
    # recursion_limit 是运行时保险，max_attempts 是可解释的业务规则。
    result = graph.invoke(initial_state, config={"recursion_limit": 20})
    print(result)

