# 安全与预算边界示例

运行：

```bash
python safe_agent.py
python -m unittest discover -s tests -v
```

示例把模型视为“动作提议者”。`ToolPolicy` 是最终裁决者；用户文本中即使出现授权声明也不能改变代码策略。`InjectionScanner` 只增加风险信号，不能替代策略。

`BudgetLedger` 是单进程教学实现。多进程/分布式生产环境必须把 `reserve` 与 `settle` 放入支持原子更新的数据库或配额服务。
