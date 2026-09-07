---
id: "kb-linux-shell-system"
title: "Linux Shell 与系统管理速查"
summary: "系统状态、Shell 引号、服务管理、APT 和 Alias。"
category: "操作系统"
status: "published"
order: 15
parent: "kb-linux-operations"
tags: ["shell", "systemd", "apt", "alias"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Linux Shell 与系统管理速查

## 9. free -m vs df -Th vs lsblk 三者对比

| | free -m | df -Th | lsblk |
|---|---|---|---|
| 看什么 | 内存 + swap | 文件系统空间 | 块设备结构 |
| 层级 | RAM 层 | 文件系统层 | 磁盘/分区层 |
| swap 相关 | ✅ 显示 swap 总量和使用 | ❌ 不显示 | ⚠️ 只标 [SWAP] 标记 |
| 能看到设备关系 | ❌ | ❌ | ✅ 树状展示 |
| 能看到可用空间 | ✅ 内存可用 | ✅ 磁盘可用 | ❌ 只有大小 |

**为什么验证 swap 用 free -m 而不是 df -Th？** swap 分区没有文件系统，`df -Th` 根本看不到它。

---


---

## 11. Bash 单引号与双引号的区别

**无变量时两者等价：**
- `logger 'This is a rhcsa exam'` 和 `logger "This is a rhcsa exam"` 效果相同

**有变量时不同：**
- 单引号：所见即所得，不解析变量 → `echo '$VAR'` 输出 `$VAR`
- 双引号：解析变量和命令替换 → `echo "$VAR"` 输出变量值

**记忆：** 字符串里有 `$` 才需要考虑用哪种引号，纯文本随便用

---


---

## 14. macOS 与 Linux 服务管理体系对比

### macOS 服务管理

#### 1. launchd（核心机制）
- 系统级：`/Library/LaunchDaemons/`（后台守护）、`/Library/LaunchAgents/`（登录启动）
- 用户级：`~/Library/LaunchAgents/`
- 管理命令：`launchctl list`、`launchctl load/unload`
- 配置文件：plist 格式

#### 2. Homebrew Services（第三方，推荐）
- `brew services list/start/stop/restart`
- 简化了 launchd 的操作

#### 3. 应用目录
- `/Applications/`（系统级）、`~/Applications/`（用户级）

### Linux 服务管理

#### systemd（核心）
- 服务文件：`/lib/systemd/system/`
- 自定义服务：`/etc/systemd/system/`
- 用户服务：`~/.config/systemd/user/`
- 管理命令：`systemctl list-units --type=service`、`systemctl status/start/stop/enable/disable`

### 关键区别

| 维度 | macOS | Linux |
|------|-------|-------|
| 服务管理 | launchd + brew services（两层） | systemd（一个管所有） |
| 服务配置 | plist 文件 | service 文件 |
| 查看端口 | `lsof -i -P | grep LISTEN` | `ss -tlnp` |
| 包管理 | brew | apt/yum/dnf |


---

## 16. apt update 与 apt upgrade 的区别

- `apt update`：更新软件源索引（本地缓存的包列表），**不安装任何软件**
- `apt upgrade`：根据最新索引，实际升级已安装的软件包

**为什么要先 update？**
- apt install/upgrade 查的是本地缓存的索引，不会实时访问远程服务器
- 不 update → 本地索引过期 → 可能装不上或装旧版本
- 类比：先去超市拿最新价目表，再按价格买东西

**标准流程**：`sudo apt update && sudo apt upgrade -y`

---

## 17. Alias 别名配置

**配置文件**：
- Linux bash：`~/.bashrc`
- Linux zsh / macOS zsh：`~/.zshrc`
- 全局：`/etc/bash.bashrc` 或 `/etc/profile.d/`

**用法**：
- 临时生效：`alias python=python3`
- 永久生效：写入 `~/.zshrc` 或 `~/.bashrc`，然后 `source` 加载
- 查看所有别名：`alias`
- 删除别名：`unalias python`

**python3 vs python**：很多 Linux 发行版默认只有 `python3`，没有 `python`，用 `alias python=python3` 即可解决

**注意**：`python3` 和 `pip3` 本身就是标准命令，不需要起别名。需要 alias 的是 `python` 和 `pip`（让它们指向 python3/pip3）。在 venv 虚拟环境里 `python`/`pip` 自动可用，不需要 alias。
