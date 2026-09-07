# 08 Agent 状态与记忆

> 状态是一次运行当前“拥有什么数据”；记忆是有选择地保存、在未来重新取回的数据。状态不一定持久化，持久化状态也不一定都值得称为记忆。

## 学习目标

完成本章后，你应该能够：

- 区分运行状态、短期记忆、长期记忆、知识库和缓存。
- 设计最小、可序列化、可演进的 Agent 状态。
- 理解 reducer、checkpoint、thread 与 store 的职责。
- 用纯 Python 实现线程状态和跨线程用户记忆。
- 用 LangGraph `InMemorySaver` 与 `InMemoryStore` 演示短期和长期记忆。
- 为有状态循环设置终止条件，并处理并发、损坏状态和存储异常。

## 1. 术语

| 术语 | 含义 |
| --- | --- |
| State（状态） | 当前运行步骤可读写的数据快照，例如消息、步骤数、工具结果和审批状态。 |
| State Schema | 状态字段及类型组成的契约，常用 `TypedDict` 或 Pydantic 表达。 |
| Reducer | 当节点返回新值时，决定状态字段是覆盖、追加还是自定义合并的函数。 |
| Checkpoint | 某个执行边界上的状态快照，用于恢复、历史查看和容错。 |
| Checkpointer | 按 `thread_id` 保存和读取 checkpoint 的组件。 |
| Thread | 一条会话或任务执行序列的标识；同一 thread 的短期状态可跨调用延续。 |
| Short-term Memory | 线程范围内的记忆，通常就是被 checkpointer 持久化的会话状态。 |
| Long-term Memory | 跨 thread 保存的数据，通常按用户/组织等 namespace 存入 Store。 |
| Store | 保存长期记忆的键值或语义检索接口，数据通常由 namespace + key 定位。 |
| Semantic Memory | 事实和偏好，例如“用户偏好中文回答”。 |
| Episodic Memory | 过去发生的事件或成功案例。 |
| Procedural Memory | 做事规则和流程，例如审批策略。 |
| Cache | 为性能复用计算结果，不代表系统应该把内容当作用户记忆。 |

## 2. 核心原理：按作用域与生命周期区分数据

| 数据 | 典型范围 | 典型内容 | 推荐载体 |
| --- | --- | --- | --- |
| 临时局部变量 | 一个函数 | 中间计算值 | Python 局部变量 |
| 运行状态 | 一次图运行 | 当前节点、步骤数、工具结果 | Graph State |
| 短期记忆 | 一个 thread | 对话消息、当前任务上下文 | State + Checkpointer |
| 长期记忆 | 跨 thread | 用户偏好、长期事实 | Store + namespace |
| 知识库 | 多用户/领域 | 手册、制度、产品文档 | 文档库/检索系统 |

用户说“我偏好简洁回答”，若只在当前对话使用，是短期记忆；若经同意保存并在新会话使用，是长期语义记忆。公司手册则属于知识库，不应复制进每个用户记忆。

## 3. 状态设计

### 3.1 只保存恢复所需数据

```python
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: list
    step_count: int
    status: str
    last_error: str | None
```

不要把数据库连接、打开的文件句柄、线程锁或巨大二进制对象放入状态。状态通常要被序列化、复制和持久化。

### 3.2 节点返回增量更新

LangGraph 节点通常读取完整状态，但只返回本节点要更新的字段：

```python
def increment(state: AgentState) -> dict:
    return {"step_count": state["step_count"] + 1}
```

直接原地修改输入会让追踪、并行合并和测试更难理解。

### 3.3 Reducer 决定“怎么合并”

普通字段默认由新值覆盖。消息列表需要追加并正确处理消息 ID，因此应使用 `MessagesState` 或 `add_messages`，而不是简单 `old + new`。多个并行节点写同一字段时必须定义确定的合并规则，否则应避免并行写冲突。

## 4. 短期记忆：State + Checkpointer

短期记忆属于 thread：

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "conversation-001"}}
graph.invoke({"messages": [{"role": "user", "content": "我叫小林"}]}, config)
graph.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, config)
```

第二次调用使用相同 `thread_id`，checkpointer 才能加载之前的状态。换一个 `thread_id` 就是新会话。

`InMemorySaver` 只适合教学和测试，进程退出后数据丢失。生产环境应选择持久化实现，并处理迁移、加密、备份、连接池和数据保留策略。

## 5. 长期记忆：Store + Namespace

长期记忆跨 thread，共享范围由 namespace 决定：

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
namespace = ("user-42", "preferences")
store.put(namespace, "language", {"value": "zh-CN"})
item = store.get(namespace, "language")
```

namespace 应来自已认证身份，不能直接相信模型或用户输入。常见形式：

```text
(tenant_id, user_id, memory_type)
```

长期记忆不应“什么都记”。写入前要确定：

- 是否得到用户同意。
- 是否确有未来价值。
- 是否敏感或有过期时间。
- 新内容与旧内容冲突时如何更新。
- 用户如何查看、更正和删除。

## 6. Checkpointer 与 Store 的区别

| 对比 | Checkpointer | Store |
| --- | --- | --- |
| 主键范围 | `thread_id` | 自定义 namespace + key |
| 主要对象 | 图状态快照 | 业务定义的长期记忆 |
| 跨 thread | 否 | 可以 |
| 恢复执行 | 是 | 不是主要职责 |
| 典型内容 | 消息、当前节点、步骤状态 | 偏好、画像、长期事实 |

二者可以同时使用：checkpointer 让当前对话连续，store 让同一用户在新对话中仍能取回经过选择的偏好。

## 7. 上下文过长与记忆压缩

短期消息持续追加会增加费用并降低模型对关键信息的关注。常见策略：

1. 保留最近 N 条消息。
2. 按 Token 预算裁剪。
3. 将较早对话总结为结构化摘要。
4. 把稳定偏好提取为长期记忆，再从短期历史移除冗余表达。

摘要是有损压缩，必须保留关键事实来源，不能把模型猜测写成用户事实。高风险任务应保留必要原始记录用于审计。

## 8. 记忆写入时机

### 热路径写入

在回答前识别并保存记忆。新会话立即可用，但增加延迟，而且错误写入会马上影响当前任务。

### 后台写入

回答后异步提取、去重和审核。延迟更低，更适合批量治理，但刚保存的信息可能暂时不可见。

无论哪种方式，建议保存：值、来源、创建时间、更新时间、置信或确认状态，而不只是一个裸字符串。

## 9. 终止条件与状态机

状态让终止条件可以被确定性检查：

```python
def route(state: AgentState) -> str:
    if state["status"] in {"completed", "failed", "cancelled"}:
        return "end"
    if state["step_count"] >= 8:
        return "budget_exceeded"
    if state["last_error"] and not state.get("retryable", False):
        return "failed"
    return "continue"
```

推荐把终止原因写入状态：

- `completed`：目标已完成。
- `needs_input`：缺少用户信息。
- `failed`：不可恢复错误。
- `budget_exceeded`：步数、时间、Token 或费用超限。
- `cancelled`：用户取消。

同时使用图的 `recursion_limit` 作为最后保险，但业务终止条件应由自己的状态字段表达。

## 10. 异常与一致性

### 存储失败

不要在保存失败时谎称“我已经记住”。根据业务选择重试、降级为当前 thread 使用或明确告知未保存。

### 并发更新

同一用户可能在多个 thread 同时修改偏好。使用版本号、条件更新或数据库事务，避免最后写入静默覆盖。

### 状态 Schema 演进

已保存 checkpoint 可能来自旧代码。新增字段应有默认值；删除或改名需要迁移策略和兼容窗口。

### 损坏或不可信状态

恢复后仍要校验状态。不要因为值来自自己的数据库就跳过类型、权限和范围检查。

### 重放副作用

恢复执行可能再次运行节点。写操作需要幂等键或“已提交”记录，避免重复付款、发信或创建工单。

## 11. 完整示例

### 11.1 纯 Python

[examples/01_python_state_memory.py](examples/01_python_state_memory.py) 实现线程状态仓库和跨线程用户偏好仓库，清楚展示同一用户换 thread 后哪些数据保留：

```bash
python 08_Agent状态与记忆/examples/01_python_state_memory.py
```

### 11.2 LangGraph

[examples/02_langgraph_memory.py](examples/02_langgraph_memory.py) 使用 `MessagesState`、`InMemorySaver` 和 `InMemoryStore`，不调用模型也不需要 API Key：

```bash
python 08_Agent状态与记忆/examples/02_langgraph_memory.py
```

示例使用内存后端是为了可运行性，不是生产存储建议。

## 12. 常见错误

### 错误 1：把状态和记忆当作同义词

状态描述当前运行；记忆强调跨时间保存和取回。`step_count` 是状态，通常不应成为用户长期记忆。

### 错误 2：所有消息永久放进 Prompt

checkpoint 可以保存历史，不代表每次都应把全部历史发送给模型。持久化策略和上下文策略是两件事。

### 错误 3：换 thread 后期待短期记忆仍存在

跨 thread 的信息必须显式写入 Store；不要通过复用所有用户的同一个 thread 伪造长期记忆。

### 错误 4：把用户 ID 交给模型决定

身份和 namespace 必须来自认证上下文，否则会发生跨用户记忆读取。

### 错误 5：自动保存所有敏感信息

记忆需要最小化、同意、用途和删除机制。密钥、完整证件号等不应进入普通记忆 Store。

### 错误 6：恢复节点时重复副作用

checkpoint 恢复保证状态连续，不自动保证外部 API 幂等。

## 13. 练习

1. 为纯 Python 示例增加记忆删除和过期时间。
2. 用两个不同用户 ID 验证 namespace 隔离。
3. 为 LangGraph 示例新增 `step_count`，达到 3 时进入 `budget_exceeded`。
4. 设计一份长期偏好 Schema，包含值、来源、用户确认状态和更新时间。
5. 模拟存储写入失败，确保程序不会告诉用户“保存成功”。
6. 说明一个你项目中的字段为何属于状态、短期记忆、长期记忆或知识库。

## 14. 小结

- State、短期记忆和长期记忆的差别首先在作用域和生命周期。
- Checkpointer 按 thread 保存状态快照；Store 按 namespace 保存跨 thread 记忆。
- 状态要最小、可序列化、可迁移；并行更新要有 reducer 或冲突策略。
- 长期记忆要有同意、隔离、更新、过期和删除机制。
- 有状态 Agent 仍必须用明确状态表达成功、失败、取消和预算终止。

下一模块将在这些概念上使用 LangGraph 显式定义节点、边、条件路由和循环。

## 参考资料

- [LangGraph Memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangChain Memory Concepts](https://docs.langchain.com/oss/python/concepts/memory)
