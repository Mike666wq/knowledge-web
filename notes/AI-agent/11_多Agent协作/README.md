# 11 多 Agent 协作

## 本章定位

多 Agent 不是“模型越多越聪明”。它的价值是职责、工具和上下文隔离；代价是路由错误、信息丢失、成本增加和更难测试。单 Agent 加合适工具能解决时，优先保持简单。

## 学习目标

1. 解释 Supervisor、Worker、Router、Handoff 和共享状态。
2. 选择流水线、路由、Supervisor 或评审模式。
3. 构建有最大派发次数的 Supervisor 工作流。
4. 为每个 Agent 设置最小工具权限和输入输出契约。

## 1. 核心术语

| 术语 | 含义 |
| --- | --- |
| Worker Agent | 负责一个专业领域或有限能力的执行者 |
| Supervisor | 读取任务状态，选择 Worker，汇总结果并决定结束 |
| Router | 一次分类后把任务发送到一个或多个专门处理器 |
| Handoff | 当前 Agent 把控制权和必要上下文转交给另一个 Agent |
| Context isolation | 每个 Agent 只接收完成职责所需的上下文 |
| Shared state | 多个节点交换任务、结果、错误和预算的数据契约 |

Supervisor 是协调角色，不应拥有所有业务工具。它的主要动作应限制为“选择 Worker、停止、请求人工处理”。

## 2. 架构选择

| 模式 | 适用场景 | 主要风险 |
| --- | --- | --- |
| 流水线 | 步骤和顺序固定 | 上游错误向下传播 |
| Router | 任务可一次分类 | 分类错误、类别遗漏 |
| Supervisor + Workers | 需要动态多步协调 | 循环、成本、单点误判 |
| 并行评审 | 需要独立观点再聚合 | 结果冲突和延迟 |
| Handoff | 对话中需要切换专业角色 | 上下文和权限随转交泄漏 |

如果只是按类型调用不同函数，Router 已足够，不要为了形式引入多 Agent。

## 3. Supervisor 工作流

~~~text
START → supervisor ─→ research_worker ─┐
          ↑                            │
          ├──── writing_worker ←───────┤
          │                            │
          └──── verify_worker ←────────┘
          │
          └─完成或达到上限 → END
~~~

Supervisor 每轮读取 completed_workers、results、errors 和 dispatch_count，返回下一个有限标签。Worker 完成后回到 Supervisor。终止条件必须独立于模型措辞。

## 4. 状态与通信契约

推荐只共享结构化结果：

~~~python
class TeamState(TypedDict):
    task: str
    completed_workers: list[str]
    results: dict[str, str]
    next_worker: str
    dispatch_count: int
    max_dispatches: int
    status: Literal["running", "completed", "failed"]
~~~

不要把全部内部推理、全部聊天记录和所有工具输出无差别广播。上下文越大，泄漏面、成本和冲突越大。

Worker 输出至少包含：

- worker 名称与任务 ID。
- 结论和必要证据。
- 错误类型及是否可重试。
- 是否需要其他 Worker 或人工输入。

## 5. 权限和边界

- 每个 Worker 只绑定完成职责所需的工具。
- 研究 Agent 不应获得发邮件、删除或支付权限。
- Supervisor 不得通过改写提示绕过工具层策略。
- 外部写入必须经过第 12 章的授权与审批。
- Worker 调用要有超时、重试次数、Token 和并发上限。
- 达到 max_dispatches 后明确失败或转人工，不能继续派发。

## 6. 关键示例

[supervisor_workflow.py](./examples/supervisor_workflow.py) 使用确定性 Supervisor 协调 research、write、verify 三个 Worker，展示结构化共享状态、最小职责和最大派发次数。

~~~bash
python examples/supervisor_workflow.py
~~~

替换为模型 Supervisor 时，应让模型输出 next_worker 枚举，并在代码中校验；模型不能返回任意节点名。

## 7. 常见错误

1. 多个 Agent 使用相同提示和工具，只是改了名字。
2. Supervisor 能调用全部高风险工具，破坏权限隔离。
3. Worker 互相发送自然语言全文，状态持续膨胀。
4. 没有派发上限，两个 Worker 互相转交。
5. 聚合器无法处理冲突，却默认最后一个结果正确。
6. 把并发当并行安全；共享字段没有 reducer 或冲突策略。

## 8. 测试与验收

至少测试：

- 每类任务路由到正确 Worker。
- 未知路由标签被拒绝。
- Worker 失败时有限重试或转人工。
- 达到 max_dispatches 后停止。
- 未授权 Worker 无法调用高风险工具。
- 结果冲突时不会静默覆盖。

练习：

1. 让 verify Worker 驳回缺少证据的写作结果。
2. 模拟 research Worker 超时并进入失败路径。
3. 给每个 Worker 增加 allowed_tools，并写越权测试。

## 9. 本章小结

多 Agent 的核心不是数量，而是边界。Supervisor 负责有限路由，Worker 负责专业执行，共享状态负责传递可验证结果。只有在职责、上下文、权限和终止条件都清晰时，多 Agent 才比单 Agent 更可靠。

下一章给涉及外部状态的动作加入 interrupt、resume、人工审批和权限控制。

