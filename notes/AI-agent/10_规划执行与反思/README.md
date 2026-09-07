# 10 规划、执行与反思

## 本章定位

复杂目标不能总靠一次模型调用完成。常见做法是把职责拆为 Planner、Executor、Reviewer：规划器产出有限步骤，执行器逐步工作，审查器判断接受、修改还是失败。三者是角色，不一定是三个模型进程。

## 学习目标

1. 解释 Planner、Executor、Reviewer 及计划状态。
2. 用 LangGraph 表达“计划 → 执行 → 审查 → 有限修订”。
3. 给计划长度、执行次数和审查轮数设置上限。
4. 区分可验证反馈与空泛的“再想一遍”。

## 1. 术语与职责

| 角色 | 输入 | 输出 | 不应承担 |
| --- | --- | --- | --- |
| Planner | 目标、约束、已有信息 | 有序、有限、可执行的步骤 | 直接修改外部系统 |
| Executor | 当前步骤、允许的工具 | 结果、证据、错误 | 任意扩张目标 |
| Reviewer | 目标、计划、结果、标准 | accept、revise 或 fail | 无限要求重写 |
| Replan | 失败证据与剩余预算 | 调整后的剩余步骤 | 丢弃全部执行历史 |

反思（reflection）不是让模型自由地“再思考”，而是针对明确标准检查缺口，并输出可执行反馈。

## 2. 状态设计

最小状态通常包含：

~~~python
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
~~~

计划与执行游标分开保存，恢复时才能知道哪些步骤已经完成。结果应带步骤编号或稳定 ID，防止重新规划后错位。

## 3. 工作流

~~~text
START → planner → executor ──还有步骤──→ executor
                         │
                         └─执行完成──→ reviewer
                                          │
                    accept → END ← fail   │
                                          └─revise → planner
~~~

节点边界：

- Planner 只创建或调整计划。
- Executor 每次只执行一个步骤，然后增加 current_step。
- Reviewer 使用验收标准做有限决策。
- 路由函数只读状态，不执行工具。

## 4. 三层终止保护

1. 计划长度不得超过 max_steps；超长计划在执行前拒绝或裁剪。
2. revision_count 不得超过 max_revisions。
3. graph.invoke 设置 recursion_limit，防止图设计错误造成无限推进。

此外，还应限制单工具超时、总 Token、总费用与截止时间。达到预算时返回 failed 和原因，不生成貌似成功的答案。

## 5. 规划质量

合格步骤应：

- 与目标直接相关。
- 有清楚的完成条件。
- 粒度足够小但不碎片化。
- 依赖顺序明确。
- 只使用 Executor 被授权的工具。

模型生成计划时，推荐使用结构化输出并由 Pydantic 验证长度、字段和枚举。教程示例采用确定性规则，便于离线运行。

## 6. 审查标准

Reviewer 至少检查：

- 完整性：所有必要步骤是否完成。
- 正确性：结果是否与证据一致。
- 约束：是否遵守权限、格式、时间和预算。
- 可追溯性：结论能否关联到步骤结果。

Reviewer 输出应是结构化的 decision、reason 和 actionable_feedback。若反馈无法转化为具体修改，不应进入下一轮。

## 7. 关键示例

[planner_executor_reviewer.py](./examples/planner_executor_reviewer.py) 实现离线可运行的 Planner–Executor–Reviewer 图，包含计划长度、修订次数与 recursion_limit 三层上限。

~~~bash
python examples/planner_executor_reviewer.py
~~~

将确定性节点替换为 LLM 时，保留相同 State、路由和上限，就能把模型的不确定性限制在受控节点中。

## 8. 常见错误

1. Planner 一次创建几十个步骤，导致成本和错误累积。
2. Executor 一次跑完整计划，checkpoint 无法细粒度恢复。
3. Reviewer 只返回“质量不够”，没有可执行反馈。
4. 修订时清空历史，重复执行已有副作用。
5. 把 Reviewer 当事实保证；高风险结论仍需规则校验或人工负责。

## 9. 练习与验收

1. 为每个步骤增加 stable step_id 与 done 状态。
2. 模拟某一步失败，让 Reviewer 只重排剩余步骤。
3. 增加总耗时预算，超时后明确失败。
4. 为 Reviewer 编写 accept、revise、fail 三条测试。

检查清单：

- [ ] 计划有限、结构化且可验证。
- [ ] Executor 每轮只处理有限工作。
- [ ] Reviewer 有明确标准与决策枚举。
- [ ] 修订、步数和图推进都有上限。
- [ ] 已完成步骤和副作用不会被无意重放。

## 10. 本章小结

Planner 决定做什么，Executor 负责做一步，Reviewer 判断结果是否满足标准。可靠性来自清晰状态、有限计划、可执行反馈和多层终止条件，而不是增加更多“思考”轮次。

下一章把单工作流中的角色扩展为由 Supervisor 协调的多个专业 Agent。

