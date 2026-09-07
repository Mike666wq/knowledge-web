# 05 LangChain 核心抽象

> 本章解决一个核心问题：LangChain 的 `|`、`invoke` 和各种 `Runnable` 到底在抽象什么。先用纯 Python 实现同样的数据流，再使用 LCEL 重写，避免把框架 API 当作魔法。

## 学习目标

完成本章后，你应该能够：

- 区分模型、Prompt、解析器、Runnable 与 Chain 的职责。
- 解释 LCEL 管道中每一步的输入类型和输出类型。
- 使用 `invoke`、`batch`、`stream` 与对应的异步接口。
- 使用 `RunnableLambda`、`RunnablePassthrough`、`RunnableParallel` 组合数据流。
- 为链增加配置、重试、降级和异常边界。
- 判断何时用普通 Python 函数，何时用 LangChain Runnable。

## 1. 术语

| 术语 | 含义 |
| --- | --- |
| Component（组件） | 完成单一职责的对象，例如 Prompt、模型、解析器或检索器。 |
| Chain（链） | 多个组件按照确定顺序组成的数据处理流程。链本身不等于 Agent，因为它通常不自主选择下一步。 |
| Runnable | LangChain 对“可执行组件”的统一协议。不同组件因此共享调用、批处理、流式和组合接口。 |
| LCEL | LangChain Expression Language，用 `|` 表达顺序组合，用字典表达并行/字段映射。 |
| Schema（模式） | 输入或输出的数据结构契约，例如 `dict[str, str]` 或 Pydantic 模型。 |
| Adapter（适配器） | 在两个组件之间转换数据形状的步骤。 |
| Parser（解析器） | 把模型消息转换为字符串、JSON 或业务对象的组件。 |
| Batch（批处理） | 对一组独立输入执行同一 Runnable。它不等于模型服务一定会原生批推理。 |
| Stream（流式） | 逐块产出中间或最终结果，而不是等全部结束后一次返回。 |
| Fallback（降级） | 主步骤失败时切换到备用实现。 |

## 2. 核心原理：链就是带契约的函数组合

纯 Python 中，下面三个函数已经是一条链：

```python
def build_prompt(data: dict[str, str]) -> str:
    return f"请把下列文本压缩为一句话：{data['text']}"

def call_model(prompt: str) -> str:
    return "模拟模型输出"

def parse_output(message: str) -> str:
    return message.strip()


result = parse_output(call_model(build_prompt({"text": "很长的正文"})))
```

它的数据流是：

```text
dict[str, str] -> str -> str -> str
```

框架的价值不在于替代函数，而在于让不同组件遵守统一协议，并统一提供批处理、异步、流式、回调、追踪和配置传递。无论是否使用框架，最重要的问题始终是：

1. 当前步骤接收什么类型？
2. 当前步骤返回什么类型？
3. 下一步能否直接消费该类型？
4. 失败时由谁处理？

完整纯 Python 实现见 [examples/01_python_pipeline.py](examples/01_python_pipeline.py)。

## 3. Runnable 协议

常用同步接口：

| 接口 | 用途 | 典型返回 |
| --- | --- | --- |
| `invoke(input)` | 单次调用 | 一个结果 |
| `batch(inputs)` | 一组独立输入 | 与输入顺序对应的结果列表 |
| `stream(input)` | 流式调用 | 结果块迭代器 |

对应异步接口为 `ainvoke`、`abatch`、`astream`。异步的价值主要来自 I/O 并发；如果底层工作是阻塞 CPU 计算，仅把函数改成 `async` 并不会自动提速。

### 3.1 `|` 的准确含义

```python
chain = step_a | step_b | step_c
```

表示 `step_a` 的输出成为 `step_b` 的输入，`step_b` 的输出再成为 `step_c` 的输入。它通常构造一个 `RunnableSequence`，并不在定义时执行。

最常见错误是数据形状不匹配：

```python
# translate 输出 str，但 summary_prompt 需要 {"text": ...}
broken = translate | summary_prompt

# 使用适配器修正
fixed = translate | RunnableLambda(lambda text: {"text": text}) | summary_prompt
```

不要只看变量名推测类型。调试时应在边界打印或断言实际值，也可以为关键输入输出定义 Pydantic 模型。

## 4. 五个核心组合件

### 4.1 `RunnableLambda`

把普通函数纳入 Runnable 数据流：

```python
from langchain_core.runnables import RunnableLambda

normalize = RunnableLambda(lambda text: text.strip().lower())
```

适合轻量转换、校验和格式化。复杂业务逻辑应保留为有名称、可单测的普通函数，再交给 `RunnableLambda` 包装。

### 4.2 `RunnablePassthrough`

原样传递输入，常用于保留原问题：

```python
from langchain_core.runnables import RunnablePassthrough

prepare = {
    "question": RunnablePassthrough(),
    "context": retriever,
}
```

调用 `prepare.invoke("什么是 RAG？")` 时，两个分支都收到同一个字符串。结果是一个包含 `question` 和 `context` 的字典。

### 4.3 `RunnableParallel`

对同一输入执行多个独立分支，并将结果合并为字典：

```python
from langchain_core.runnables import RunnableLambda, RunnableParallel

analyze = RunnableParallel(
    length=RunnableLambda(len),
    upper=RunnableLambda(str.upper),
)
```

“并行”描述的是可并发的数据依赖关系。是否真正并发、并发上限多大，还取决于调用方式、执行器和下游服务。

### 4.4 Prompt 与消息

`ChatPromptTemplate` 把业务输入转换为模型消息列表。它不调用模型：

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是严谨的技术编辑。"),
    ("human", "请总结：{text}"),
])
```

### 4.5 输出解析器

聊天模型通常返回 `AIMessage`，业务层往往需要字符串或结构化对象：

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | model | StrOutputParser()
```

解析器只能校验和转换模型已经返回的内容。若业务要求强类型输出，优先使用模型支持的结构化输出能力，并在应用边界继续做 Pydantic 校验。

## 5. 串行、并行与分支如何选择

| 关系 | 选择 | 示例 |
| --- | --- | --- |
| B 依赖 A 的结果 | 串行 `A | B` | 翻译后再总结 |
| B、C 只依赖同一原始输入 | `RunnableParallel` | 同时做分类和摘要 |
| 根据确定规则二选一 | `RunnableBranch` 或普通函数 | 按文件类型选择解析器 |
| 下一步由模型动态决定 | Agent/图工作流 | 模型决定是否调用工具 |

固定业务规则不要交给模型“猜”。确定性流程用 Chain 或图；只有确实需要动态决策时才升级为 Agent。

## 6. 配置、超时、重试与降级

### 6.1 配置不是业务输入

`config` 可携带运行名、标签、元数据、回调和并发限制，不应把它和 Prompt 变量混为一谈：

```python
result = chain.invoke(
    {"text": "待总结内容"},
    config={
        "run_name": "summary_chain",
        "tags": ["tutorial"],
        "metadata": {"tenant": "demo"},
    },
)
```

### 6.2 重试只处理瞬时故障

网络抖动、限流和临时服务异常可以有限重试；参数错误、权限错误和确定性解析错误不应盲目重试。重试必须具备：

- 最大次数。
- 指数退避或服务端建议的等待时间。
- 可重试异常白名单。
- 幂等性判断，尤其是写操作。

### 6.3 降级不等于吞掉错误

备用模型、缓存结果或模板化答复都可以是降级策略，但结果中应保留降级标记，日志中应记录原始异常。不要用空字符串伪装成功。

### 6.4 超时应在真正的 I/O 边界设置

Runnable 的外层限制不能替代 HTTP 客户端、数据库驱动和工具函数自身的超时。生产系统应在每个外部依赖上设置连接和读取超时，并在更外层设置总任务预算。

## 7. 完整示例

### 7.1 纯 Python 数据流水线

[examples/01_python_pipeline.py](examples/01_python_pipeline.py) 实现：

- 显式输入输出类型。
- 可组合的 `Pipeline`。
- 步骤级异常包装。
- 批处理时选择“立即失败”或“收集异常”。
- 无网络、无第三方依赖，可直接运行。

```bash
python 05_LangChain核心抽象/examples/01_python_pipeline.py
```

### 7.2 LCEL 工单分析流水线

[examples/02_lcel_pipeline.py](examples/02_lcel_pipeline.py) 使用 LangChain Core 完成字段校验、并行分析、字段汇总和批处理。示例使用确定性函数，因此不需要 API Key：

```bash
python 05_LangChain核心抽象/examples/02_lcel_pipeline.py
```

它刻意不调用真实模型，便于先观察 LCEL 的数据流；将其中某个 `RunnableLambda` 替换为 `prompt | ChatOpenAI(...) | parser`，其余结构无需改变。

## 8. 常见错误

### 错误 1：把 Chain 当 Agent

链只是预先定义的数据流。它不会因为结果不好而自行决定重新检索，也不会自行选择工具。

### 错误 2：Prompt 需要字典，上一环却返回字符串

在边界增加有名称的适配函数，并为输入做校验。不要堆叠难读的匿名 `lambda`。

### 错误 3：以为 `batch` 一定比循环便宜

`batch` 可能并发调用多次远端 API，费用通常仍按每次请求计算，还可能触发限流。使用 `config={"max_concurrency": N}` 控制并发。

### 错误 4：流式输出后又做必须看完整文本的解析

后置解析器可能需要缓存全部上游结果，导致用户看不到真正的逐 token 流。设计流式链时要明确哪一步能增量处理。

### 错误 5：在 `RunnableLambda` 中隐藏大量副作用

数据库写入、付款和文件删除等副作用需要显式函数、审计、权限与幂等设计；不要把它们伪装成一个轻量转换步骤。

### 错误 6：捕获所有异常后返回“成功”

异常应该分类：可重试、可降级、需要用户修正、系统故障。错误结果也应有明确结构。

## 9. 练习

1. 为纯 Python `Pipeline` 增加步骤耗时统计，并保持业务函数不感知监控逻辑。
2. 在 LCEL 示例中新增 `risk` 分支，与 `category`、`summary` 并行执行。
3. 故意让一个批处理输入缺少 `text`，分别观察立即失败和收集异常两种策略。
4. 写出一个适配器，把 `AIMessage` 转换为 `{"answer": str, "usage": dict}`。
5. 设计一个主链和备用链：主链失败时返回模板化结果，同时保留 `degraded=True`。
6. 画出你自己项目中一条链的每一步输入/输出类型；若存在 `Any`，说明为什么无法进一步收紧。

## 10. 小结

- LangChain 的核心不是管道符，而是统一的 Runnable 契约。
- Chain 适合确定性数据流；Agent 适合模型参与下一步决策的循环。
- 组合前先写清每一步的输入、输出和异常边界。
- 并行只用于没有数据依赖的分支，批处理仍需控制限流与成本。
- 框架负责组合能力，业务正确性仍依赖校验、超时、重试和测试。

下一章将在这些抽象之上构建工具调用循环，并解释 Agent 为什么必须有明确终止条件。

## 参考资料

- [LangChain Runnable API](https://python.langchain.com/api_reference/core/runnables.html)
- [LangChain Models](https://docs.langchain.com/oss/python/langchain/models)
- [LangChain 原课程参考：05～08](../../ai-agent-dev/ai-agent/模块三_LangChain核心组件/README.md)
