# AI Agent 开发：从 0 到 1

这是一套面向 Python 开发者的系统化 Agent 教程。它以 `ai-agent-dev` 为参考，但重新组织了学习顺序、概念解释、代码示例和工程实践。

## 学习路线

| 阶段 | 模块 | 核心产出 |
| --- | --- | --- |
| 基础 | 00～04 | 理解 Agent、模型 API、消息、Prompt 与结构化输出 |
| 组件 | 05～08 | 掌握 LangChain、工具调用、RAG、状态与记忆 |
| 编排 | 09～12 | 使用 LangGraph 构建工作流、规划、多 Agent 与人机协作 |
| 工程 | 13～15 | 将 Demo 变成可测试、可观测、可控成本的服务 |
| 实战 | 16 | 完成一个知识与任务管理 Agent |

推荐顺序：

```text
00 学习指南
→ 01 Agent 与大模型基础
→ 02 Python 与项目环境
→ 03 大模型 API 与消息模型
→ 04 Prompt 与结构化输出
→ 05 LangChain 核心抽象
→ 06 工具调用与 Agent 循环
→ 07 RAG 与知识库
→ 08 状态与记忆
→ 09 LangGraph 工作流
→ 10 规划、执行与反思
→ 11 多 Agent 协作
→ 12 人机协作与权限控制
→ 13 Agent 工程化
→ 14 测试、评估与可观测性
→ 15 安全、成本与生产实践
→ 16 综合项目
```

## 章节入口

- [00 学习指南](00_学习指南/README.md)
- [01 Agent 与大模型基础](01_Agent与大模型基础/README.md)
- [02 Python 与项目环境](02_Python与项目环境/README.md)
- [03 大模型 API 与消息模型](03_大模型API与消息模型/README.md)
- [04 Prompt 与结构化输出](04_Prompt与结构化输出/README.md)
- [05 LangChain 核心抽象](05_LangChain核心抽象/README.md)
- [06 工具调用与 Agent 循环](06_工具调用与Agent循环/README.md)
- [07 RAG 与知识库](07_RAG与知识库/README.md)
- [08 Agent 状态与记忆](08_Agent状态与记忆/README.md)
- [09 LangGraph 工作流](09_LangGraph工作流/README.md)
- [10 规划、执行与反思](10_规划执行与反思/README.md)
- [11 多 Agent 协作](11_多Agent协作/README.md)
- [12 人机协作与权限控制](12_人机协作与权限控制/README.md)
- [13 Agent 工程化](13_Agent工程化/README.md)
- [14 测试、评估与可观测性](14_测试评估与可观测性/README.md)
- [15 安全、成本与生产实践](15_安全成本与生产实践/README.md)
- [16 综合项目](16_综合项目/README.md)
- [术语表](术语表.md)
- [重构说明](重构说明.md)

## 目录说明

- 每个编号目录包含一份主教程 `README.md`。
- `examples/` 保存可复用、可直接运行或可测试的参考代码。
- 所有密钥通过环境变量配置，禁止写入源码。
- 示例优先使用 OpenAI 兼容 API；模型名称由环境变量控制。
- 框架示例和“纯 Python 原理示例”并存，避免只会调用封装 API。

## 环境准备

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

第 07 章默认使用可离线运行的教学检索器；需要实践 Chroma 持久化向量库时，再安装 `requirements-optional.txt`。

最小配置：

```dotenv
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://your-provider.example/v1
LLM_MODEL=your-chat-model
EMBEDDING_MODEL=your-embedding-model
```

## 教程约定

每章尽量包含：学习目标、术语、原理、最小示例、完整示例、常见错误、练习和小结。代码中的网络调用均可能产生费用；运行前先确认服务地址、模型名称和账户额度。

## 从原课程到新教程的对应关系

| 原课程 | 新教程 |
| --- | --- |
| 01～04 环境与 API | 01～03 |
| 05～08 Prompt、Parser、Chain | 04～05 |
| 09～10 工具 | 06 |
| 11～13 RAG | 07 |
| 14～19 LangGraph | 08～09 |
| 20～23 高级编排 | 10～12 |
| 24～26 项目 | 16 |
| 27～28 部署评估与总结 | 13～15 |

## 学完后的能力

你应能解释 Agent 的决策循环，独立设计工具与状态，构建 RAG 和 LangGraph 工作流，实现人工审批与失败恢复，并用测试、评估、日志、安全边界和成本预算把项目推进到可交付状态。
