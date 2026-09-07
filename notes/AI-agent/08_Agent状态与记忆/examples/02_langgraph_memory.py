"""LangGraph：checkpointer 保存 thread 消息，store 保存跨 thread 偏好。"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore


def respond(
    state: MessagesState,
    config: RunnableConfig,
    *,
    store: BaseStore,
) -> dict:
    configurable = config.get("configurable", {})
    user_id = str(configurable.get("user_id", ""))
    if not user_id:
        raise ValueError("configurable.user_id 不能为空")

    last_message = str(state["messages"][-1].content)
    namespace = (user_id, "preferences")

    if last_message.startswith("记住语言="):
        language = last_message.split("=", 1)[1].strip()
        if not language:
            answer = "语言不能为空。"
        else:
            store.put(
                namespace,
                "language",
                {"value": language, "source": "explicit_user_request"},
            )
            answer = f"已保存长期偏好：{language}。"
    else:
        item = store.get(namespace, "language")
        language = item.value["value"] if item else "未设置"
        human_count = sum(
            isinstance(message, HumanMessage) for message in state["messages"]
        )
        answer = (
            f"当前 thread 已有 {human_count} 条用户消息；"
            f"跨 thread 语言偏好为 {language}。"
        )
    return {"messages": [AIMessage(content=answer)]}


def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile(
        checkpointer=InMemorySaver(),
        store=InMemoryStore(),
    )


def main() -> None:
    graph = build_graph()
    config_a = {
        "configurable": {"thread_id": "thread-a", "user_id": "user-42"}
    }
    config_b = {
        "configurable": {"thread_id": "thread-b", "user_id": "user-42"}
    }

    first = graph.invoke(
        {"messages": [HumanMessage(content="记住语言=中文")]},
        config_a,
    )
    print(first["messages"][-1].content)

    # 新 thread 没有旧对话，但同一 user_id 可以读取长期偏好。
    second = graph.invoke(
        {"messages": [HumanMessage(content="这是一个新会话")]},
        config_b,
    )
    print(second["messages"][-1].content)

    # 回到同一 thread，checkpointer 会累计该 thread 的消息。
    third = graph.invoke(
        {"messages": [HumanMessage(content="继续当前会话")]},
        config_b,
    )
    print(third["messages"][-1].content)


if __name__ == "__main__":
    main()
