---
id: "kb-linux-automation-monitoring"
title: "Linux 自动化与系统监控"
summary: "Cron、监控脚本、压力测试与 watch 实时观察。"
category: "操作系统"
status: "published"
order: 14
parent: "kb-linux-operations"
tags: ["cron", "monitoring", "stress-ng", "watch"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Linux 自动化与系统监控

## 5. Cron 计划任务完整指南
| cron 写法 | 含义 | 执行时间 |
|-----------|------|----------|
| `*/2` | 每隔 2 分钟 | 0, 2, 4, 6, 8, ... |
| `2` | 每小时的第 2 分钟 | x:02:00 |

**原理**：`*` 表示"所有值"，`*/2` = "所有值中每隔 2 个取一个"，即 0, 2, 4, 6...

**常见例子**：
- `*/5` → 每 5 分钟
- `*/10` → 每 10 分钟
- `*/15` → 每 15 分钟

**一句话**：`*/数字` = 每隔 N 分钟，单独写数字 = 每小时的第 N 分钟

---


---

### Cron 计划任务相关命令总结
### 一、Linux 系统 cron 命令

| 命令 | 含义 |
|------|------|
| `crontab -l` | 查看当前用户的计划任务 |
| `crontab -l -u natasha` | 查看指定用户的计划任务 |
| `crontab -e` | 编辑当前用户的计划任务（交互式） |
| `crontab -r` | 删除当前用户的所有计划任务 |
| `crontab mycron.txt` | 从文件导入计划任务 |

### cron 时间格式

```
┌────── 分钟 (0-59)
│ ┌──── 小时 (0-23)
│ │ ┌── 日 (1-31)
│ │ │ ┌ 月 (1-12)
│ │ │ │ ┌ 星期 (0-7, 0和7都是周日)
│ │ │ │ │
*/2 * * * *  echo hello
```

### 特殊符号

| 符号 | 含义 | 示例 |
|------|------|------|
| `*` | 每 | `* * * * *` 每分钟 |
| `*/n` | 每隔 n | `*/5 * * * *` 每5分钟 |
| `,` | 列举 | `1,3,5 * * * *` 第1、3、5分钟 |
| `-` | 范围 | `1-5 * * * *` 第1到5分钟 |

### 常见 cron 示例

- 每天凌晨2点：`0 2 * * * /scripts/backup.sh`
- 每周一早上8点：`0 8 * * 1 /scripts/report.sh`
- 每5分钟：`*/5 * * * * /scripts/check.sh`

### 二、Ansible cron 模块

| 参数 | 含义 |
|------|------|
| `name` | 任务描述（标识，用于删除） |
| `minute` | 分钟 |
| `hour` | 小时 |
| `day` | 日 |
| `month` | 月 |
| `weekday` | 星期 |
| `job` | 执行的命令 |
| `user` | 执行用户 |
| `state` | `present`(创建) / `absent`(删除) |

创建：`cron: name="任务描述" minute="*/2" user=natasha job="echo hello"`
删除：`cron: name="任务描述" state=absent`（用 name 匹配精确删除）

### 三、系统 crontab vs Ansible cron

| 项目 | 系统 crontab | Ansible cron 模块 |
|------|-------------|-------------------|
| 编辑方式 | `crontab -e` 交互式 | Playbook 声明式 |
| 删除任务 | 手动删行或 `crontab -r` 清空 | `state: absent` 按 name 精确删除 |
| 标识 | 无 | `name` 字段（Ansible 自动加注释） |

---


---


---

## 6. 系统监控脚本

### 脚本内容

```bash
#!/bin/bash
ps -xao user,pid,vsz,rss,%cpu --sort=%cpu
```

### ps 参数拆解

```
ps -xao user,pid,vsz,rss,%cpu --sort=%cpu
   ① ②        ③              ④
```

| 参数 | 含义 |
|---|---|
| `-x` | 显示所有用户的进程，包括不依附终端的 |
| `-a` | 显示所有终端（tty）上的进程 |
| `-o` | 自定义输出格式（字段用逗号隔开） |
| `--sort=%cpu` | 按 CPU 使用率升序排列 |

### 输出字段说明

| 字段 | 含义 |
|---|---|
| `user` | 进程的所有者 |
| `pid` | 进程 ID |
| `vsz` | 虚拟内存大小（KB） |
| `rss` | 实际占用的物理内存（KB） |
| `%cpu` | CPU 使用率 |

### 创建和运行

```bash
# 1. 创建脚本
vim /usr/local/bin/exam_sysinfo

# 2. 加执行权限
chmod +x /usr/local/bin/exam_sysinfo

# 3. 运行
exam_sysinfo
```

### ps 其他常用参数

| 参数 | 含义 |
|---|---|
| `-ef` | 显示所有进程 + 完整命令 |
| `-aux` | BSD 风格，显示所有进程 |
| `--sort=-%cpu` | 降序排列（CPU 最高的在前面） |
| `--sort=-%mem` | 按内存降序排列 |

⚠️ 脚本放在 `/usr/local/bin/` 可以直接用名字运行，不用写全路径。



---


### top 与 htop 实时监控

#### top 基本用法

```bash
top
```

**常用快捷键：**
| 按键 | 功能 |
|---|---|
| `Shift+M` | 按内存 (MEM%) 降序排列 |
| `Shift+P` | 按 CPU 降序排列 |
| `Shift+N` | 按 PID 降序排列 |
| `1` | 展开每个 CPU 核心 |
| `k` | 杀死进程（输入 PID） |
| `q` | 退出 top |

#### htop（增强版 top）

```bash
# 安装
yum install -y htop   # RHEL/CentOS
apt install -y htop   # Debian/Ubuntu

# 运行
htop
```

**htop 优势：**
- 鼠标可点击，无需记快捷键
- 彩色显示，更直观
- 支持树状视图（按 `F5`）
- 搜索进程（按 `F3`）

⚠️ `htop` 需要额外安装，`top` 系统自带。

---

### 6.1 lsof 详解（查进程 / 文件 / 端口 / 网络资源）

#### 查进程“三件套”
| 需求 | 命令 | 说明 |
|---|---|---|
| 进程快照 | `ps aux` | 最常用，一次列出所有进程 |
| 实时监控 | `top` / `htop` | 动态刷新（htop 更友好） |
| 查 PID | `pidof nginx` / `pgrep -f 关键字` | 按名字/命令行反查 PID |

`ps aux` 输出字段：`USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND`
STAT 常见值：`R` 运行、`S` 睡眠、`Z` 僵尸（有害）、`T` 停止、`s` 会话首进程。

#### lsof 是什么
**全名**：`LiSt Open Files` —— 列出打开的文件
**核心思想**：Linux **一切皆文件**（普通文件、目录、socket、管道、设备），所以 lsof 能查所有打开的资源。

#### 最常用的 7 个用法
**① 端口被占，谁在监听？**
```bash
lsof -i :80
# COMMAND  PID  USER  FD  TYPE  DEVICE  NAME
# nginx   1234  root  6u IPv4  ...     TCP *:http (LISTEN)
```

**② 文件被占，删不掉？**
```bash
rm /var/log/nginx/access.log   # Device or resource busy
lsof /var/log/nginx/access.log   # 查谁在用
```

**③ 进程打开了哪些东西？**
```bash
lsof -p 1234           # 进程 1234 所有打开的资源
lsof -p 1234 -i        # 进程 1234 的网络连接
```

**④ 谁在用某个目录？**
```bash
lsof +D /var/log/nginx/   # 递归查目录（慢）
lsof +d /var/log/nginx    # 不递归
```

**⑤ 指定用户的进程**
```bash
lsof -u root -i           # root 的网络连接
```

**⑥ 协议过滤**
```bash
lsof -i tcp:22            # 只看 22 端口 TCP
```

**⑦ 反向查连接**
```bash
lsof -p 1234 -i -a | grep ESTABLISHED
```

#### 实战场景速查
| 场景 | 命令 |
|---|---|
| 端口被占 | `lsof -i :端口` |
| 文件删不掉 | `lsof <文件>` |
| 查进程在干啥 | `lsof -p <PID>` |
| 查进程网络连接 | `lsof -p <PID> -i` |
| 查谁在写日志 | `lsof +D /var/log/` |

#### lsof vs ss vs netstat
| 命令 | 特点 | 用途 |
|---|---|---|
| `lsof` | **文件级**精确（进程+FD+文件） | 文件/端口/网络全能查 |
| `ss -tlnp` | **快**（读内核），netstat 替代品 | 仅查端口监听 |
| `netstat -tlnp` | 老工具，慢 | 同上（逐渐淘汰） |

**推荐**：查端口用 `ss -tlnp`（快），查具体进程占文件用 `lsof`（精）。

**一句话速记：** lsof = `LiSt Open Files`，Linux 一切皆文件，所以能查进程、文件、端口、socket、目录的所有打开状态。最常用三招：端口占用 `lsof -i :端口`、文件被占 `lsof <文件>`、进程资源 `lsof -p <PID>`。

---

## 22. stress-ng 压力测试工具

### 是什么
压力测试工具，可施加 CPU / 内存 / IO / 网络 等压力，常用于：
- 验证 Docker 资源限制（`-m`、`--cpus`）是否生效
- 测试系统在极限负载下的表现

### `--vm` 参数详解（重点）

**核心理解：** `--vm` 不是"虚拟内存"本身，是 vm 压力 worker 的**数量**。
- `--vm N`：启动 N 个 vm 压力 worker
- `--vm-bytes SIZE`：每个 worker 占多少内存
- **总占用 = `--vm` × `--vm-bytes`**

**示例：**
```bash
docker run tylersmith22/docker-stress-ng --vm 2 --vm-bytes 256m
# 2 个 worker × 256MB = 512MB 总占用
```

vm worker 反复写入内存，模拟"内存被疯狂使用"。

### 常用参数

| 参数 | 作用 | 默认 |
|------|------|------|
| `--vm N` | vm worker 数量 | 0 |
| `--vm-bytes SIZE` | 每个 worker 占用内存 | 256M |
| `--vm-hang N` | 写完挂 N 秒再写 | 0 |
| `--vm-keep` | 占着内存不释放 | - |
| `--cpu N` | CPU 压力 worker（算素数） | 0 |
| `--io N` | 磁盘 IO worker | 0 |
| `--timeout 60s` | 跑 60 秒自动停 | 永久 |

### Docker 资源限制验证示例

```bash
# 内存限制测试：-m 256m + 想用 512m → OOM
docker run -m 256m tylersmith22/docker-stress-ng --vm 2 --vm-bytes 256m

# CPU 限制测试：--cpus 1 限制只用 1 核
docker run --cpus 1 tylersmith22/docker-stress-ng --cpu 1
```

### 一句话总结
`--vm` = worker 数量，`--vm-bytes` = 每个 worker 内存大小
**总内存压力 = `--vm` × `--vm-bytes`**

> 💡 配合 Docker 资源限制：`-m` 是硬上限，设多少就是多少，超了直接 OOM kill。CPU 限制分硬（`--cpus`）和软（`--cpu-shares`）两种。详见 cloud.md §3.8。

## 25. watch 命令（实时监控面板）

### 是什么
Linux 标准命令（来自 **procps-ng** 包），**周期性执行同一个命令并全屏刷新输出** = 实时监控面板。

- 默认每 **2 秒**执行一次
- 不会滚屏，每次刷新整个屏幕
- 顶部默认显示 `Every 2.0s: <command>` + 当前时间
- **退出**：`Ctrl+C`

### 常用参数
| 参数 | 作用 |
|---|---|
| `-n <秒>` | 刷新间隔（覆盖默认 2s） |
| `-d` / `--differences` | 高亮显示变化的部分 |
| `-t` | 关闭顶部标题行 |

### K8s 场景的经典用法
```bash
watch -n 1 kubectl get pod
```
= 每 1 秒重跑 `kubectl get pod` 并全屏刷新。适合观察 Pod 状态从 `Pending` → `ContainerCreating` → `Running` 的过渡，或者看 Pod 被删除/重启。

**教学常见套路**：
- **滚动更新**：`watch` 一边 + `kubectl set image` 一边 → 看 Pod 一个个被替换
- **Pod 删除**：`watch` 一边 + `kubectl delete pod` 一边 → 看新 Pod 被补上
- **HPA 扩容**：`watch` 一边 + `ab -c 100` 压测一边 → 看 Pod 数量自动增加

### watch vs kubectl -w 的区别
| 方式 | 行为 | 输出方式 |
|---|---|---|
| `watch -n 1 kubectl get pod` | 定期重跑整个命令 | 每次重画整个表格 |
| `kubectl get pod -w` | 只在有变化时输出新行 | 只追加变化行 |

- watch：看整个表（Status / READY / AGE 等所有列）
- kubectl -w：只看事件流（`Pod scheduled`、`Container started`）

生产跟变化用 `-w`，教学盯表用 watch。

### 一句话速记
`watch -n 1 <cmd>` = 每 1 秒重画命令输出，实时监控面板。Ctrl+C 退出。`-d` 高亮变化。

### 相关记忆
- watch 默认 2s 刷新，-n 覆盖间隔
- watch 重画全表，kubectl -w 只追加变化行
- watch 来自 procps-ng 包（包含 ps、top、kill 等经典命令）

---

---
