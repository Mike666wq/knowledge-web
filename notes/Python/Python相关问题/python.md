---
id: "kb-programming-python-fastapi"
title: "Python / FastAPI"
category: "编程语言"
status: "published"
order: 2
---

# 🐍 Python / FastAPI

---

## python vs python3 的区别

### 历史原因
- Python 2（`python`）已于 2020 年废弃
- Python 3（`python3`）是当前主流

### 为什么有两个命令
- `python` → 系统默认，可能是 Python 2 或 3，取决于系统配置
- `python3` → 明确指定 Python 3，不会搞混

### 不同系统表现
- macOS 老版本：`python` → Python 2.7，`python3` → Python 3.x
- macOS 新版本：`python` 可能不存在，`python3` → Python 3.x
- Ubuntu 20.04+：`python` 可能不存在，`python3` → Python 3.x
- CentOS 7：`python` → Python 2.7

### 最佳实践
- **永远用 `python3`**，明确指定版本
- `python3 script.py` > `python script.py`
- Python 2 已废弃，很多库不支持

### 验证命令
```bash
python --version
python3 --version
which python
which python3
```

---

## `python3 -m <module>` 参数详解

### 核心理解
`-m <module>`：把模块当作脚本运行
- Python 在 `sys.path` 里找这个模块
- 执行 `if __name__ == "__main__":` 那部分
- 不需要写 `.py` 后缀

### `python3 -m http.server` 解析
启动简易 HTTP 服务器，**当前目录作为网站根目录**，**默认监听 8000 端口**。

**完整签名：**
```
python3 -m http.server [port] [--bind ADDR] [--directory DIR]
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `port` | 端口号（位置参数） | **8000** |
| `--bind / -b` | 绑定 IP | **0.0.0.0**（所有网卡） |
| `--directory / -d` | 服务目录（3.7+） | **当前工作目录** |

### `-m` 后能接其他参数吗？
**能！** `-m http.server` 后面的所有参数都传给 http.server 模块自己：
```bash
python3 -m http.server 9000 --bind 127.0.0.1 --directory /tmp/share
```

### 其他常用 `-m` 模块

| 命令 | 用途 |
|------|------|
| `python3 -m pip install xxx` | 包管理 |
| `python3 -m venv myenv` | 创建虚拟环境 |
| `python3 -m pdb myscript.py` | 调试器（pdb） |
| `python3 -m json.tool file.json` | JSON 格式化 |
| `python3 -m ensurepip` | 安装 pip |
| `python3 -m py_compile foo.py` | 语法检查（不执行） |
| `python3 -m unittest` | 单元测试 |
| `python3 -m doctest mymodule.py` | 文档测试 |

### `-m` vs 直接执行脚本

| 写法 | 含义 |
|------|------|
| `python3 script.py` | 执行文件路径 |
| `python3 -m foo` | 从 `sys.path` 找模块执行 |

**关键区别：** 当前目录的 `foo.py`，`python3 foo` 找不到，`python3 -m foo` 能找到（当前目录在 `sys.path`）。

### `http.server` 默认端口确认
- 默认端口：**8000**
- 默认绑定：**0.0.0.0**（所有网卡）
- 默认目录：**当前工作目录**

> 💡 配合 Docker 端口映射注意：`-p 8000:8000` 只是端口映射规则，**和 http.server 默认 8000 是独立的巧合**。三个端口必须一致：主机端口 → 容器端口 → 服务监听端口。详见 cloud.md §3.3.1。

---

## LangChain LCEL 链式调用的延迟执行

### 核心结论

```python
chain = prompt | llm        # 只构造链，不执行
chain.invoke({...})         # 此时才真正执行
```

`prompt | llm` 不会调用模型，也不会填充模板变量。它只是把两个 `Runnable` 组合成一个 `RunnableSequence`，记录后续的执行顺序。

### 第一步：构造 `RunnableSequence`

```python
chain = prompt | llm
```

- `prompt` 和 `llm` 都实现了 LangChain 的 `Runnable` 接口。
- `|` 运算符把组件连接成执行图。
- 此时模板不渲染、模型不调用、不会产生网络请求。
- 得到的 `chain` 本身也是一个 `Runnable`。

### 第二步：触发执行

```python
result = chain.invoke({
    "style": "简洁",
    "question": "什么是 LCEL？"
})
```

链会从左到右依次运行：

| 顺序 | 调用 | 作用 |
|------|------|------|
| 1 | `prompt.invoke(input_dict)` | 用输入字典填充 `{style}` 等占位符，渲染成消息或 PromptValue |
| 2 | `llm.invoke(rendered_prompt)` | 将渲染后的内容发送给模型，返回 `AIMessage` 等结果 |

变量填充发生在 `prompt.invoke()` 阶段，由整个链的 `invoke()` 触发。LLM 不会看到原始占位符，只会收到已经渲染好的最终内容。

### 常见执行接口

| 接口 | 用途 |
|------|------|
| `invoke(input)` | 同步执行一次，返回最终结果 |
| `stream(input)` | 流式执行，逐块返回结果 |
| `batch([input1, input2])` | 批量处理多组输入，可并行执行 |
| `ainvoke(input)` | 异步执行一次 |
| `astream(input)` | 异步流式执行 |
| `abatch(inputs)` | 异步批量执行 |

### 心智模型

- `|`：声明“应该怎样做”，用于定义和组合流程。
- `invoke`、`stream`、`batch`：命令“现在开始做”，用于真正触发流程。
- 类比：`prompt | llm` 像写好 SQL 查询，`invoke()` 像调用 `execute()`。

<!-- KB:INSERT:python-additions -->
