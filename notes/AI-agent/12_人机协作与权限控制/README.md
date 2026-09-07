# 12 人机协作与权限控制

## 本章定位

模型可以提出动作，但不能自行获得权限。涉及发送、删除、支付、发布、账号变更或敏感数据访问时，应由确定性策略先做授权，再用 LangGraph interrupt 暂停并让合适的人审批，最后才执行副作用。

## 学习目标

1. 解释 interrupt、Command(resume=...)、checkpoint 和 thread_id 的关系。
2. 实现“授权 → 审批 → 执行或拒绝”的可恢复流程。
3. 理解最小权限、默认拒绝、允许列表、审计与幂等。
4. 避免恢复时重复副作用和越权审批。

## 1. 核心术语

| 术语 | 含义 |
| --- | --- |
| Human-in-the-loop | 在关键决策点由人补充、修改、批准或拒绝 |
| interrupt | 在节点中暂停执行，并向调用方暴露可序列化载荷 |
| resume | 用 Command 把人工输入送回原 interrupt |
| Authorization | 判断主体是否有权对资源执行动作 |
| Approval | 有权审批的人是否同意本次具体动作 |
| Least privilege | 只授予完成职责所需的最小权限 |
| Deny by default | 未明确允许的动作一律拒绝 |
| Audit log | 记录谁在何时对什么动作做了什么决定 |
| Idempotency | 同一动作重复执行不会造成重复副作用 |

授权与审批不是一回事：无权操作不能靠一次“同意”变成有权；有操作权限也不代表高风险动作无需审批。

## 2. interrupt / resume 的执行过程

~~~text
首次 invoke
  → 节点调用 interrupt(payload)
  → checkpointer 保存状态
  → 返回 __interrupt__

同一 thread_id 再次 invoke(Command(resume=value))
  → 恢复同一检查点
  → 节点从开头重新执行
  → interrupt 返回 value
  → 节点继续，图向后推进
~~~

必要条件：

1. 编译图时配置 checkpointer。
2. 首次调用与恢复使用同一个 thread_id。
3. interrupt 载荷和 resume 值可序列化。
4. 生产环境使用持久化 checkpointer。

节点恢复时会从节点开头重跑，所以 interrupt 之前的代码必须无副作用或具备幂等性。不要把 interrupt 包在会吞掉其内部暂停信号的 try/except 中，也不要随意改变同一节点内多个 interrupt 的顺序。

## 3. 安全流程顺序

~~~text
输入请求
  → 参数验证
  → 身份认证
  → 授权策略（默认拒绝）
  → 风险分级
  → 必要时 interrupt 审批
  → 恢复后重新校验关键条件
  → 幂等执行
  → 审计记录
~~~

模型只负责提出候选动作和参数。权限判断、审批人匹配、资源范围、金额限制和执行开关必须由普通代码或策略引擎控制。

## 4. 审批载荷

给审批人的信息至少包括：

- action_id 与动作类型。
- 发起者、目标资源和影响范围。
- 关键参数的差异或预览。
- 风险等级与不可逆性。
- 预计成本和有效期。
- approve、reject、edit 等允许决定。

不得在载荷中暴露密钥、访问令牌或不必要的个人数据。审批决定要绑定 action_id 和内容摘要，防止审批后参数被替换。

## 5. 权限模型

教程可以从 RBAC（基于角色）开始，但生产系统通常还要检查租户、资源所有权、环境、时间、金额等属性。

~~~python
ALLOWED_ACTIONS = {
    "reader": {"read"},
    "editor": {"read", "draft"},
    "admin": {"read", "draft", "delete"},
}


def is_authorized(role: str, action: str) -> bool:
    return action in ALLOWED_ACTIONS.get(role, set())
~~~

关键原则：

- 未知角色和未知动作默认拒绝。
- 工具层再次校验，不只依赖 Prompt 或路由节点。
- 读取权限与写入权限分开。
- 开发、测试、生产环境凭据分开。
- Supervisor 或 Reviewer 也不能绕过工具策略。

## 6. 关键示例

[approval_and_permissions.py](./examples/approval_and_permissions.py) 演示：

- 确定性角色授权。
- 高风险动作触发 interrupt。
- 使用同一 thread_id 和 Command(resume=...) 恢复。
- 拒绝路径与模拟幂等执行。
- 结构化审计记录。

~~~bash
python examples/approval_and_permissions.py
~~~

示例不会真的删除数据。接入真实工具时，把幂等键写入业务数据库，并在执行瞬间重新检查权限、资源版本和审批内容。

## 7. 常见错误

1. 用 input() 阻塞服务；它不能跨进程、跨请求可靠恢复。
2. 恢复时换 thread_id，导致找不到暂停状态。
3. 在 interrupt 前发送邮件或写数据库，恢复后重复执行。
4. 把“用户说已批准”当作审批凭据。
5. 只在 Prompt 中写“不要删除”，工具层没有权限检查。
6. 审批后允许模型改变关键参数，造成所批非所执行。
7. 永久等待审批，没有过期、撤销和升级处理。

## 8. 测试与验收

至少测试：

- 未授权角色在 interrupt 前就被拒绝。
- approve 只执行一次，重复 action_id 不重复写入。
- reject 永不调用执行工具。
- 错误 thread_id 无法恢复原流程。
- 修改关键参数后旧审批失效。
- 审批超时后进入 expired 或 cancelled。

练习：

1. 增加 edit 决定，允许审批人修改非关键字段。
2. 给审批增加 expires_at，并在恢复时验证。
3. 将内存 checkpointer 换成持久化实现。
4. 用模拟工具记录调用次数，证明重试不会重复执行。

## 9. 检查清单

- [ ] 身份、授权、审批和执行职责分离。
- [ ] 默认拒绝，工具使用允许列表。
- [ ] interrupt 与 resume 使用同一 thread_id。
- [ ] interrupt 前无非幂等副作用。
- [ ] 执行时重新验证权限和关键参数。
- [ ] 审批有期限、审计和拒绝路径。
- [ ] 生产 checkpointer 持久化并隔离租户。

## 10. 本章小结

interrupt 解决“在哪里暂停并恢复”，权限策略解决“谁能做什么”，审批解决“本次是否同意”，幂等和审计解决“怎样安全执行并追责”。四者缺一不可。模型可以建议动作，但最终权限边界必须掌握在确定性代码和人类责任链中。

