"""有最大派发次数的 Supervisor 多 Agent 工作流。"""

from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph

WorkerName = Literal["research", "write", "verify", "finish", "fail"]


class TeamState(TypedDict):
    task: str
    completed_workers: list[str]
    results: dict[str, str]
    next_worker: WorkerName
    dispatch_count: int
    max_dispatches: int
    status: Literal["running", "completed", "failed"]
    error: str


def supervisor(state: TeamState) -> dict:
    if state["dispatch_count"] >= state["max_dispatches"]:
        return {
            "next_worker": "fail",
            "status": "failed",
            "error": "达到最大派发次数",
        }

    completed = set(state["completed_workers"])
    for worker in ("research", "write", "verify"):
        if worker not in completed:
            return {
                "next_worker": worker,
                "dispatch_count": state["dispatch_count"] + 1,
            }
    return {"next_worker": "finish", "status": "completed"}


def route_supervisor(state: TeamState) -> WorkerName:
    return state["next_worker"]


def research_worker(state: TeamState) -> dict:
    results = dict(state["results"])
    results["research"] = f"已为“{state['task']}”收集三条可验证资料"
    return {
        "results": results,
        "completed_workers": state["completed_workers"] + ["research"],
    }


def writing_worker(state: TeamState) -> dict:
    assert "research" in state["results"], "写作前必须先完成研究"
    results = dict(state["results"])
    results["write"] = "根据研究结果形成结构化初稿"
    return {
        "results": results,
        "completed_workers": state["completed_workers"] + ["write"],
    }


def verify_worker(state: TeamState) -> dict:
    assert "write" in state["results"], "校验前必须先完成写作"
    results = dict(state["results"])
    results["verify"] = "已检查来源、结构和权限边界"
    return {
        "results": results,
        "completed_workers": state["completed_workers"] + ["verify"],
    }


def build_graph():
    builder = StateGraph(TeamState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("research", research_worker)
    builder.add_node("write", writing_worker)
    builder.add_node("verify", verify_worker)
    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "research": "research",
            "write": "write",
            "verify": "verify",
            "finish": END,
            "fail": END,
        },
    )
    for worker in ("research", "write", "verify"):
        builder.add_edge(worker, "supervisor")
    return builder.compile()


if __name__ == "__main__":
    initial: TeamState = {
        "task": "编写 Agent 工作流说明",
        "completed_workers": [],
        "results": {},
        "next_worker": "research",
        "dispatch_count": 0,
        "max_dispatches": 4,
        "status": "running",
        "error": "",
    }
    result = build_graph().invoke(initial, config={"recursion_limit": 20})
    print(result)
    assert result["status"] == "completed"
