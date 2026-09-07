# 03 大模型 API 与消息模型

本章直接使用 OpenAI Python SDK 调用 **OpenAI 兼容 API**，重点不是背某个厂商的方法名，而是理解请求、消息、上下文和响应之间的关系。示例把客户端创建、单轮调用、多轮状态和流式输出分开，便于替换服务商并进行离线测试。

## 学习目标

完成本章后，你应当能够：

1. 解释 HTTP API、Endpoint、Base URL、API Key 和 JSON；
2. 正确使用 system、user、assistant、tool 消息；
3. 使用环境变量创建 OpenAI 兼容客户端；
4. 完成单轮、多轮和流式调用；
5. 解释为什么 API 本身通常是无状态的；
6. 处理超时、认证失败、限流和服务端错误；
7. 使用假客户端在不消耗 Token 的情况下测试请求构造。

## 1. 术语解释

| 术语 | 解释 | 示例 |
| --- | --- | --- |
| API | 程序之间约定好的调用接口 | Python 程序请求模型服务 |
| HTTP | Web 上常用的请求/响应协议 | `POST /v1/chat/completions` |
| Endpoint | 某项具体能力的请求地址 | 聊天补全接口 |
| Base URL | 一组接口共享的地址前缀 | `https://provider.example/v1` |
| API Key | 服务端识别调用者身份的凭据 | 通过环境变量注入 |
| JSON | 跨语言传输结构化数据的文本格式 | 消息数组和模型参数 |
| Request | 客户端发送的模型、消息和参数 | `model`、`messages` |
| Response | 服务端返回的文本、用量或错误 | `choices[0].message.content` |
| Message | 带角色的对话单元 | `{"role": "user", ...}` |
| Stateless | 服务端不自动记住上一次独立请求 | 多轮历史要由客户端再次发送 |
| Streaming | 响应生成一部分就返回一部分 | 降低看到首个字符的等待时间 |
| Rate Limit | 服务端限制单位时间或单位额度的请求 | 常表现为 HTTP 429 |
| Timeout | 等待连接或响应的最长时间 | 防止请求永久挂起 |
| Retry | 发生暂时性错误后重新尝试 | 适合限流或部分 5xx，不适合所有错误 |

## 2. 一次请求的原理：发生了什么

```text
Python 应用
  │  1. 构造 model + messages
  │  2. 使用 API Key 发起 HTTPS 请求
  ▼
模型服务
  │  3. 校验身份、额度与参数
  │  4. 把消息编码为 Token 并推理
  ▼
Python 应用
     5. 接收文本、结束原因、用量或错误
```

SDK 帮我们完成 HTTP、认证头、JSON 序列化和响应对象转换，但请求的本质没有改变。理解这一点有助于排查“SDK 报错”和“服务商不兼容”。

## 3. 消息模型

### 3.1 system

定义本次对话的总体行为、边界和输出要求。

```python
{"role": "system", "content": "你是技术助教；不知道时明确说明。"}
```

System 消息不是绝对安全边界。权限校验、数据访问控制等必须由应用代码执行。

### 3.2 user

表示用户输入。用户内容是不可信输入，可能包含错误信息或提示注入指令。

```python
{"role": "user", "content": "请解释上下文窗口。"}
```

### 3.3 assistant

表示模型之前的回答。多轮对话中，客户端把历史 assistant 消息与新的 user 消息一起发送。

```python
{"role": "assistant", "content": "上下文窗口是……"}
```

### 3.4 tool

表示宿主程序执行工具后返回给模型的结果，通常需要与模型提出的某个工具调用 ID 对应。工具调用将在第 06 模块完整实现。

### 3.5 多轮对话为何要重发历史

多数聊天 API 对独立请求是无状态的：

```text
请求 1：[system, user-1]
响应 1：assistant-1

请求 2：[system, user-1, assistant-1, user-2]
响应 2：assistant-2
```

如果请求 2 只发送 `user-2`，模型通常不知道请求 1 的内容。历史越长，Token、费用和延迟也越高，因此真实系统会做截断、摘要、检索或持久化。

## 4. 配置与客户端

项目根目录 `.env` 使用：

```dotenv
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://provider.example/v1
LLM_MODEL=provider-model-name
REQUEST_TIMEOUT=60
```

`OPENAI_BASE_URL` 留空时使用 SDK 默认地址；使用兼容服务商时，按服务商文档填写。不要凭经验随意追加或删除 `/v1`。

本章 `client_factory.py` 会：

- 检查 API Key 和模型名；
- 校验超时范围；
- 仅在配置了 Base URL 时传入该参数；
- 为暂时性网络错误启用有限次数重试；
- 从不打印密钥。

## 5. 递进示例

目录结构：

```text
examples/
├── client_factory.py
├── single_turn.py
├── conversation.py
├── streaming_chat.py
└── test_api_examples.py
```

先从 `AI-agent` 根目录准备 `.env`，再进入示例目录。

### 示例 1：单轮调用

```powershell
python 03_大模型API与消息模型\examples\single_turn.py "用一句话解释 Agent"
```

核心代码：

```python
response = client.chat.completions.create(
    model=config.model,
    messages=[
        {"role": "system", "content": "你是严谨的技术助教。"},
        {"role": "user", "content": question},
    ],
)
answer = response.choices[0].message.content
```

不要假设 `content` 一定存在。服务端可能返回空选择、拒绝、工具调用或不兼容格式，程序应显式检查。

### 示例 2：多轮对话

```powershell
python 03_大模型API与消息模型\examples\conversation.py
```

`Conversation` 在内存中维护消息列表。只有模型请求成功后才把 assistant 回复加入历史，避免失败响应污染状态。

这只是教学版短期状态，尚未包括：

- Token 预算与历史裁剪；
- 数据库存储；
- 多用户隔离；
- 敏感信息清理；
- 会话并发控制。

### 示例 3：流式输出

```powershell
python 03_大模型API与消息模型\examples\streaming_chat.py "列出三个 Agent 风险"
```

流式响应不是一次返回完整字符串，而是一系列事件或块。某些块的文本可能是 `None` 或空字符串，必须跳过。

### 示例 4：离线测试请求结构

```powershell
cd 03_大模型API与消息模型\examples
python -m pytest test_api_examples.py -q
```

测试使用假客户端记录 `create()` 的参数，不连接网络、不需要真实密钥，也不会产生费用。

## 6. 生成参数

不同服务商支持的参数可能不同，常见参数包括：

| 参数 | 作用 | 建议 |
| --- | --- | --- |
| `model` | 选择服务商提供的模型 | 始终通过 `LLM_MODEL` 配置 |
| `temperature` | 调整随机性 | 信息抽取通常较低，创作可适当提高 |
| `max_completion_tokens` | 限制最大输出 Token | 兼容服务商可能使用其他名称 |
| `stop` | 命中指定序列时停止 | 不要把它当作可靠的 JSON 校验 |
| `stream` | 是否流式返回 | 流式需要不同的响应处理方式 |

参数不是越多越专业。先使用服务商确认支持的最小参数集，再逐项加入并测试。

## 7. 错误处理策略

### 7.1 认证错误（401/403）

检查密钥、Base URL、账户权限和模型访问权限。更换重试次数通常没有意义。

### 7.2 参数或模型错误（400/404）

检查模型名、消息格式、接口路径和服务商兼容范围。不要无限重试确定性错误。

### 7.3 限流（429）

使用指数退避、随机抖动和并发限制；同时检查账户额度。重试必须有上限。

### 7.4 服务端错误（5xx）与网络超时

可以有限重试，但要记录请求 ID、耗时和错误类型。对有副作用的外部操作还要考虑幂等性，避免重试造成重复执行。

### 7.5 响应结构不符合预期

兼容 API 不代表所有细节完全一致。对空 `choices`、空 `content`、不支持参数和流式块差异给出明确错误。

## 8. 常见错误

### 错误 1：硬编码模型名和密钥

模型名属于部署配置，密钥属于 Secret。二者都不应散落在示例函数中。

### 错误 2：每次提问都新建空消息列表

这样不会形成多轮上下文。应由会话对象保存历史，并设置预算和清理策略。

### 错误 3：把流式迭代器当成普通响应

`stream=True` 返回的是可迭代数据流，需要逐块处理，不能直接读取完整 `response.choices[0]`。

### 错误 4：打印整个响应或请求头到日志

调试日志可能包含用户敏感内容、密钥或内部提示。生产环境要做字段白名单和脱敏。

### 错误 5：对所有异常无限重试

认证错误和无效参数不会因重试自动修复。重试只适合暂时性错误，并且必须有次数与总时限。

### 错误 6：认为 temperature=0 就完全确定

模型服务、硬件、版本和并发实现仍可能造成差异。需要稳定格式时应使用结构化输出和程序校验。

## 9. 练习

1. 在单轮示例中加入可配置的 system 消息，但不要将其与用户输入拼成一个字符串；
2. 为 `Conversation` 增加 `reset()`，并为它写离线测试；
3. 限制历史最多保留最近 6 条消息，思考 system 消息应如何处理；
4. 让流式示例同时累计完整文本，流结束后打印字符数；
5. 使用假响应模拟空 `choices`，验证程序返回清晰错误；
6. 查阅你实际服务商的文档，记录其模型名、Base URL 和不兼容参数。

## 10. 小结

- SDK 是 HTTP/JSON 调用的封装，Base URL、认证、请求和响应仍是排错核心；
- 消息角色表达对话结构，但 system 消息不能代替程序权限控制；
- 多轮历史通常由客户端维护并随请求再次发送；
- 流式输出降低首字等待时间，但需要逐块处理；
- 配置集中、失败显式、有限重试和离线测试是可靠调用的起点；
- 下一章会把自由文本输出升级为可校验的结构化数据。
