"""演示 checkpointer 与 thread_id 的状态隔离。"""

from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class CounterState(TypedDict):
    value: int


def add_one(state: CounterState) -> dict:
    return {"value": state["value"] + 1}


def build_graph():
    builder = StateGraph(CounterState)
    builder.add_node("add_one", add_one)
    builder.add_edge(START, "add_one")
    builder.add_edge("add_one", END)
    return builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    graph = build_graph()
    config_a = {"configurable": {"thread_id": "demo:user-a:task-1"}}
    config_b = {"configurable": {"thread_id": "demo:user-b:task-1"}}

    graph.invoke({"value": 0}, config=config_a)
    graph.invoke({"value": 100}, config=config_b)
    # 空更新会从同一 thread 的 checkpoint 恢复 value=1，再执行 add_one。
    graph.invoke({}, config=config_a)

    snapshot_a = graph.get_state(config_a)
    snapshot_b = graph.get_state(config_b)
    print("A 最新快照：", snapshot_a.values)
    print("B 最新快照：", snapshot_b.values)

    assert snapshot_a.values["value"] == 2
    assert snapshot_b.values["value"] == 101
