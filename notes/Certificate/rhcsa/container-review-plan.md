---
id: "kb-rhcsa-container-review-plan"
title: "RHCSA 容器专项、报考与复习计划"
summary: "容器镜像专项题、报考指南和三周复习安排。"
category: "认证考试"
status: "published"
order: 27
parent: "kb-certification-rhcsa"
tags: ["rhcsa", "container", "exam-plan"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhcsa.md"
applicableVersion: "RHCSA 9.0"
---

# RHCSA 容器专项、报考与复习计划

> 容器通用知识以 [云计算与容器](/cloud) 为 Canonical；本文聚焦 RHCSA 考试题型。

## 34. 容器镜像系统概述 (2026-07-01)

### 什么是容器镜像？

镜像是一个**只读模板**，包含运行应用所需的一切：
- 应用代码
- 运行时环境（Python、Java...）
- 系统库文件
- 环境变量、配置

类比：镜像 = 装好软件的系统盘，容器 = 用这个盘启动的一台虚拟机。

### 分层结构

```
┌─────────────────────┐
│   应用代码层 (COPY)  │  ← 最上层，每次改代码只重建这一层
├─────────────────────┤
│   依赖安装层 (RUN)   │  ← 比如 pip install
├─────────────────────┤
│   基础镜像层 (FROM)  │  ← 比如 python:3.11-slim
└─────────────────────┘
```

- 多个镜像共享相同的层，节省磁盘空间
- 改了上层，下层不用重建（构建缓存）
- 分发时只传输变化的层

### RHCSA 用 Podman，不是 Docker

```bash
podman --version
# RHEL 9/10 默认用 podman，命令和 docker 几乎一样
# 区别：podman 无守护进程、支持 rootless
```

### 核心操作速查

| 操作 | 命令 |
|------|------|
| 拉取镜像 | `podman pull <image>` |
| 查看镜像 | `podman images` |
| 运行容器 | `podman run -d --name <name> -p <host:cont> <image>` |
| 进入容器 | `podman exec -it <name> /bin/bash` |
| 查看日志 | `podman logs <name>` |
| 导出镜像 | `podman save -o <file.tar> <image>` |
| 导入镜像 | `podman load -i <file.tar>` |
| 推送镜像 | `podman login` → `podman tag` → `podman push` |
| 删除镜像 | `podman rmi <image>` |
| 清理悬空镜像 | `podman image prune` |

### Containerfile 编写

```dockerfile
FROM registry.access.redhat.com/ubi9/ubi:latest
RUN dnf install -y python3 && dnf clean all
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 8080
CMD ["python3", "app.py"]
```

**关键指令：**

| 指令 | 作用 | 示例 |
|------|------|------|
| `FROM` | 指定基础镜像（必须第一行） | `FROM ubi9/ubi:latest` |
| `COPY` | 复制文件到镜像 | `COPY app.py .` |
| `RUN` | 执行命令（构建时） | `RUN dnf install -y python3` |
| `CMD` | 容器启动时执行的命令 | `CMD ["python3", "app.py"]` |
| `EXPOSE` | 声明端口（文档作用） | `EXPOSE 8080` |
| `WORKDIR` | 设置工作目录 | `WORKDIR /app` |

**构建缓存优化：**
- 不常变的指令放前面（利用缓存，加快构建）
- `RUN` 命令合并，减少层数：
```dockerfile
# 不好（3 层）
RUN dnf install -y python3
RUN dnf install -y pip
RUN dnf clean all

# 好（1 层）
RUN dnf install -y python3 pip && dnf clean all
```

### systemd 管理容器

```bash
# 生成 systemd 服务文件
podman generate systemd --new --name web --files

# 复制到 systemd 目录
cp container-web.service /etc/systemd/system/

# 重新加载 + 启用
systemctl daemon-reload
systemctl enable --now container-web.service
```

**`--new` 参数重要：**
- 加 `--new`：systemd 会每次重启时重新创建容器（推荐）
- 不加：只做 start/stop，容器配置变了不会更新

### 考试注意事项

1. Podman 是 **rootless** 的，普通用户也能跑容器
2. `COPY` 路径是相对于构建上下文（`.`），不是宿主机根目录
3. 镜像名格式：`[registry/]repository[:tag]`，不写 tag 默认 latest
4. `save/load` 是离线传输（tar 文件），`push/pull` 是在线传输（仓库）

---

## 35. 容器镜像练习题 (2026-07-01)

### 题型一：写 Containerfile 构建镜像

**题目：** 创建 Containerfile，基于 ubi9，安装 python3，复制 app.py，暴露 8080，构建镜像 myapp:v1

```bash
mkdir -p /root/container-exam && cd /root/container-exam

cat > app.py << 'EOF'
from http.server import HTTPServer, SimpleHTTPRequestHandler
HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler).serve_forever()
EOF

cat > Containerfile << 'EOF'
FROM registry.access.redhat.com/ubi9/ubi:latest
RUN dnf install -y python3 && dnf clean all
WORKDIR /app
COPY app.py .
EXPOSE 8080
CMD ["python3", "app.py"]
EOF

podman build -t myapp:v1 .
```

### 题型二：导出/导入镜像

```bash
# 导出
podman save -o /tmp/myapp-v1.tar myapp:v1

# 删除原镜像
podman rmi myapp:v1

# 导入
podman load -i /tmp/myapp-v1.tar

# 验证
podman images
```

### 题型三：镜像推送到私有仓库

```bash
podman login registry.example.com
podman tag myapp:v1 registry.example.com/myrepo/myapp:latest
podman push registry.example.com/myrepo/myapp:latest
```

### 题型四：容器管理

```bash
# 启动
podman run -d --name web -p 8080:8080 myapp:v1

# 查看
podman ps

# 进入容器
podman exec -it web /bin/bash

# 查看日志
podman logs web
```

### 题型五：systemd 管理容器

```bash
podman generate systemd --new --name web --files
cp container-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now container-web.service
systemctl status container-web.service
```

### 题型六：容器网络

```bash
# 创建自定义网络
podman network create mynet

# 多容器通过容器名互通
podman run -d --name web --network mynet myapp:v1
podman run -d --name client --network mynet ubi9/ubi sleep 3600
podman exec client ping -c 3 web
```

---

## 36. RHCSA 报考指南 (2026-07-01)

### 考试基本信息

| 项目 | 内容 |
|------|------|
| 考试代码 | EX200 |
| 当前版本 | 基于 RHEL 10（已从 RHEL 9 升级） |
| 形式 | 上机实操，约 2-3 小时 |
| 费用 | 约 4000-6000 元 |

### 报名方式

- **不能个人直接报名**，必须通过红帽授权培训机构或 Pearson VUE
- 常见机构：达内、中软国际、誉天等
- 培训机构一般有"培训+考试"套餐

### 前置条件

- RHCSA 不强制要求培训课程，有经验可直接考
- RHCE 必须先有 RHCSA 证书

### 注意事项

- 考试已升级到 RHEL 10，复习资料要确认版本
- 考位需要排期，建议提前预约

---

## 37. 考试复习计划 (2026-07-01)

### 总览

```
7/1-7/7    → RHCSA 核心考点突击
7/8-7/14   → RHCE Ansible + 软考穿插
7/15-7/21  → 三科模拟题轮番刷
7/22-7/31  → 考前冲刺 + 考试
```

### 第一周：RHCSA 核心考点（每天 4h 实操 + 2h 理论）

| 日期 | 上午（实操） | 晚上（复盘） |
|------|-------------|-------------|
| Day 1 | LVM 创建：PV → VG → LV → 格式化 → 挂载 | 记笔记，默写命令 |
| Day 2 | LVM 进阶：扩容（在线/离线）、缩容 | 做 2 道 LVM 题 |
| Day 3 | LVM 快照：创建 → 验证 → merge 恢复 | 整理 LVM 完整流程图 |
| Day 4 | 用户权限：useradd/groupadd/chmod/chown/ACL | SELinux 布尔值 + 上下文 |
| Day 5 | systemd：创建自定义服务 → enable → 日志排查 | 练习 journalctl |
| Day 6 | nmcli：配 IP/DNS/路由/Bond/桥接 | systemctl restart NetworkManager |
| Day 7 | Podman：Containerfile → build → run → save/load | systemd 管理容器 |

### 第二周：RHCE Ansible + 软考（每天 3h Ansible + 3h 软考）

| 日期 | 上午（Ansible） | 下午（软考） |
|------|----------------|-------------|
| Day 8-9 | inventory + ad-hoc + playbook 基础 | OSI/TCP-IP + 子网划分 |
| Day 10-11 | loops/conditionals/templates + roles | 路由协议 + 交换机/VLAN |
| Day 12 | 实战写完整 playbook | 网络安全 |
| Day 13-14 | Ansible 查漏补缺 | 软考真题 |

### 第三周：模拟题轮刷

- 每天一套模拟题（RHCSA/RHCE 轮换）
- 软考真题每天一套
- 错题整理是核心
- 考前 3 天不学新东西，只看错题

### 关键原则

1. **实操 > 看书** — RHCSA/RHCE 都是上机考
2. **每天必须碰 Linux** — 保持手感
3. **错题本** — 考前只看错题
4. **软考和 RHCSA 有交集** — 网络配置部分学一份两边用

---
