---
id: "kb-cloud-platforms-exam"
title: "执行环境、虚拟化与容器考试"
summary: "Ansible 执行环境、虚拟化、云原生和认证考试容器操作。"
category: "云计算"
status: "published"
order: 15
parent: "kb-cloud-containers"
tags: ["virtualization", "cloud-native", "rhce"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# 执行环境、虚拟化与容器考试

## 7. 容器编排与执行环境

### 7.1 ansible-navigator（容器执行环境）

**是什么：** RHCE 考试用的 Ansible 执行环境，跑在 Podman 容器里。

**对比 ansible-playbook：**

| | ansible-playbook | ansible-navigator |
|---|---|---|
| **执行环境** | 宿主机本地 | 容器内（Podman） |
| **输出** | 直接打到终端 | 默认进交互界面，加 `-m stdout` 才打到终端 |
| **环境隔离** | ❌ | ✅ |
| **配置文件** | ansible.cfg | ansible-navigator.yml（指定容器镜像） |
| **PATH 环境** | 直接加载 | 需要完整 PATH（`su - devops` 才能加载） |

**考试关键：** 配置文件 `ansible-navigator.yml` 指定容器镜像地址，考试镜像在 `registry.lab.example.com`。

```yaml
# ansible-navigator.yml
---
ansible-navigator:
  execution-environment:
    image: registry.lab.example.com/rhel9-ee:latest
  playbook-artifact:
    enable: true
```

**常用命令：**
```bash
ansible-navigator run playbook.yml -m stdout           # 跑 playbook
ansible-navigator run playbook.yml -i inventory -m stdout  # 显式指定 inventory
ansible-navigator logs                               # 查看日志
ansible-navigator explore                            # 交互式调试
ansible-navigator images                             # 获取导航器镜像
podman login utility.lab.example.com                 # 登录镜像仓库
```

---

### 7.2 为什么加 `-i inventory`？

- `ansible-playbook`（本机执行）→ 读 `ansible.cfg` 里的 inventory 配置，自动找到
- `ansible-navigator`（容器里执行）→ 容器内"当前目录"可能和宿主机不同，`ansible.cfg` 里的相对路径找不到
- `-i inventory` 是显式指定 inventory 路径的**保险写法**，防止 `No inventory was parsed` 警告
- **简单记：本地跑一般不用加，容器跑加 `-i` 更稳**

---

## 8. 虚拟机与虚拟化

> _暂无内容（KVM 虚拟化知识待归档）_

---

## 9. JVM 虚拟机

> _暂无内容_

---

## 10. 云服务与云原生

> _暂无内容_

---

## 11. RHCE/RHCSA 容器考试专项

### 11.1 模拟题 vs 正式考试对比

| 对比项 | 模拟题 | 正式考试（2026） |
|---|---|---|
| 容器数量 | 3 道独立容器题 | **3 合 1**，一道题考完 |
| 镜像来源 | 自定义构建（Containerfile + build） | **自行拉取**（podman pull） |
| 镜像地址 | 固定地址 | **每人不同**，和座位号相关 |

---

### 11.2 镜像地址规律

```
座位号 10 → registries.server10.example.com/library/...
座位号 5  → registries.server5.example.com/library/...
```

⚠️ **镜像地址每人不同，务必先查考前须知，用 `podman search` 确认路径后再拉取。**

---

### 11.3 完整考试操作流程

```bash
# 1. 登录仓库（地址看考前须知）
podman login registries.serverXX.example.com

# 2. 搜索镜像确认路径
podman search registries.serverXX.example.com watch

# 3. 拉取镜像
podman pull registries.serverXX.example.com/library/watch:latest

# 4. 准备挂载目录
mkdir -p /opt/txt /opt/pdf

# 5. 运行临时容器
podman run -d --name txt2pdf \
  -v /opt/txt:/opt/txt:Z \
  -v /opt/pdf:/opt/pdf:Z \
  registries.serverXX.example.com/library/watch:latest

# 6. 生成 systemd 服务文件
mkdir -p ~/.config/systemd/user
cd ~/.config/systemd/user
podman generate systemd txt2pdf --files --name new

# 7. 启用开机自启
systemctl --user daemon-reload
systemctl --user enable container-txt2pdf.service

# 8. 清理并重启
podman rm -f txt2pdf
systemctl --user restart container-txt2pdf.service

# 9. 验证
podman ps
```

---

### 11.4 必背命令速查

| 操作 | 命令 |
|------|------|
| 登录仓库 | `podman login <registry>` |
| 搜索镜像 | `podman search <registry> <keyword>` |
| 拉取镜像 | `podman pull <full-image-path>` |
| 列出镜像 | `podman images` |
| 打标签 | `podman tag <src> <dst>` |
| 删除镜像 | `podman rmi <image>` |
| 运行容器 | `podman run -d --name <name> <image>` |
| 列出容器 | `podman ps` / `podman ps -a`（含停止的） |
| 进入容器 | `podman exec -it <name> /bin/bash` |
| 删除容器 | `podman rm <name>` |
| 生成 systemd | `podman generate systemd <name> --files --name new` |
| 启用自启 | `systemctl --user enable container-<name>.service` |
| 查远程镜像 | `skopeo inspect docker://<image>` |
| 删除远程镜像 | `skopeo delete docker://<image>` |
---
