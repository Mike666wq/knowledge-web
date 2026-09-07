---
id: "kb-cloud-container-foundations"
title: "容器基础与镜像管理"
summary: "容器运行时、Docker/Podman 与镜像构建和仓库。"
category: "云计算"
status: "published"
order: 11
parent: "kb-cloud-containers"
tags: ["container", "image", "docker", "podman"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# 容器基础与镜像管理

## 1. 容器基础概念

### 1.1 容器三大核心概念

```
Containerfile/Dockerfile   ←  配方（怎么装软件、配什么环境）
        ↓ podman build
      镜像 (Image)          ←  打包好的成品（只读，不动）
        ↓ podman run
     容器 (Container)       ←  跑起来的实例（活的，占内存）
```

| 概念 | 定义 | 类比 |
|------|------|------|
| **Containerfile / Dockerfile** | 镜像构建脚本，写清楚要什么材料、怎么做 | 菜谱 |
| **镜像 (Image)** | 只读模板，包含 OS 基础层 + 软件 + 配置文件，存在本地磁盘上，一个镜像可同时跑多个容器 | 做好的菜，放冰箱里不动 |
| **容器 (Container)** | 镜像跑起来的实例，在镜像基础上加可写层，占用 CPU 和内存 | 餐桌上正在吃的那盘菜 |

**核心要点：**
- 镜像是**只读**的，容器是**可写**的（在镜像上加一层可写层）
- 一个镜像可以同时跑多个容器
- 镜像存磁盘，容器占内存

---

### 1.2 容器运行时（Container Runtime）

**容器运行时**：真正负责把容器跑起来的那一层（创建 namespace、cgroup、挂载 rootfs、启动进程）。

| 运行时 | 简介 | 特点 | 适用场景 |
|--------|------|------|----------|
| **LXC**（Linux Containers） | 早期容器运行时，用 Linux 内核的 Namespace 和 Cgroup 实现进程隔离和资源管理 | 提供完整 Linux 系统环境；支持多种 Linux 发行版；早期 Docker 曾用 LXC 作为默认运行时 | 需要完整 Linux 系统环境的容器化应用 |
| **Runc** | 目前 Docker 默认的容器运行时，轻量级 CLI 工具，用于运行和管理容器 | 完全遵循 OCI Runtime Spec；轻量级高性能；是许多容器运行时的底层实现 | 需要高性能和轻量级容器运行环境的场景 |
| **Rkt**（Rocket） | CoreOS 开发的容器运行时，提供安全、可靠且符合 OCI 规范的运行环境 | 独立运行时，不依赖 Docker 守护进程；通过 AppArmor 和 SELinux 提供更好的安全性 | 对安全性要求较高的容器化应用 |
| **Podman** | Red Hat 开发的下一代容器运行时，RHEL 8/9 默认容器工具，RHCSA/RHCE 2026 官方指定 | 无守护进程（Daemonless）；Rootless 原生支持；完全兼容 Docker CLI；原生支持 Pod 概念；`podman generate systemd` 一键集成 systemd | RHEL/CentOS 环境的无守护进程容器、rootless 安全容器、RHCSA/RHCE 考试 |

**Podman 关键特性详解：**

- **无守护进程（Daemonless）**：直接通过 runc 运行容器，不需要 Docker 那种常驻后台进程，部署更轻量、启动更快、故障域更小
- **Rootless 原生支持**：普通用户无需 root 权限就能运行容器，安全性更高（考试场景的核心要求）
- **完全兼容 Docker CLI**：`alias docker=podman` 即可无缝切换；同时支持 Docker 镜像（docker.io）和 Podman 默认（localhost）
- **原生 Pod 概念**：除了单容器，还能管理 Pod（一组共享网络/存储的容器），与 K8s 的 Pod 概念对齐
- **Systemd 集成**：`podman generate systemd` 一键把容器转成 systemd 服务，开机自启很方便

**一句话选型：**
- 学习/考试（RHCSA/RHCE 2026）：选 Podman
- 个人开发/快速上手：选 Docker（生态成熟）
- 生产 RHEL 环境：选 Podman（无 daemon、rootless 安全）
- 已有 Docker Compose 大量配置：继续用 Docker，或 podman-compose 平迁

---

### 1.3 Docker vs Podman

| 特性 | Docker | Podman |
|------|--------|--------|
| **架构** | C/S 架构（需要 daemon 守护进程） | 无守护进程（直接通过 runc） |
| **Rootless** | 需要额外配置 | 原生支持（推荐） |
| **CLI 兼容性** | 自己的命令 | **完全兼容** Docker 命令（别名 `alias docker=podman`） |
| **RHEL 推荐** | ❌ | ✅（RHCSA/RHCE 考试用 podman） |
| **配置文件** | `/etc/docker/daemon.json` | `/etc/containers/registries.conf` |
| **镜像构建** | `docker build` | `podman build`（用 Containerfile 或 Dockerfile） |
| **镜像命名** | `docker.io/xxx` | `localhost/xxx`（默认） |

**考试场景**：RHCSA/RHCE 2026 改用 **Podman**，所有容器操作都用 `podman` 命令。

---

### 1.4 镜像构建隔离性（Build once, run anywhere）

#### 构建时：pip 包装到镜像里，与物理机隔离

**问题：** `pip install -r requirements.txt` 装的包是下载到镜像里吗？和物理机隔离吗？

**答案：** 都对 ✅

**构建过程：**
1. `docker build` 启动临时容器
2. 在临时容器内执行 `RUN pip install`
3. 包安装到容器的 `/usr/local/lib/python3.x/site-packages/`
4. 临时容器销毁，结果**冻结成一层固化到镜像**

**两个核心点：**
1. **下载到镜像里**：装的包是镜像文件系统的一部分，可 `docker save/load` 分发
2. **与物理机隔离**：物理机没装 Python 也能跑，装了不同版本也不冲突

#### 原理：分层文件系统 UnionFS

- 镜像多层叠加（基础镜像层 → COPY → pip install → ...）
- 容器在最上面加**可写层**
- 容器看到的是所有层的**合并视图**
- 物理机原生文件系统**不参与**

#### 不隔离会怎样？

| 场景 | 冲突结果 |
|------|----------|
| 物理机 Python 3.9，容器想用 3.12 | ❌ 版本冲突 |
| 物理机包 A v1.0，容器想用 v2.0 | ❌ 包冲突 |
| 项目 A 依赖 X v1，项目 B 依赖 X v2 | ❌ 多项目依赖冲突 |

#### 核心结论

> **镜像 = 应用 + 依赖 + 运行时 + 配置，全部打包。**
> 物理机只负责 Linux 内核 + Docker daemon。
> 这就是 **Build once, run anywhere** 的核心。

**一句话总结：** 构建时临时容器内 RUN，pip 包装到镜像某一层；运行时容器看到的 Python 和包都是镜像里的，和物理机完全隔离。

---

## 2. 镜像管理

### 2.1 镜像仓库配置

**配置文件：`/etc/containers/registries.conf`**

#### 模板一（Toml 格式，RHCSA 考试用）

```toml
unqualified-search-registries = ["registry.lab.example.com"]

[[registry]]
location = "registry.lab.example.com"
insecure = true
blocked = false
```

| 参数 | 含义 |
|------|------|
| `unqualified-search-registries` | 不带域名前缀时默认搜索的仓库 |
| `insecure = true` | 允许 HTTP 连接（考试内网无证书） |
| `blocked = false` | 不阻止该仓库 |

#### 模板二（INI 格式，RHCE ansible-navigator 用）

```toml
# /etc/containers/registries.conf
[registries.search]
registries = ['utility.lab.example.com']

[registries.insecure]
registries = ['utility.lab.example.com']
```

---

### 2.2 构建镜像

```bash
# 完整流程（sashat 用户）
ssh sashat@servera

# 1. 下载 Containerfile
wget http://content.example.com/Containerfile

# 2. 登录镜像仓库
podman login registry.lab.example.com
# Username: admin / Password: 321

# 3. 构建镜像
podman build -t modify_file:latest .
#                                    ^ 点不能忘！

# 4. 查看构建结果
podman images
```

**`podman build` 关键参数：**

| 参数 | 含义 |
|------|------|
| `-t NAME:TAG` | 指定镜像名和标签 |
| `.` | 构建上下文（当前目录），**漏掉会报错** |
| `-f Containerfile路径` | 指定 Containerfile 路径（默认当前目录） |

---

### 2.3 镜像导入/导出/标签/推送

```bash
# 1. 从 tar 包导入镜像
podman load < rsyslog.tar
# ⚠️ 用 < 重定向读取，不能直接跟文件名

# 2. 打标签（镜像名必须匹配仓库地址）
podman image tag localhost/rsyslog:latest \
  registry.lab.example.com/library/rsyslog:latest

# 3. 登录仓库
podman login registry.lab.example.com

# 4. 推送到仓库
podman push registry.lab.example.com/library/rsyslog:latest

# 5. 拉取远程镜像
podman pull registry.lab.example.com/library/watch:latest

# 6. 搜索镜像（确认路径）
podman search registry.lab.example.com watch
```

**镜像命名格式：**
```
[仓库地址/][命名空间/]镜像名[:标签]
localhost/rsyslog:latest                          # 本地镜像
registry.lab.example.com/library/rsyslog:latest  # 远程仓库
```

---

### 2.4 删除远程 Registry 中的错误镜像

**问题场景**：tag 错了本地镜像，push 到了远程 registry，需要删除

```bash
# 方法1：skopeo 删除（推荐）
skopeo delete --force docker://registry.lab.example.com/library/rsyslog:latest

# 方法2：curl 调 Registry API 删除
DIGEST=$(skopeo inspect docker://registry.lab.example.com/library/rsyslog:latest \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['Digest'])")
curl -X DELETE -k https://registry.lab.example.com/v2/library/rsyslog/manifests/$DIGEST

# 本地取消 tag
podman rmi -f <image>
```

⚠️ **前提条件**：Registry 需要开启 delete 功能（`storage.delete.enabled: true`），否则返回 405。

---

### 2.5 rm vs rmi（常考易混点）

| 命令 | 用途 | 删除对象 |
|------|------|----------|
| `podman rm` | 删除**容器** | 运行中/已停止的容器 |
| `podman rmi` | 删除**镜像**（i = image） | 镜像 |

```bash
podman rmi localhost/rsyslog:latest     # 删除单个镜像
podman rmi --all                        # 删除所有镜像
podman images                           # 确认镜像已删除
```

---

### 2.6 `docker build` 命令详解

**命令**：`docker build -t web_game:v1 .`

**参数拆解：**

| 部分 | 含义 |
|------|------|
| `docker build` | 根据 Dockerfile 构建镜像 |
| `-t web_game:v1` | 打标签，格式 `镜像名:版本`（不写 tag 默认 `:latest`） |
| `.` | **构建上下文路径**（build context）= 当前目录 |

⚠️ **重要：`.` 不是单纯的"当前目录"**

**真实含义**：把当前目录下的所有内容打包，发给 Docker daemon，作为构建上下文的根。

Dockerfile 里 `COPY` / `ADD` 的源路径都相对这个上下文根：

```dockerfile
COPY . /app           # 把上下文根下所有文件 → 容器 /app
COPY ./src /app/src   # 上下文根/src → 容器 /app/src
```

**坑**：如果当前目录有 .git、node_modules、.env，构建会：
1. 慢（大文件全发给 daemon）
2. **泄露**（.env、密钥可能被打进镜像）

**解决**：在构建目录加 `.dockerignore`（语法同 .gitignore）：

```
.git
node_modules
*.log
.env
target/
__pycache__/
```

**不打 `-t` 会怎样？** 构建完只有临时镜像 ID（`<none>:<none>`），操作起来很麻烦。

**常用参数：**

| 参数 | 含义 |
|------|------|
| `-f` / `--file Dockerfile.dev` | 指定 Dockerfile 路径（默认 `./Dockerfile`） |
| `--build-arg KEY=***` | Build 参数（对应 Dockerfile 里 ARG） |
| `--no-cache` | 不用构建缓存，强制全重编 |
| `--pull` | 总是拉最新基础镜像（避免用本地过期缓存） |
| `--target dev-stage` | 多阶段构建选阶段 |
| `-t name:v1 -t name:latest` | 一次打多个标签 |

**完整流程示例：**

```bash
# 目录结构
.
├── Dockerfile
├── .dockerignore
├── app.py
└── requirements.txt

docker build -t web_game:v1 .
docker images | grep web_game
docker run -d -p 8080:8080 --name web web_game:v1
```

---

### 2.7 镜像与容器元数据（`docker inspect`）

#### 2.7.1 `docker inspect` 基础

**用途**：查任何 docker 对象的详细元数据，返回 JSON。**默认刷屏，配合 `-f` 用 Go template 取单字段才是日常姿势**。

**支持 inspect 的对象：**

```bash
docker inspect nginx:1.27          # 镜像
docker inspect web                  # 容器
docker inspect bridge mynet         # 网络
docker inspect myvol                # 卷
docker inspect node1                # swarm 节点
```

**后接镜像：看的是「静态构建信息」**

| 字段 | 含义 |
|------|------|
| `Id` | 完整 SHA256 |
| `RepoTags` | 所有 tag |
| `RepoDigests` | 所有 digest（内容寻址） |
| `Created` | **镜像构建时间**（不是 pull 时间） |
| `Architecture` / `Os` | 架构、系统 |
| `Size` | 压缩后所有层总和（byte） |
| `RootFS.Layers` | 每层 SHA256（构建顺序） |
| `Config` | 镜像「运行配置」（建好就定了）：`Cmd`、`Entrypoint`、`Env`、`WorkingDir`、`ExposedPorts`、`Volumes`、`Labels` |

**后接容器：看的是「静态 + 运行时」**

容器比镜像多了一堆**运行时状态**：

| 字段 | 含义 |
|------|------|
| `State.Status` | running/exited/paused/restarting/dead |
| `State.Pid` | 容器 PID 1 在宿主机的进程号（debug 用） |
| `State.ExitCode` | 上次退出码（exited 时看） |
| `State.OOMKilled` | 是否被 OOM 杀掉 |
| `Mounts` | 所有挂载点（type/source/destination） |
| `NetworkSettings` | IP、Gateway、Ports（端口映射） |
| `HostConfig` | 启动时的资源/策略（内存/CPU/重启策略/日志驱动） |
| `LogPath` | 日志文件路径 |
| `Env` | 环境变量 |

**核心：`-f` Go template 用法（重点记）**

| 写法 | 含义 |
|------|------|
| `&#123;&#123;.Id&#125;&#125;` | 取顶层字段 |
| `&#123;&#123;.State.Pid&#125;&#125;` | 嵌套字段（点路径） |
| `&#123;&#123;json .Mounts&#125;&#125;` | 转 JSON（接 jq 美滋滋） |
| `&#123;&#123;range .X&#125;&#125;&#123;&#123;.Y&#125;&#125;&#123;&#123;end&#125;&#125;` | 遍历数组/切片 |
| `&#123;&#123;range .X&#125;&#125;&#123;&#123;println .&#125;&#125;&#123;&#123;end&#125;&#125;` | 每行打一项 |
| `&#123;&#123;index .X "key"&#125;&#125;` | map 取值 |

**容器常用 `-f` 例子：**

```bash
# 查容器 IP（最常用）
docker inspect -f '&#123;&#123;range .NetworkSettings.Networks}}&#123;&#123;.IPAddress}}&#123;&#123;end}}' web

# 查主进程 PID
docker inspect -f '&#123;&#123;.State.Pid}}' web

# 查所有挂载点
docker inspect -f '&#123;&#123;json .Mounts}}' web | jq .

# 查退出码（排查为什么起不来）
docker inspect -f '&#123;&#123;.State.ExitCode}}' web

# 查 OOM
docker inspect -f '&#123;&#123;.State.OOMKilled}}' web

# 查端口映射
docker inspect -f '&#123;&#123;json .NetworkSettings.Ports}}' web | jq .
```

**镜像常用 `-f` 例子：**

```bash
# 完整 SHA256
docker inspect -f '&#123;&#123;.Id}}' nginx:latest

# 默认 CMD
docker inspect -f '&#123;&#123;json .Config.Cmd}}' centos:7

# ENTRYPOINT
docker inspect -f '&#123;&#123;json .Config.Entrypoint}}' nginx:1.27

# 所有环境变量
docker inspect -f '&#123;&#123;range .Config.Env}}&#123;&#123;println .}}&#123;&#123;end}}' nginx:1.27

# 所有 tag
docker inspect -f '&#123;&#123;json .RepoTags}}' nginx:1.27

# 所有层
docker inspect -f '&#123;&#123;range .RootFS.Layers}}&#123;&#123;println .}}&#123;&#123;end}}' nginx:1.27
```

**实战排查三连（背下来）：**

```bash
# 容器起不来三连：
docker ps -a | grep web                                # 1. 看在不在
docker logs --tail 50 web                              # 2. 看日志
docker inspect -f '状态=&#123;&#123;.State.Status}} 退出码=&#123;&#123;.State.ExitCode}} OOM=&#123;&#123;.State.OOMKilled}}' web  # 3. 看状态

# 端口映射没生效？
docker inspect -f '&#123;&#123;json .NetworkSettings.Ports}}' web | jq .

# 环境变量问题排查
docker inspect -f '&#123;&#123;range .Config.Env}}&#123;&#123;println .}}&#123;&#123;end}}' web
```

#### 2.7.2 `GraphDriver.Data` 消失问题（Docker 版本演进）

**现象**：老教程里 `docker inspect centos:7` 输出长这样：

```json
"GraphDriver": {
  "Data": {
    "MergedDir": "/var/lib/docker/overlay2/xxx/merged",
    "UpperDir":  "/var/lib/docker/overlay2/xxx/diff",   ← 可写层
    "WorkDir":   "/var/lib/docker/overlay2/xxx/work",
    "LowerDir":  "/var/lib/docker/overlay2/.../diff"
  },
  "Name": "overlay2"
}
```

**但新版只看到 RootFS，没有 GraphDriver.Data**：

```json
"RootFS": {
  "Type": "layers",
  "Layers": ["sha256:174f56854..."]   ← 只有这一条
}
```

**原因：Docker 迁移到 containerd snapshotter**

Docker 25.0 起开始迁移到 containerd snapshotter（新版镜像存储系统），到 27/28 版完成。

新版用 snapshotter 管理内容存储，**不再暴露 overlay2 的文件系统路径**。`/var/lib/docker/overlay2/<id>/` 这种老路径可能整个没了。

**老版本四件套含义：**

| 字段 | 含义 |
|------|------|
| `UpperDir` | 容器运行时产生的可写层 |
| `LowerDir` | 镜像所有只读层的合并视图 |
| `MergedDir` | Lower + Upper 联合挂载出来的虚拟合并盘 |
| `WorkDir` | overlay2 内部工作目录（atomic rename 用） |

**版本差异对比：**

| 项 | 老版 overlay2 | 新版 snapshotter |
|----|---------------|------------------|
| 路径 | `/var/lib/docker/overlay2/<id>/` | snapshotter 统一管理，不公开 |
| inspect | `GraphDriver.Data` 有四件套 | 只有 `RootFS.Layers` |
| 进 MergedDir 翻文件 | ✅ 可以 | ❌ 普通方法不行 |
| 启动速度 | 一般 | 略快（lazy pull、按需加载） |

**验证自己用的是哪个版本：**

```bash
docker version                                                    # client & server 版本
docker info | grep -i "storage driver"                            # 看 storage driver 关键！
ls /var/lib/docker/                                               # 新版可能没 overlay2/ 目录
```

**这影响什么？**

1. **直接进 MergedDir 翻文件**这条老技巧死了
2. **想看镜像内文件的新办法**：

   ```bash
   # 方法 1：临时容器看
   docker run --rm -it centos:7 ls /etc/

   # 方法 2：create + cp
   docker create --name tmp centos:7
   docker cp tmp:/etc/passwd /tmp/passwd
   docker rm tmp

   # 方法 3：dive 工具（强烈推荐）
   dive centos:7
   ```

3. **别再按老教程查 `/var/lib/docker/overlay2/`**——查不到

---
