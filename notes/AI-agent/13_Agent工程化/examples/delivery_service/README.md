# 可交付 Agent 服务骨架

这个示例刻意使用 `MockModelClient`，因此不需要 API Key。它演示服务边界，而不是绑定某家模型供应商。

## 运行

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
curl http://127.0.0.1:8000/live
curl -X POST http://127.0.0.1:8000/v1/answer \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是可重试错误？"}'
```

测试不依赖 FastAPI 或外网：

```bash
python -m unittest discover -s tests -v
```

把 mock 换成真实模型时，实现 `ModelClient.generate()` 协议，在应用启动时注入，并在适配器内部设置单次网络超时。不要改变领域服务或 HTTP 数据模型。
