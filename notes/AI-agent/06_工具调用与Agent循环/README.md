# 06 工具调用与 Agent 循环

> 模型不会执行 Python 函数。它只能生成一份“希望调用哪个工具、参数是什么”的结构化请求；真正的查找、校验、执行、回传和终止都由应用程序负责。

## 学习目标

完成本章后，你应该能够：

- 解释 Tool Calling、Function Calling、ReAct 与 Agent Loop 的关系。
- 设计名称清晰、参数严格、返回稳定的工具契约。
- 不借助 Agent 框架，手写“模型 → 工具 → 模型”的完整循环。
- 使用 LangChain `@tool`、`bind_tools` 和 `ToolMessage`。
- 使用 `create_agent` 构建预置工具循环，并理解它替你做了什么。
- 处理未知工具、参数错误、工具异常、超时、重复调用和死循环。
- 为循环设计明确的成功、失败和预算终止条件。

## 1. 术语

| 术语 | 含义 |
| --- | --- |
| Tool（工具） | Agent 可调用的外部能力，通常对应一个函数、API、数据库查询或受控操作。 |
| Tool Schema | 工具名称、用途、参数类型和约束组成的接口契约。 |
| Tool Calling | 模型输出结构化工具调用意图，由宿主程序执行工具。 |
| Function Calling | 常被用作 Tool Calling 的旧称或供应商术语；本质仍是模型生成函数名和参数。 |
| Tool Call ID | 一次工具请求的唯一标识；工具结果必须用它与请求配对。 |
| Observation | 工具执行后返回给模型的结果，也包括受控的错误信息。 |
| ReAct | Reason + Act 范式：模型依据已有上下文选择行动，读取观察结果，再决定下一步。应用无需向用户暴露模型的内部思维。 |
| Agent Loop | 重复执行“调用模型—执行工具—回传结果”，直到模型直接回答或命中终止条件。 |
| Idempotency（幂等） | 相同请求重复执行不会造成额外副作用。查询通常较易幂等，付款等写操作需要幂等键。 |
| Step Budget | 一次任务允许的最大模型/工具循环步数。 |

## 2. 核心原理：模型返回意图，应用执行工具

绑定工具后，模型收到的是工具描述和 JSON Schema。它可能返回普通文本，也可能返回类似结构：

```json
{
  "id": "call_123",
  "name": "get_weather",
  "args": {"city": "北京"}
}
```

这不是函数执行结果。宿主程序还要：

1. 检查工具是否在白名单中。
2. 校验参数类型、长度、范围和权限。
3. 执行工具，并设置工具自己的超时。
4. 将返回值序列化为模型可理解的内容。
5. 用相同 `tool_call_id` 创建工具消息。
6. 再次调用模型，让它决定继续调用还是给出最终答复。

完整数据流：

```text
用户消息
  ↓
模型（绑定工具 Schema）
  ├─ 没有 tool_calls ─────────────→ 最终答复
  └─ 一个或多个 tool_calls
              ↓
      白名单、参数、权限校验
              ↓
          执行工具
              ↓
     ToolMessage / Observation
              └───────────────→ 回到模型
```

## 3. 工具契约设计

### 3.1 名称与描述

模型主要依赖名称、描述和参数 Schema 选工具：

```python
from langchain.tools import tool


@tool
def get_order_status(order_id: str) -> dict:
    """查询一个订单的当前状态；仅用于读取，不会修改订单。"""
    ...
```

描述应说明“什么时候用”和“不会做什么”。不要写“处理订单”这类含糊描述。

### 3.2 参数约束

类型注解是最低要求；关键工具应使用 Pydantic 约束长度、枚举和数值范围。即使 Schema 已发送给模型，服务端仍必须重新校验——模型输出永远是不可信输入。

### 3.3 返回值

优先返回短小、稳定的结构：

```python
{"ok": True, "order_id": "A100", "status": "shipped"}
```

不要把巨大的数据库对象、HTML 页面或堆栈直接塞回上下文。对错误返回安全、可行动的信息；详细堆栈只写服务端日志。

### 3.4 读工具与写工具分离

`get_order` 和 `cancel_order` 应是两个工具。写工具通常还需要：

- 明确的用户身份和授权检查。
- 参数白名单。
- 人工确认或策略审批。
- 幂等键。
- 审计日志。
- 可回滚或补偿方案。

模型“选择了工具”不等于用户“授权了操作”。

## 4. ReAct 与工具调用

经典 ReAct 把推理与行动交替组织：

```text
问题 → 选择行动 → 工具观察 → 再选择行动 → 最终答案
```

现代 Tool Calling 通常用结构化消息表达“行动”和“观察”，比让模型输出 `Action:` 文本更可靠。工程上应记录可审计的外部轨迹：

- 收到的用户任务。
- 模型提出的工具名和参数。
- 参数校验结果。
- 工具状态、耗时和摘要。
- 终止原因。

不应要求或存储模型的私有思维过程。调试 Agent 的重点是可观察的调用轨迹和状态变化。

## 5. 纯 Python Agent 循环

框架之外的最小循环如下：

```python
for step in range(max_steps):
    decision = model(messages, tool_schemas)
    messages.append(decision)

    if not decision.tool_calls:
        return decision.content

    for call in decision.tool_calls:
        observation = execute_safely(call)
        messages.append(observation)

raise StepLimitExceeded(max_steps)
```

这个循环至少要回答六个问题：

1. 一轮允许多个工具并行吗？
2. 工具失败后把错误交给模型重试，还是直接失败？
3. 同一调用连续重复几次视为死循环？
4. 最大步数、总耗时和 Token 预算是多少？
5. 哪些操作必须人工确认？
6. 最终答案为空时是否算成功？

[examples/01_python_tool_loop.py](examples/01_python_tool_loop.py) 用一个可预测的模拟模型完整演示两次工具调用和最终答复，不需要 API Key。

## 6. LangChain 手动工具循环

### 6.1 定义并绑定工具

```python
from langchain.tools import tool
from langchain_openai import ChatOpenAI


@tool
def get_weather(city: str) -> dict:
    """查询指定城市的模拟天气，只读。"""
    return {"city": city, "temperature_c": 26.5}


model = ChatOpenAI(model="your-model", timeout=30, max_retries=2)
model_with_tools = model.bind_tools([get_weather])
```

`bind_tools` 只是把工具 Schema 交给模型并让返回消息能携带 `tool_calls`，它不会自动执行函数。

### 6.2 回传 `ToolMessage`

```python
from langchain_core.messages import ToolMessage

tool_message = ToolMessage(
    content='{"ok": true, "temperature_c": 26.5}',
    tool_call_id=call["id"],
    name=call["name"],
)
```

一个 `AIMessage` 若包含多个工具调用，每个调用都必须有对应结果。遗漏、错配 ID 或改变消息顺序，都会使部分模型提供商拒绝请求。

完整实现见 [examples/02_langchain_tool_loop.py](examples/02_langchain_tool_loop.py)。运行前设置项目根目录 `.env`：

```bash
python 06_工具调用与Agent循环/examples/02_langchain_tool_loop.py
```

## 7. 使用 `create_agent`

LangChain 1.x 的 `create_agent` 会构建一个基于 LangGraph 的工具循环，负责消息累积、工具调度和循环路由：

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="只在需要外部数据时调用工具。",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "北京的模拟天气如何？"}]},
    config={"recursion_limit": 12},
)
```

`recursion_limit` 是图执行的安全上限，不等同于精确的“工具调用次数”。应用仍应设置总耗时、调用次数、费用和副作用预算。

[examples/03_create_agent.py](examples/03_create_agent.py) 给出可运行示例。学习时先掌握手动循环，再使用预置 Agent，才能在出错时知道问题发生在模型、消息协议、工具还是图循环。

## 8. 终止条件

只判断“模型没有工具调用”不够。推荐至少包含：

| 条件 | 终止类型 | 处理 |
| --- | --- | --- |
| 模型返回非空最终答复 | 成功 | 返回答案和轨迹摘要 |
| 达到最大步数 | 预算失败 | 返回明确错误，可附已完成步骤 |
| 达到总耗时/费用上限 | 预算失败 | 停止发起新调用 |
| 连续重复相同工具和参数 | 循环失败 | 中止或只允许一次纠错 |
| 未知工具或越权工具 | 安全失败 | 拒绝执行并记录审计 |
| 参数多次校验失败 | 输入失败 | 要求用户澄清，不继续猜测 |
| 必需工具不可用 | 依赖失败 | 降级或告知暂不可完成 |
| 用户取消 | 取消 | 停止新步骤，安全清理资源 |

终止结果应是结构化状态，例如 `completed`、`needs_input`、`blocked`、`budget_exceeded`，而不是全部伪装成自然语言“完成了”。

## 9. 异常处理策略

### 9.1 参数错误

将简短的字段错误作为 Observation 返回，允许模型最多修正一次；反复错误则请求用户澄清。

### 9.2 工具业务错误

“订单不存在”是可预期业务结果，不应抛系统异常。返回 `{"ok": false, "code": "NOT_FOUND"}`。

### 9.3 瞬时依赖错误

网络超时或 503 可有限重试。写操作只有在幂等性得到保证时才能自动重试。

### 9.4 编程错误

`TypeError`、空指针和不变量被破坏通常应记录详细日志并终止，不要让模型无限尝试修复服务端 Bug。

### 9.5 超时

HTTP 工具应在 HTTP 客户端设置连接/读取超时；数据库工具应在驱动或查询层设置超时。外层 Future 超时通常不能强制终止已经运行的线程，因此不能替代底层超时和取消机制。

## 10. 安全边界

- 工具注册表采用白名单，不允许模型传入任意 Python 函数名。
- 禁止直接 `eval` 模型生成的表达式；计算器应解析有限语法树。
- 文件工具限制根目录并解析规范路径，防止 `../` 越界。
- SQL 工具使用参数化查询和只读账号，限制结果行数。
- 网络工具限制协议、域名、重定向和响应大小，防范 SSRF。
- 敏感参数不回显到模型消息或日志。
- 高风险写操作必须有授权、确认、审计和幂等保护。

## 11. 完整示例运行

```bash
# 无第三方依赖、无网络
python 06_工具调用与Agent循环/examples/01_python_tool_loop.py

# 需要项目依赖、模型配置和可能产生费用的 API 调用
python 06_工具调用与Agent循环/examples/02_langchain_tool_loop.py
python 06_工具调用与Agent循环/examples/03_create_agent.py
```

## 12. 常见错误

### 错误 1：调用 `bind_tools` 后认为工具会自动执行

`bind_tools` 只处理模型协议。要么手写循环，要么使用 `create_agent` / `ToolNode`。

### 错误 2：只执行第一个 `tool_call`

模型可能在一条消息中请求多个工具。必须逐个配对结果；是否并行要根据副作用和依赖关系决定。

### 错误 3：工具描述写成实现细节

模型需要知道用途、适用场景和参数含义，而不是函数内部用了哪个 HTTP 库。

### 错误 4：把异常堆栈原样返回模型

这会泄露路径、SQL、密钥或内部实现。模型只需要安全错误码和可纠正信息。

### 错误 5：没有循环预算

任何 Agent 循环都可能重复调用、增加费用或持续产生副作用。必须有步数和总预算上限。

### 错误 6：让模型决定权限

权限必须由确定性代码根据已认证身份判断，不能依赖 Prompt 指示模型“不要越权”。

## 13. 练习

1. 为纯 Python 示例增加 `divide` 工具，并分别测试除零和参数缺失。
2. 为手动 LangChain 循环增加重复调用检测：相同 `name + args` 连续两次即终止。
3. 设计一个 `cancel_order` 工具的 Pydantic 参数模型，加入原因长度和订单号格式校验。
4. 将两个只读工具并行执行，但保持两个写工具串行；说明你的判断依据。
5. 为工具返回定义统一的 `ToolResult`：`ok`、`data`、`error_code`、`retryable`。
6. 模拟模型一直请求同一工具，验证步数上限确实生效。
7. 为高风险工具增加“待审批”状态，而不是直接执行。

## 14. 小结

- Tool Calling 是结构化请求协议，不是模型直接执行函数。
- ReAct 的工程实现是可观察的“行动—观察”循环，无需暴露私有思维过程。
- 工具 Schema、服务端校验、权限与返回结构共同构成工具契约。
- 手写循环有助于理解消息配对；`create_agent` 负责通用编排，但不会替你完成业务安全设计。
- Agent 必须同时具备成功、失败、预算、安全和用户取消等终止条件。

下一章会把“检索知识”实现成固定 RAG 流程，并比较固定检索链与 Agentic RAG。

## 参考资料

- [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [原课程参考：09 工具定义](../../ai-agent-dev/ai-agent/模块四_工具定义与工具调用/09_工具定义.md)
- [原课程参考：10 工具调用](../../ai-agent-dev/ai-agent/模块四_工具定义与工具调用/10_工具调用.md)
