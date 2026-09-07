# 09 LangGraph 工作流

## 本章定位

Chain 适合固定步骤，Agent 循环适合让模型在有限动作中选择。真实业务还需要显式分支、循环、恢复和状态审计。LangGraph 是一个有状态工作流运行时：开发者定义状态、节点和控制流，运行时负责推进、合并状态和保存检查点。

## 学习目标

1. 解释 StateGraph、State、节点、边、条件路由和 reducer。
2. 构建顺序、分支和循环三种图结构。
3. 给循环设置业务终止条件和运行时上限。
4. 使用 checkpointer，并用 thread_id 隔离执行线程。
5. 区分图内状态、checkpoint 和长期业务数据。

## 前置知识

- Python 函数、类型标注与 TypedDict。
- Agent 的“观察 → 决策 → 行动 → 再观察”循环。
- 状态是当前工作流的数据；记忆是跨步骤或跨调用保留的信息。

## 1. 核心术语

| 术语 | 含义 | 关键问题 |
| --- | --- | --- |
| State | 节点共享的数据契约 | 哪些字段必须跨节点传递？ |
| StateGraph | 基于 State 定义节点和边的图构建器 | 流程有哪些步骤？ |
| Node | 读取 State、执行单一职责并返回局部更新的函数 | 是否只做一件事？ |
| Edge | 节点间的控制流连接 | 下一步固定还是由状态决定？ |
| START / END | 图的逻辑入口与终点 | 所有路径都能结束吗？ |
| Conditional edge | 根据路由函数选择后继节点 | 是否覆盖所有情况？ |
| Reducer | 字段收到新值时的合并规则 | 覆盖、追加还是自定义？ |
| Checkpoint | 某条线程在超步边界上的状态快照 | 是否需要恢复与审计？ |
| Checkpointer | 保存和读取 checkpoint 的组件 | 是否需要持久化？ |
| thread_id | 持久化执行线程的标识 | 是否稳定、唯一、隔离？ |
| Recursion limit | 一次调用允许推进的最大超步数 | 失控时怎样硬停止？ |

“递归上限”约束图执行步数，并不要求 Python 函数真的递归。

## 2. StateGraph 的执行模型

~~~text
START → normalize → validate → END
~~~

1. 调用方传入初始 State。
2. START 把执行权交给入口节点。
3. 节点读取 State，返回需要更新的字段。
4. LangGraph 按 reducer 合并更新。
5. 普通边或条件边决定下一节点。
6. 到达 END 后返回最终 State。

节点应返回局部更新：

~~~python
class OrderState(TypedDict):
    quantity: int
    unit_price: float
    total: float


def calculate_total(state: OrderState) -> dict:
    return {"total": state["quantity"] * state["unit_price"]}
~~~

这能明确字段写权限，也减少并行更新冲突。

## 3. 节点、边与条件路由

普通边表达固定顺序：

~~~python
builder.add_edge(START, "normalize")
builder.add_edge("normalize", "validate")
builder.add_edge("validate", END)
~~~

确定性规则优先写成普通节点，不必让 LLM 参与。条件边读取最新状态并选择后继节点：

~~~python
from typing import Literal


def route_after_validate(
    state: OrderState,
) -> Literal["accept", "reject"]:
    return "accept" if state["total"] <= 10_000 else "reject"


builder.add_conditional_edges(
    "validate",
    route_after_validate,
    {"accept": "accept_order", "reject": "reject_order"},
)
~~~

accept 与 reject 是路由标签，映射值才是节点名。路由函数应返回有限集合中的值，覆盖全部路径，且不执行网络请求或外部写入。

## 4. 循环、退出条件与上限

循环就是边重新指向上游节点：

~~~text
draft → review ──通过──→ END
          │
          └─需修改──→ revise → review
~~~

每个循环必须有两层保护：

1. 业务退出条件：完成、达标、无步骤可执行或确认失败。
2. 硬上限：attempts 大于等于 max_attempts，并在调用配置设置 recursion_limit。

达到上限时要记录失败原因，不能把未达标结果伪装成成功。[01_bounded_workflow.py](./examples/01_bounded_workflow.py) 给出了完整实现。

## 5. State 与 reducer

没有 reducer 时，新值通常覆盖旧值。列表需累积时显式声明：

~~~python
import operator
from typing import Annotated


class ResearchState(TypedDict):
    query: str
    notes: Annotated[list[str], operator.add]
~~~

消息历史推荐使用 add_messages：

~~~python
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
~~~

只导入 add_messages 不会生效，必须通过 Annotated 声明。State 中不要保存密钥、数据库连接、文件句柄或无上限的大对象。

## 6. checkpoint、checkpointer 与 thread_id

~~~text
同一张图
├── thread_id = order-1001 → checkpoint 1 → checkpoint 2
└── thread_id = order-1002 → checkpoint 1 → checkpoint 2
~~~

- checkpoint 是状态快照。
- checkpointer 是存储组件。
- thread_id 告诉 checkpointer 读写哪条线程。

~~~python
from langgraph.checkpoint.memory import InMemorySaver

graph = builder.compile(checkpointer=InMemorySaver())
config = {
    "configurable": {"thread_id": "order-1001"},
    "recursion_limit": 20,
}
result = graph.invoke(initial_state, config=config)
snapshot = graph.get_state(config)
~~~

一个用户可以有多个任务，因此 thread_id 不等于 user_id。可组合 tenant_id、user_id 和 workflow_instance_id 形成标识；服务端还必须验证调用者是否拥有该线程。

InMemorySaver 只适合教程和测试：进程退出即丢失，多进程不共享。生产中要使用持久化 checkpointer，并配置保留期、加密、租户隔离和清理策略。[02_checkpoint_threads.py](./examples/02_checkpoint_threads.py) 演示两个线程的状态隔离。

## 7. 副作用与失败边界

恢复状态不等于副作用安全。发送邮件、扣款或数据库写入在重试后可能重复执行：

- 使用 thread_id 与 action_id 组成幂等键。
- 先记录操作意图，再执行外部动作。
- 只对可重试错误做有限重试。
- 高风险动作进入第 12 章的人工审批。
- 可恢复错误走补救分支，不无限回环。

## 8. 常见错误

1. 节点返回整个旧 State，导致 reducer 重复追加；只返回变化字段。
2. 路由值与映射键不一致；用 Literal 限制并测试全部分支。
3. 循环没有失败出口；必须设置业务上限和 recursion_limit。
4. 错误复用 thread_id；共用会串状态，恢复时换 ID 又找不到检查点。
5. 把 checkpoint 当知识库；它不替代业务库或向量库。

## 9. 运行示例

~~~bash
python examples/01_bounded_workflow.py
python examples/02_checkpoint_threads.py
~~~

## 10. 练习与验收

1. 增加 cancelled 状态，让调用方提前取消。
2. 测试“通过、继续修订、达到上限”三条路由。
3. 换成持久化 checkpointer，验证进程重启后恢复。
4. 设计订单审批 State，标出模型与业务系统各自可写字段。
5. 分别触发 max_attempts 与 recursion_limit。

检查清单：

- [ ] State 字段类型和职责清晰，节点只返回局部更新。
- [ ] 条件路由映射完整，每个回边都有退出条件。
- [ ] 调用配置有 recursion_limit。
- [ ] checkpoint 不含密钥或无上限对象。
- [ ] thread_id 唯一并经过访问控制。
- [ ] 外部副作用具备幂等或审批机制。

## 11. 本章小结

StateGraph 把数据流与控制流分开：State 说明“传什么”，节点说明“做什么”，边说明“接下来去哪”。条件边带来分支，回边带来循环，checkpointer 与 thread_id 带来可恢复执行；可靠系统还必须有上限、隔离和副作用保护。

下一章在此基础上实现 planner → executor → reviewer。
