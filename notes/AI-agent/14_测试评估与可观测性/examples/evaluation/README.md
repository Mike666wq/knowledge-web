# Agent 离线评估示例

只使用 Python 标准库：

```bash
python evaluate.py
python -m unittest discover -s tests -v
```

`dataset.jsonl` 是期望，`sample_runs.jsonl` 是某个候选版本的实际运行记录。真实系统只需导出相同字段，即可复用指标计算。`observability.py` 展示不记录原始 Prompt 的最小 span。

注意：事实覆盖率使用标准化后的短语匹配，只是可解释基线，不等于语义忠实度。生产评估应增加人工标注或经过校准的语义评审。
