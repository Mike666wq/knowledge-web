# 02 Python 与项目环境

Agent Demo 往往只需要几十行代码，但可复现的 Agent 项目还需要隔离依赖、管理配置、处理异常并支持测试。本章把这些基础一次搭稳，后续示例都沿用同一套环境变量约定。

## 学习目标

完成本章后，你应当能够：

1. 创建、激活和验证 Python 虚拟环境；
2. 解释解释器、虚拟环境、包、模块和依赖锁定的区别；
3. 使用项目根目录的 `requirements.txt` 安装依赖；
4. 使用 `.env` 与系统环境变量保存配置，不在源码中写密钥；
5. 使用类型标注、数据类和异常建立可靠的配置边界；
6. 运行环境自检脚本和离线单元测试。

## 1. 术语解释

| 术语 | 解释 | 本教程中的用途 |
| --- | --- | --- |
| Python Interpreter | 读取并执行 Python 代码的程序 | 确保终端、编辑器和测试使用同一解释器 |
| Virtual Environment | 独立的 Python 与第三方包安装目录 | 避免不同项目依赖互相污染 |
| Package | 可安装、分发的一组 Python 模块 | 例如 `openai`、`pydantic` |
| Module | 一个可导入的 `.py` 文件或扩展模块 | 例如 `settings.py` |
| Dependency | 当前项目运行所依赖的第三方包 | 记录在 `requirements.txt` |
| Environment Variable | 由操作系统或进程提供的键值配置 | 保存密钥、模型名、服务地址和超时 |
| `.env` | 本地开发时保存环境变量的文本文件 | 应被 Git 忽略，不应分享真实密钥 |
| Type Hint | 对变量、参数和返回值的类型说明 | 提高可读性并帮助静态检查 |
| Dataclass | 用于定义数据对象的标准库工具 | 集中保存经过校验的配置 |
| Exception | 程序无法正常继续时抛出的错误对象 | 让配置错误尽早、清晰地暴露 |
| Unit Test | 验证一个小单元行为的自动化测试 | 不调用真实 API 也能验证核心逻辑 |
| Sync / Async | 同步依次等待；异步可在等待 I/O 时处理其他任务 | Agent 调多个 API 时常需异步，但应先掌握同步版本 |

## 2. 推荐环境

- Python 3.11 或 3.12；
- VS Code 或其他能选择 Python 解释器的编辑器；
- `venv` 创建虚拟环境；
- PowerShell、CMD、Bash 等命令行；
- Git 用于版本管理。

不建议把教程绑定到某个精确的 Python 补丁版本。项目真正需要的是兼容范围和可复现依赖，而不是“只有 3.12.11 才能运行”。

## 3. 创建并激活虚拟环境

在 `C:\笔记\AI-agent` 目录执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

使用 `python -m pip` 比直接写 `pip` 更清晰：它明确表示“使用当前这个 Python 解释器对应的 pip”。

验证解释器：

```powershell
python -c "import sys; print(sys.executable); print(sys.version)"
python -m pip --version
```

两条命令显示的路径都应指向当前项目的 `.venv`。

## 4. 依赖管理原理

项目根目录采用兼容范围，例如：

```text
openai>=2.0,<3
pydantic>=2.7,<3
```

这表示教程支持同一主版本中的兼容更新。教学项目可以用范围保持可安装性；生产部署通常还会根据已验证环境生成锁文件或精确版本清单。

不要直接把整个开发环境的 `pip freeze` 当作教程依赖，它会包含大量间接依赖和与平台相关的包，掩盖项目真正使用了什么。

常用命令：

```powershell
python -m pip list
python -m pip show openai
python -m pip check
python -m pytest -q
```

## 5. 环境变量与密钥安全

复制项目根目录已有模板：

```powershell
Copy-Item .env.example .env
```

填写你自己的配置：

```dotenv
OPENAI_API_KEY=your-real-key
OPENAI_BASE_URL=https://provider.example/v1
LLM_MODEL=provider-model-name
REQUEST_TIMEOUT=60
```

规则如下：

1. `.env.example` 只写变量名和无敏感性的示例值；
2. `.env` 保存本机真实值，并确保它没有被提交；
3. 代码只通过 `os.environ` 或配置类读取；
4. 日志不打印完整密钥；
5. CI/CD 和生产环境使用平台的 Secret 管理功能，而不是复制开发机 `.env`。

### 配置优先级

`python-dotenv` 默认把 `.env` 中的值加载到进程环境中，但不会覆盖已存在的系统环境变量：

```text
操作系统/运行平台注入的变量（高优先级）
            ↓
本地 .env 中尚未存在的变量
            ↓
应用代码读取并校验
```

不要在库模块导入时到处调用 `load_dotenv()`。推荐由程序入口加载一次，再把配置对象传给其他模块；这样测试更容易控制输入。

## 6. Agent 开发需要的 Python 基础

### 6.1 字典与 JSON

API 请求和响应常以 JSON 传输，进入 Python 后通常表现为字典、列表、字符串、数字和布尔值。

```python
message = {"role": "user", "content": "你好"}
```

JSON 不是 Python 字典。JSON 使用 `true`、`false`、`null`；Python 使用 `True`、`False`、`None`。

### 6.2 函数与类型标注

```python
def normalize_question(text: str) -> str:
    value = text.strip()
    if not value:
        raise ValueError("问题不能为空")
    return value
```

类型标注不会自动阻止错误类型传入，但能表达接口契约，并被编辑器、类型检查器和数据校验库利用。

### 6.3 异常处理

```python
try:
    result = call_service()
except TimeoutError as exc:
    raise RuntimeError("上游服务超时") from exc
```

只捕获你能处理的异常。`except Exception: pass` 会吞掉真正的问题，使 Agent 看起来“没有响应”。

### 6.4 数据类与 Pydantic

- `dataclass` 适合程序内部、已经可信的数据对象；
- Pydantic 适合 API、环境变量、模型输出等外部输入，需要运行时校验。

本章配置示例使用数据类并手动校验；第 04 章使用 Pydantic 校验模型输出。

### 6.5 同步与异步

同步代码更容易学习和调试：

```python
result = client.call()
```

异步代码适合大量 I/O 等待：

```python
result = await async_client.call()
```

异步不会让一次模型推理本身变快，它提高的是多个等待任务重叠执行时的吞吐量。前四章以同步为主。

## 7. 递进示例

本章专属示例位于 `examples/`：

```text
examples/
├── .env.example
├── settings.py
├── check_environment.py
└── test_settings.py
```

### 示例 1：加载并校验配置

`Settings.from_env()` 完成三件事：

1. 检查必须变量；
2. 把超时从字符串转换为浮点数；
3. 拒绝无效范围，并提供不会泄露密钥的摘要。

### 示例 2：运行环境自检

从项目根目录运行：

```powershell
python 02_Python与项目环境\examples\check_environment.py
```

自检只验证本地环境和配置，不发送网络请求，也不会打印密钥。

### 示例 3：离线测试

```powershell
cd 02_Python与项目环境\examples
python -m pytest test_settings.py -q
```

测试直接传入一个模拟环境变量字典，因此不依赖开发者机器上的真实 `.env`。

## 8. 常见错误

### 错误 1：编辑器和终端使用不同解释器

表现为终端可以导入包，Notebook 或编辑器却报 `ModuleNotFoundError`。检查 `sys.executable`，重新选择项目 `.venv`。

### 错误 2：把 `.env` 当作 Python 文件

`.env` 应写 `KEY=value`，不能写 `KEY = "value"` 后再用 Python 语法理解它。值中需要空格时可以加引号，但不要在等号两侧随意加入语义不清的内容。

### 错误 3：在源码中设置真实密钥

```python
# 错误示例
api_key = "sk-real-secret"
```

一旦进入 Git 历史，即使删除当前行也可能已经泄露。应立即吊销并重新生成密钥。

### 错误 4：用空字符串绕过配置检查

`OPENAI_API_KEY=` 与没有可用密钥等价。应在启动时失败，而不是等到请求发出后才收到难懂的 401。

### 错误 5：盲目升级所有包

框架主版本可能包含破坏性变化。升级后先运行测试，再处理弃用警告和接口变化。

### 错误 6：删除虚拟环境前没有确认路径

虚拟环境可以重建，但递归删除命令风险很高。先确认目标确实是项目内的 `.venv`，再执行删除操作。

## 9. 练习

1. 创建 `.venv`，记录 `sys.executable` 和 `pip --version` 输出；
2. 将 `REQUEST_TIMEOUT` 设置为 `abc`，观察错误并解释为什么要尽早校验；
3. 为 `Settings` 增加 `MAX_AGENT_STEPS`，要求范围为 1～100；
4. 修改测试，验证空白模型名会被拒绝；
5. 写一个 `mask_secret()` 函数，只显示密钥最后四位，并为它写测试；
6. 比较系统环境变量与 `.env` 同名时，`load_dotenv()` 的实际优先级。

## 10. 小结

- 虚拟环境隔离项目依赖，解释器路径是排查环境问题的第一线索；
- 依赖清单表达项目真正需要的直接依赖；
- 密钥属于运行时配置，不属于源码；
- 入口加载、集中校验、对象传递比到处读取环境变量更容易测试；
- 下一章会在这套配置基础上调用 OpenAI 兼容的大模型 API。

