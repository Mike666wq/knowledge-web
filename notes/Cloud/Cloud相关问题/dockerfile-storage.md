---
id: "kb-cloud-dockerfile-storage"
title: "Dockerfile 与容器存储清理"
summary: "Dockerfile 指令、镜像存储、空间分析和安全清理。"
category: "云计算"
status: "published"
order: 16
parent: "kb-cloud-containers"
tags: ["dockerfile", "storage", "cleanup"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# Dockerfile 与容器存储清理

## 12. Dockerfile 指令详解（ENV / ADD / EXPOSE / CMD）

### 12.1 ENV 指令详解

**语法：**
```dockerfile
ENV <key>=<value> ...
```

**两个阶段都可用：**
- **构建时**：RUN / CMD / ENTRYPOINT 里用 `$VAR` 引用
- **运行时**：作为环境变量传给容器内进程

**ENV vs ARG 对比：**

| 指令 | 构建时 | 运行时 |
|------|--------|--------|
| `ENV` | ✅ 可用 | ✅ 可用 |
| `ARG` | ✅ 可用 | ❌ 不可见 |

**实战 Dockerfile 解析（ubuntu:26.04 sshd 镜像）：**

```dockerfile
FROM ubuntu:26.04
ENV DEBIAN_FRONTEND=noninteractive  # apt 隐性读取
ENV TZ=Asia/Shanghai                # 显式 $TZ + 运行时透传
ENV APP_VERSION=v1.0                # 只运行时给程序读
RUN apt update \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo "$TZ" > /etc/timezone \
 && apt install -y vim net-tools openssh-server iputils-ping iproute2 python3 \
 && sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin/" /etc/ssh/sshd_config \
 && echo 'root:1' | chpasswd \
 && apt clean
EXPOSE 22 8000                       # 只是文档声明，不真发布端口
CMD ["/usr/sbin/sshd", "-D"]         # 前台启动 sshd
```

**三个 ENV 实际用法区分：**
1. `DEBIAN_FRONTEND=noninteractive` — apt 工具**自动读取**（约定俗成的隐性引用）
2. `TZ=Asia/Shanghai` — Dockerfile 里**显式 `$TZ`** 设置时区 + 运行时透传给应用
3. `APP_VERSION=v1.0` — Dockerfile 里**不引用**，只在运行时给应用程序读

**运行时验证：**
```bash
docker exec -it <容器> env                # 查看所有环境变量
docker exec -it <容器> echo $APP_VERSION  # 输出 v1.0
```

### 12.2 ADD 指令详解

**语法：**
```
ADD <src> <dest>
```

**src 源路径：**
- 必须在构建上下文（`docker build` 的目录）内
- **不能写系统绝对路径**（如 `/etc/passwd`）
- 类型：文件、目录、相对路径、URL、通配符

**dest 目标路径：**
- 必须是**容器内绝对路径**
- 不能是相对路径

**结尾斜杠的关键差别（重点）：**

| 写法 | 结果 |
|------|------|
| `ADD mydir /app/` | 把 mydir 的**内容**放进 /app/（不含 mydir 这一层） |
| `ADD mydir /app`  | 把 mydir **放到** /app 下，结果是 /app/mydir/ |

**ADD 的特殊功能（COPY 没有）：**
1. **自动解压 tar 文件**：`ADD archive.tar.gz /app/`
2. **URL 下载**：`ADD https://example.com/file /tmp/`（不推荐，建议用 RUN curl）

### 12.3 ADD vs COPY

| 维度 | ADD | COPY |
|------|-----|------|
| 基础复制 | ✅ | ✅ |
| 自动解压 tar | ✅ | ❌ |
| URL 下载 | ✅ | ❌ |
| 官方推荐度 | 需要解压/下载才用 | **能 COPY 就 COPY** |

**官方建议：能 COPY 就 COPY，需要解压 tar 或下载时才用 ADD。**

### 12.4 EXPOSE 真相

**只是文档声明**，告诉用户端口用途，**不会真发布端口**，必须 `docker run -p` 映射才生效。

```dockerfile
EXPOSE 22 8000    # 仅文档作用，实际发布靠 -p
```

### 12.5 CMD vs ENTRYPOINT（速记）

| 指令 | 作用 | docker run 后参数会怎样 |
|------|------|-------------------------|
| `CMD` | 默认启动命令 | **被覆盖** |
| `ENTRYPOINT` | 固定入口 | 作为参数**追加**给 ENTRYPOINT |

## 13. Docker 镜像存储位置 & 空间清理



### 默认存储位置

- 根目录：`/var/lib/docker/`
- 镜像层（按存储驱动）：
  - overlay2（现代默认）：`/var/lib/docker/overlay2/`
  - aufs（旧）：`/var/lib/docker/aufs/`
  - devicemapper（旧）：`/var/lib/docker/devicemapper/`

/var/lib/docker/ 子目录：
```
overlay2/   ← 镜像和容器层都在这（最大头）
image/      ← 镜像元数据
volumes/    ← 匿名卷
containers/ ← 容器元数据
network/    ← 网络配置
tmp/
```

### 查看空间占用

```bash
# 一键看 docker 占的各类资源
docker system df

# TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
# Images          18        5         8.732GB   4.512GB (51%)
# Containers      8         2         1.234GB   987.5MB (80%)
# Local Volumes   12        4         567.8MB   123.4MB (21%)
# Build Cache     0         0         0B        0B

docker system df -v   # 详细模式

# 看具体根目录
docker info | grep "Docker Root Dir"
# Docker Root Dir: /var/lib/docker

# 系统层看大小
du -sh /var/lib/docker/
du -sh /var/lib/docker/*/
```

### Docker 占空间的四类

1. **Images** - 拉下来的镜像
2. **Containers** - 创建过的容器层（rm 后还在）
3. **Local Volumes** - 容器卷
4. **Build Cache** - build 中间层（不用 build 几乎不占）

---

### 清理命令（按风险从小到大）

#### 1. 清 dangling 镜像（标签 `<none>`）

```bash
# dangling = 无主镜像，build 中间产物
docker images
# REPOSITORY   TAG       IMAGE ID
# <none>       <none>    abc123...  ← 这种

docker image prune      # 清 dangling
docker image prune -a   # 清 dangling + 所有无用的已命名镜像
```

#### 2. 激进清（全清）

```bash
docker system prune         # 清停止的容器/无用网络/dangling/构建缓存
docker system prune -a      # 上面的 + 所有未被容器用的镜像
# ⚠️ -a 威力大，会删 php:7.4-fpm 等没起容器的镜像
```

#### 3. 按时间条件

```bash
docker image prune -a --filter "until=24h"    # 24h 前
docker image prune -a --filter "until=168h"   # 7 天前
docker builder prune --filter "until=24h"     # 构建缓存
```

#### 4. 单独清某种资源

```bash
docker container prune   # 停止的容器
docker volume prune      # 无主卷   ⚠️ 会丢数据
docker network prune     # 无用网络
```

---

### 这台 LNMP 架构主要吃的空间

| 资源 | 估算 | 处理建议 |
|------|------|----------|
| php:7.4-fpm | ~400MB | image prune -a |
| nginx:latest | ~180MB | image prune -a |
| mysql:5.7 | ~500MB | 镜像大但常驻，清了还得拉 |
| redis:7.4 | ~130MB | 同上 |
| 容器停止后的层 | 几百 MB | system prune 一次清掉 |
| dangling 镜像 | 看 build 频率 | image prune 必清 |

没用 Dockerfile build，**构建缓存基本不占**。

**直接 `docker system prune -a` 通常能回收 2-3GB。**

---

### 搬 docker 到大盘（操作前要老大同意）

```bash
# 1. 停 docker
systemctl stop docker

# 2. 同步到新盘（不是 mv，保留权限）
rsync -aP /var/lib/docker/ /mnt/newdisk/docker/

# 3. 改配置
vim /etc/docker/daemon.json
```

```json
{
  "data-root": "/mnt/newdisk/docker"
}
```

```bash
# 4. 起回去
systemctl start docker

# 5. 确认
docker info | grep "Docker Root Dir"
```

⚠️ **改 docker 根目录属于"系统/服务改动"，按 MEMORY 铁律必须先经老大同意。**

---

---

## 14. `docker system df` 输出解读



### 不是定死的

`docker system df` 的 SIZE 是**当下实际占硬盘多少字节**，每次执行现算的。

### 字段含义

```bash
TYPE            TOTAL  ACTIVE  SIZE       RECLAIMABLE
Images          14     0       7.845GB    7.061GB (90%)
Containers      0      0       0B         0B
Local Volumes   2      0       206.9MB    206.9MB (100%)
Build Cache     41     0       1.5GB      482.8MB
```

| 列 | 含义 |
|----|------|
| TYPE | 资源类型 |
| TOTAL | 此类型总个数（含使用 + 未使用） |
| ACTIVE | **正在被用**的资源数（容器在跑/镜像被任何容器引用） |
| SIZE | 实际占磁盘字节数（动态算的） |
| RECLAIMABLE | prune 后能省下多少 |

### RECLAIMABLE 怎么算

| 类型 | 啥算"可回收" |
|------|--------------|
| Images | 没被**任意**容器引用（running/stopped 都不算占用） |
| Containers | 状态是 exited/dead |
| Volumes | 没被**任意**容器挂载 |
| Build Cache | **永远可回收**（下次 build 重生成） |

⚠️ **坑**：Container stopped 状态占的层**不会自动释放**，要 `docker container prune` 或 `docker rm` 才释放。

### SIZE 何时变化

| 操作 | SIZE 变化 |
|------|-----------|
| `docker pull xxx` | Images ↑ |
| `docker run xxx` 容器内写文件 | Containers ↑ |
| `docker stop` 容器 | Container SIZE 不变 |
| `docker rm -f` | Container SIZE 可能**不立即变小**（layer 在 overlay） |
| `docker compose up -d --build` | Build Cache ↑ |
| `docker image prune -a` | Images ↓ |
| `docker system prune` | 各类 ↓ |

**"用过的就还占着"，prune 才释放。**

---

### ACTIVE 全 0 的解读

```bash
# 输出里 ACTIVE 全是 0 意味着：
# - 14 个镜像没一个被容器引用
# - 2 个卷没一个被容器挂载
# - build cache 41 个最近没 build
```

**不正常** —— LNMP 项目跑着的话 LB01/web01 的容器应该在 ACTIVE > 0。

可能情况：
- 跑完实验后 `docker stop` + `docker rm` 全清过，镜像留着没删
- dockge 项目本身就在这目录，但容器没起来
- 看的是另一台机器

### 清理前 ⚠️ 检查 volumes 不是数据库

**mysql/redis 的数据如果在 volumes 里，prune 一下全没！** 项目用的是 `-v` bind mount，不容易踩这坑，但 anonymous 卷（没用 -v 也没用 named volume）可能产生。

```bash
docker volume ls
docker volume inspect <卷名> | grep Mountpoint
ls /var/lib/docker/volumes/<卷名>/_data/
# 看到 mysql/ redis 文件夹 → ⚠️ 是数据库数据，不能清
```

### 这个场景的清理顺序

ACTIVE 全 0 → 全清风险低：

```bash
# 1. 清镜像和 dangling
docker image prune -a          # 释放 ~7GB

# 2. 清 build cache
docker builder prune           # 释放 ~0.5GB

# 3. 清无主卷（要先确认不是数据库）
docker volume prune            # 释放 ~0.2GB

# 4. 看效果
docker system df
```

清理完理论上 SIZE 总和 **9.7GB → 1GB 以内**。

---



> 💡 **一句话：** SIZE 是当下实际占盘字节数（动态算）；RECLAIMABLE 是理论值，跑了 prune 才真释放；ACTIVE 0 是异常信号；Volumes prune 前必查 Mountpoint 别误清数据库。

---
