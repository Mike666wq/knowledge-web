# 知识与任务管理 Agent

可运行的交付骨架，默认不访问网络、不需要 API Key。

```bash
python -m unittest discover -s tests -v
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

支持三类输入：

- 普通知识问题：权限过滤后检索并返回引用。
- `计算 2 * (3 + 4)`：调用受限 AST 计算器。
- `创建任务：复习评估`：返回审批指纹；用同一参数和指纹再次调用后写入。

示例请求中的 `roles` 仅为教学方便。生产服务必须从已验证的身份令牌构建角色，不能信任请求体。
