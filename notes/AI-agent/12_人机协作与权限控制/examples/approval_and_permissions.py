"""授权、interrupt 审批、resume 与幂等执行的完整示例。"""

from typing import Literal
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict):
    action_id: str
    actor_role: str
    action: str
    resource: str
    risk: Literal["low", "high"]
    status: Literal[
        "pending", "denied", "awaiting_approval",
        "approved", "rejected", "executed"
    ]
    executed_action_ids: list[str]
    audit_log: list[str]


ALLOWED_ACTIONS = {
    "reader": {"read"},
    "editor": {"read", "draft"},
    "admin": {"read", "draft", "delete"},
}


def authorize(state: ApprovalState) -> dict:
    allowed = state["action"] in ALLOWED_ACTIONS.get(
        state["actor_role"], set()
    )
    if not allowed:
        return {
            "status": "denied",
            "audit_log": state["audit_log"] + ["授权失败：默认拒绝"],
        }
    if state["risk"] == "high":
        return {"status": "awaiting_approval"}
    return {"status": "approved"}


def route_after_authorize(
    state: ApprovalState,
) -> Literal["approve", "execute", "stop"]:
    if state["status"] == "awaiting_approval":
        return "approve"
    if state["status"] == "approved":
        return "execute"
    return "stop"


def request_approval(state: ApprovalState) -> dict:
    # 恢复时节点从开头重跑，因此 interrupt 前不执行外部副作用。
    response = interrupt(
        {
            "action_id": state["action_id"],
            "action": state["action"],
            "resource": state["resource"],
            "risk": state["risk"],
            "allowed_decisions": ["approve", "reject"],
        }
    )
    decision = response.get("decision") if isinstance(response, dict) else None
    if decision == "approve":
        return {
            "status": "approved",
            "audit_log": state["audit_log"] + ["人工审批：通过"],
        }
    return {
        "status": "rejected",
        "audit_log": state["audit_log"] + ["人工审批：拒绝"],
    }


def route_after_approval(
    state: ApprovalState,
) -> Literal["execute", "stop"]:
    return "execute" if state["status"] == "approved" else "stop"


def execute_action(state: ApprovalState) -> dict:
    # 真实系统还应在数据库或外部 API 中使用同一幂等键。
    if state["action_id"] in state["executed_action_ids"]:
        return {
            "status": "executed",
            "audit_log": state["audit_log"] + ["检测到重复请求，未重复执行"],
        }
    print(f"[模拟执行] {state['action']} -> {state['resource']}")
    return {
        "status": "executed",
        "executed_action_ids": (
            state["executed_action_ids"] + [state["action_id"]]
        ),
        "audit_log": state["audit_log"] + ["动作已执行"],
    }


def build_graph():
    builder = StateGraph(ApprovalState)
    builder.add_node("authorize", authorize)
    builder.add_node("request_approval", request_approval)
    builder.add_node("execute", execute_action)
    builder.add_edge(START, "authorize")
    builder.add_conditional_edges(
        "authorize",
        route_after_authorize,
        {
            "approve": "request_approval",
            "execute": "execute",
            "stop": END,
        },
    )
    builder.add_conditional_edges(
        "request_approval",
        route_after_approval,
        {"execute": "execute", "stop": END},
    )
    builder.add_edge("execute", END)
    return builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    graph = build_graph()
    config = {"configurable": {"thread_id": "demo:approval:action-001"}}
    initial: ApprovalState = {
        "action_id": "action-001",
        "actor_role": "admin",
        "action": "delete",
        "resource": "demo/report-2026.txt",
        "risk": "high",
        "status": "pending",
        "executed_action_ids": [],
        "audit_log": [],
    }

    paused = graph.invoke(initial, config=config)
    print("等待审批：", paused["__interrupt__"])

    result = graph.invoke(
        Command(resume={"decision": "approve"}),
        config=config,
    )
    print("最终状态：", result)
    assert result["status"] == "executed"
