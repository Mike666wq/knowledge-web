---
id: "kb-cloud-container-operations"
title: "容器运行与生命周期"
summary: "容器启动、进入、端口、资源限制和批量管理。"
category: "云计算"
status: "published"
order: 12
parent: "kb-cloud-containers"
tags: ["docker", "podman", "lifecycle"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# 容器运行与生命周期

## 3. 容器操作

### 3.1 运行容器（`podman run`）

```bash
# 创建挂载目录
mkdir /home/sashat/syslog

# 运行容器（带特权模式和卷挂载）
podman run -d --privileged \
  -v /home/sashat/syslog:/var/log:Z \
  --name logserver \
  registry.lab.example.com/library/rsyslog:latest
```

**`podman run` 核心参数：**

| 参数 | 含义 |
|------|------|
| `-d` | 后台运行（detach） |
| `--privileged` | 特权模式，允许容器访问宿主机设备 |
| `-v 宿主机:容器:Z` | 挂载目录，`:Z` 为 SELinux 标签（**必须加，不加 SELinux 会拒访**） |
| `--name NAME` | 给容器命名（不加会随机生成） |
| `-it` | 交互模式 + 伪终端（用于 `exec` 进入容器） |
| `-p 主机端口:容器端口` | 端口映射 |
| `--rm` | 容器退出后自动删除（**不能和 `-d` 同时用**） |
| `-e KEY=VALUE` | 设置环境变量 |

#### 3.1.1 `docker run` 详解

**语法**：`docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`

**参数拆解（以 `docker run -itd centos:7` 为例）：**

| 参数 | 含义 |
|------|------|
| `-i`（`--interactive`） | 保持 STDIN 打开，没附加终端也能往容器里输东西 |
| `-t`（`--tty`） | 分配伪终端（pseudo-TTY），让容器以为自己在和 shell 对话（提示符、颜色等） |
| `-d`（`--detach`） | 后台模式，启动后立刻把终端还给你，只输出容器 ID |

**-itd 组合含义**：后台启动一个交互式容器（不阻塞终端），但保留交互能力，给之后 `docker exec -it` 进去用。

**典型场景**：起一个后台运行的开发环境，需要时 `docker exec -it <id> bash` 进去操作（vim、mysql 客户端这种需要 TTY 的命令才好用）。

```bash
docker run -itd --name mydev centos:7
docker exec -it mydev bash
```

⚠️ **踩坑提醒**：`centos:7` 在 2024 EOL 后，国内大部分镜像站已清理该镜像。能用是有老缓存或特定源还有，新机器 `pull` 大概率失败。

**`docker run` 常用参数大全：**

| 类别 | 参数 | 含义 |
|------|------|------|
| 🏷️ 基础 | `--name xxx` | 给容器起名（不写随机） |
| 🏷️ 基础 | `--rm` | 容器退出后自动删除（一次性任务用） |
| 🏷️ 基础 | `--hostname xxx` | 容器内主机名 |
| 🏷️ 基础 | `--restart no\|on-failure[:max]\|always\|unless-stopped` | 重启策略 |
| 🌐 网络 | `-p / --publish 宿主机:容器[:协议]` | 端口映射（如 `-p 8080:80`、`-p 53:53/udp`） |
| 🌐 网络 | `-P / --publish-all` | 自动映射所有 EXPOSE 端口到随机端口 |
| 🌐 网络 | `--network bridge\|host\|none\|container:xxx\|mynet` | 网络模式 |
| 🌐 网络 | `--add-host=host:ip` | 往 `/etc/hosts` 塞条目 |
| 🌐 网络 | `--dns 8.8.8.8` | 指定 DNS |
| 💾 存储 | `-v /host:/container` | 路径挂载 |
| 💾 存储 | `-v vol:/data` | 具名卷挂载（推荐用于持久化数据） |
| 💾 存储 | `--mount type=bind/tmpfs/volume,...` | `-v` 的规范写法 |
| 💾 存储 | `--tmpfs /path` | 临时文件系统（数据存内存） |
| 💾 存储 | `--read-only` | 根文件系统只读 |
| ⚙️ 环境 | `-e KEY=VALUE` | 设置环境变量 |
| ⚙️ 环境 | `--env-file .env` | 从文件批量读环境变量 |
| ⚙️ 环境 | `-w /app` | 工作目录 |
| ⚙️ 环境 | `-u 1000:1000` / `-u root` | 运行用户（避免用 root 是最便宜的安全加固） |
| ⚙️ 资源 | `--cpus 1.5` | CPU 核数限制 |
| ⚙️ 资源 | `-m 512m` | 内存限制 |
| ⚙️ 资源 | `--memory-swap -1` | swap 限制（-1 = 不限） |
| ⚙️ 资源 | `--cpuset-cpus 0,1` | 绑死特定 CPU |
| 🔐 安全 | `--privileged` | 特权模式（慎用，几乎能调所有内核接口） |
| 🔐 安全 | `--cap-add NET_ADMIN` | 增加 capability |
| 🔐 安全 | `--cap-drop ALL` | 去掉所有 capability（最小权限） |
| 🔐 安全 | `--security-opt seccomp=unconfined` | seccomp/apparmor |
| 🔐 安全 | `--user` | 跑非 root 用户（首选安全措施） |
| 🪵 日志 | `--log-driver json-file\|syslog\|fluentd` | 日志驱动 |
| 🪵 日志 | `--log-opt max-size=10m` | 日志驱动参数（用于切割） |
| 🪵 日志 | `--entrypoint /bin/sh` | 覆盖镜像默认入口 |

**实战模板：**

```bash
# 起后台的交互式开发环境
docker run -itd --name dev -v /root/work:/work centos:7

# 一次性前台命令
docker run -it --rm centos:7 cat /etc/redhat-release

# 长期跑的服务（自启 + 资源限制）
docker run -d --name web --restart unless-stopped -p 80:80 -m 256m --cpus 1 nginx:latest

# 跨容器通信（自定义网络）
docker network create mynet
docker run -d --name db --network mynet -e MYSQL_ROOT_PASSWORD=123 mysql:8
docker run -d --name web --network mynet -p 8080:8080 myapp
```

#### 3.1.2 `docker run` 最后的 `/usr/sbin/nginx` 是啥？

**完整语法**：`docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`

镜像名之后的所有位置参数，都是**给容器执行的进程**（不是挂载、不是参数）。

```bash
docker run -d -p 80:80 --name my_nginx rocky_nginx:v1 /usr/sbin/nginx
#                       ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^
#                       IMAGE             COMMAND
```

`/usr/sbin/nginx` 就是说容器起来后执行这个二进制，作为容器主进程（PID 1）。

**为什么不写也能跑？** 镜像 Dockerfile 通常定义了默认启动命令：

```dockerfile
ENTRYPOINT ["/usr/sbin/nginx"]   # ENTRYPOINT 形式
CMD ["/usr/sbin/nginx"]          # CMD 形式
```

**什么时候要写命令行版本？**

1. **带自定义参数启动**：`docker run rocky_nginx:v1 /usr/sbin/nginx -g "daemon off;"`
2. **覆盖默认进程（调试）**：`docker run -it --rm rocky_nginx:v1 /bin/bash`
3. **镜像没设 ENTRYPOINT/CMD 时**，必须命令行给命令，否则起不来

**ENTRYPOINT vs CMD vs 命令行：**

- **ENTRYPOINT**：命令行参数作为它的**追加参数**（不容易覆盖）
- **CMD**：命令行参数**整体替换**它
- **都没设**：必须命令行给命令

**跟挂载点 `-v` 的区别：**

```bash
# -v 是路径映射（宿主机 → 容器）
# 最后的 /usr/sbin/nginx 是启动命令
docker run -d \
  -v /root/nginx.conf:/etc/nginx/nginx.conf \
  --name web rocky_nginx:v1 /usr/sbin/nginx
```

一个是**文件映射**，一个是**进程启动**，别混了。

---

### 3.2 进入容器执行命令

```bash
# 进入容器交互式 shell
podman exec -it logserver /bin/bash

# 在容器内执行 logger
logger "This is a rhcsa exam"

# 退出容器
exit
```

**验证：**
```bash
grep rhcsa /home/sashat/syslog/messages        # 看日志是否写到宿主机
skopeo inspect docker://registry.lab.example.com/library/rsyslog:latest  # 查远程镜像信息
```

---

### 3.2.1 `docker exec` 报错 `bash: executable file not found`（瘦身镜像坑）

**报错：**
```bash
$ docker exec -it pv-ac-sim bash
OCI runtime exec failed: exec failed: unable to start container process: exec: "bash": executable file not found in $PATH
```

**结论：是的，大概率是镜像里没 bash。** 这是瘦身镜像（alpine、distroless）的常见坑。

**三大类镜像对照：**

| 镜像类型 | 有 bash？ | 进入命令 |
|---|---|---|
| `ubuntu` / `debian` / `centos` | ✅ | `docker exec -it <容器> bash` |
| `alpine` / `node:alpine` | ❌ 只有 ash | `docker exec -it <容器> sh` |
| `gcr.io/distroless/*` | ❌ **完全没 shell** | 🚫 exec 进去不了 |
| `scratch` | ❌ 空 | 🚫 exec 进去不了 |

**快速判断镜像类型：**
```bash
# 看镜像基础
docker inspect pv-ac-sim | grep -i 'image\|os'

# 看容器里有什么 shell
docker exec pv-ac-sim ls /bin/

# 验证是不是 distroless（连 sh 都没）
docker exec pv-ac-sim sh
# 如果也报 "executable file not found" → distroless，exec 废了
```

**三种解法：**

**① 改用 sh（最快）**
```bash
docker exec -it pv-ac-sim sh
```

**② alpine 装 bash**
```bash
docker exec -it pv-ac-sim apk add bash
docker exec -it pv-ac-sim bash
```
⚠️ 装 bash 不会写回镜像，容器重启就丢。

**③ 改 Dockerfile 用完整镜像（推荐永久）**
```dockerfile
# 从
FROM node:alpine
# 改成
FROM node:20-bookworm   # debian 完整版
```

**distroless 镜像怎么 debug：**
1. **看应用日志**：`docker logs <容器>` / `kubectl logs`
2. **sidecar + shareProcessNamespace**：
   ```yaml
   shareProcessNamespace: true
   ```
   exec 进带 shell 的 sidecar 看主容器进程
3. **临时换镜像**：本地调试用 `node:20-bookworm` 替代 distroless
4. **远程调试**：Node.js 加 `--inspect=0.0.0.0:9229`，Chrome DevTools 连接

**一句话速记：** 瘦身镜像（alpine/distroless）没 bash，先用 `docker exec -it <容器> sh` 试一下；distroless 连 sh 都没有，exec 完全失效，只能靠日志和 sidecar。

---

### 3.3 端口映射 `-p 主机端口:容器端口`

**命令示例：**
```bash
docker run --name nginx_container_test -d -p 8080:80 nginx
```

**参数拆解：**

| 部分 | 含义 |
|------|------|
| `--name nginx_container_test` | 给容器起名字 |
| `-d` | 后台运行 |
| `-p 8080:80` | **端口映射**（8080 = 宿主机，80 = 容器） |
| `nginx` | 用 nginx 镜像 |

**核心原理：**
```
宿主机（你的电脑）        容器（隔离的小盒子）
   8080  ←————— 映射 —————→  80
   ↑                          ↑
   外部访问入口              Nginx 内部监听端口
```

- **8080** = 宿主机端口，外部能访问
- **80** = 容器内部端口，外部访问不到
- Docker 做中转：访问宿主机 8080 → 自动转到容器的 80

**为什么不直接用 80？** 容器是**网络隔离**的，容器内 80 端口外面访问不到，必须通过 `-p` 暴露。而且可以**避免端口冲突**（多容器都用 80，映射到主机不同端口）。

**常用写法：**
```bash
-p 8080:80                  # 指定映射（最常用）
-p 127.0.0.1:8080:80        # 只允许本机访问（绑定指定 IP，更安全）
-P                          # 大写 P：随机映射端口（自动选空闲端口）
```

**查看实际映射：**
```bash
docker port nginx_container_test
# 输出：80/tcp -> 0.0.0.0:8080
```

**实测访问：** `http://localhost:8080`

---

### 3.3.1 端口映射 vs 服务监听端口（核心澄清）

**常见误解：** "docker run -p 8000:8000 已经规定了 8000，所以 python3 -m http.server 不用加端口号" ❌

**真实情况：** 两个 8000 是完全独立的，只是恰好一样：
- `-p 8000:8000` **前面的** 8000 = 主机端口
- `-p 8000:8000` **后面的** 8000 = 容器端口
- `http.server` 默认 8000 = 服务**实际监听的端口**

**端口对应关系（三段链路）：**
```
主机端口  →  Docker 转发  →  容器端口  →  服务监听端口
```

三者必须一致才能通。

**验证例子：**
- `-p 9000:8000 + http.server` ✅ 主机9000 → 容器8000 → 服务8000（默认）
- `-p 9000:7000 + http.server` ❌ 容器7000 没服务监听
- `-p 9000:7000 + http.server 7000` ✅ 显式指定服务端口

**建议写法：** 显式写出端口号更清晰：
```bash
python3 -m http.server 8000
```
虽然默认就是 8000，但显式写不容易出错。

**一句话总结：** 不加端口号能跑是因为 http.server 默认 8000，**和 -p 前面的 8000 没关系**。三个端口要一致：主机端口 → 容器端口 → 服务监听端口。

---

### 3.4 Docker 临时容器（`--rm`）

**场景**：用 Docker 运行一次性容器执行某个操作，容器自动删除。

```bash
# 生成 UUID（以 sing-box 代理工具为例）
docker run --rm ghcr.io/sagernet/sing-box:latest generate uuid
```

| 参数 | 含义 |
|------|------|
| `--rm` | 容器执行完后自动删除，不留垃圾 |
| `ghcr.io/sagernet/sing-box:latest` | Docker 镜像地址（GitHub Container Registry） |
| `generate uuid` | 容器内执行的命令 |

**原理：** Docker 拉取镜像 → 启动容器 → 执行命令 → 输出结果 → 容器自动销毁。

⚠️ **`--rm` 和 `-d` 不能同时用**：`--rm` 在容器退出时删除，`-d` 是后台运行（不会退出）。

---

### 3.5 `docker ps` 与 `ps -qa` 过滤

**命令**：`docker ps -qa`

**参数拆解：**

| 部分 | 含义 |
|------|------|
| `docker ps` | 列出容器（默认只看 running 状态） |
| `-a`（`--all`） | 显示**所有**状态的容器（running/exited/created/restarting 等） |
| `-q`（`--quiet`） | 静默模式，**只输出容器 ID**，不显示容器名、镜像、状态、端口等列 |

**效果**：每行一个容器 ID，覆盖机器上所有容器。

**典型用途**（这个命令几乎都是配合管道/命令替换用）：

```bash
# 停止所有容器
docker stop $(docker ps -qa)

# 删除所有容器（包括运行中的）
docker rm -f $(docker ps -qa)

# 用 xargs 更安全（参数为空时不会报错）
docker ps -qa | xargs -r docker rm -f

# 只删已停止的容器（更精准）
docker ps -qa --filter "status=exited" | xargs -r docker rm
```

**对比速记：**

| 命令 | 含义 |
|------|------|
| `docker ps` | 运行中 + 完整信息 |
| `docker ps -q` | 运行中 + 只 ID |
| `docker ps -a` | 所有 + 完整信息 |
| `docker ps -qa` | 所有 + 只 ID |

**常用 `--filter` 过滤：**

```bash
docker ps --filter "status=running/exited/paused"   # 按状态过滤
docker ps --filter "name=web"                        # 按名称
docker ps --filter "label=env=dev"                    # 按 label（最推荐批量方案）
```

---

### 3.6 容器管理全生命周期（含批量操作）

#### 3.6.1 查看

| 命令 | 含义 |
|------|------|
| `docker ps` | 运行中 |
| `docker ps -a` | 全部（含已停止） |
| `docker ps -qa` | 只显示 ID（配合批量用） |
| `docker ps --filter "status=..."` | 按状态/名称/label 过滤 |
| `docker stats` | 实时资源（CPU/内存/网速） |
| `docker top <id>` | 容器内进程 |
| `docker port <id>` | 端口映射 |

#### 3.6.2 启动 / 重启

| 命令 | 含义 |
|------|------|
| `docker run -d --name web nginx` | 创建 + 启动（一次性） |
| `docker start <id>` | 启动已 stop 的 |
| `docker restart <id>` | 重启（stop + start） |
| `docker restart -t 30 <id>` | 给 30s 缓冲 |

⚠️ `run` vs `start` vs `create`：`run`=创建+启动、`start`=只启动已有、`create`=只创建不启动。

#### 3.6.3 停止 / 关闭

| 命令 | 含义 |
|------|------|
| `docker stop <id>` | 发 SIGTERM → 等 10s → SIGKILL（优雅停） |
| `docker stop -t 30 <id>` | 自定义缓冲 |
| `docker kill <id>` | 强制 SIGKILL（应用卡死时才用） |
| `docker pause <id>` / `unpause <id>` | 冻结（cgroup freezer，内存保留，类似休眠） |

⚠️ `stop` vs `kill`：`stop` 给应用清理缓冲时间；`kill` 暴力用。

#### 3.6.4 删除

| 命令 | 含义 |
|------|------|
| `docker rm <id>` | 删已停止的 |
| `docker rm -f <id>` | 强删（含运行中等价 stop+rm） |
| `docker rm -f <id1> <id2>` | 一次删多个 |
| `docker container prune -f` | 清所有已停止 |

#### 3.6.5 进入容器 / 文件系统操作

| 命令 | 含义 |
|------|------|
| `docker exec -it <id> bash` | 走进运行中容器（最常用） |
| `docker exec -it <id> sh` | 镜像无 bash 时（alpine） |
| `docker attach <id>` | 附加主进程 stdin/stdout（一般不用，会冲突） |
| `docker cp 主机路径 <id>:容器路径` | 双向复制 |
| `docker export <id> > foo.tar` | 导出文件系统（丢历史+元数据） |
| `docker import foo.tar myimage:latest` | import 回来（变镜像一层） |

#### 3.6.6 日志 & 资源

- `docker logs <id>` / `-f`：看 / 跟踪
- `docker logs --tail 100` / `--since 10m`：最近 100 行 / 最近 10 分钟
- `docker logs -t`：带时间戳

#### 3.6.7 批量操作（重点）

**方案 1：直接传多个 ID**

```bash
docker stop $(docker ps -qa)
docker rm -f $(docker ps -qa)
```

**方案 2：先过滤再操作（精准）**

```bash
docker stop $(docker ps -qa --filter "status=exited")              # 只停已退出的
docker stop $(docker ps -qa --filter "name=web_")                  # 只停 name 前缀匹配
docker run -d --label env=dev nginx                                # 启动打 label
docker stop $(docker ps -qa --filter "label=env=dev")              # 按 label 批量
```

**方案 3：xargs 写法（更稳健）**

- `$(docker ps -qa)` 在没容器时会变 `docker stop ` → 新版报错，老版本试图 stop 全部镜像
- `xargs -r`：输入为空就不执行

```bash
docker ps -qa | xargs -r docker stop
docker ps -qa | xargs -r docker rm -f
docker ps -qa | xargs -I{} docker inspect -f '&#123;&#123;.State}}' {}       # -I{} 引用每行 ID
```

**方案 4：prune 系列**

| 命令 | 含义 |
|------|------|
| `docker container prune -f` | 清已停止容器 |
| `docker image prune -f` | 清悬空镜像（`<none>`） |
| `docker network prune -f` | 清无用网络 |
| `docker volume prune -f` | 清无用卷 ⚠️ 数据丢失 |
| `docker system prune -f` | 上面四件套全清（除 volume） |
| `docker system prune -af --volumes` | 连 volume 也清 ⚠️⚠️⚠️ |

⚠️ **`docker system prune --volumes` 会删带数据的卷**，执行前必先 `docker volume ls`。

**方案 5：高级批量**

- **docker-compose**：编排多容器（up/down/restart）
- **docker swarm**：集群（service update）

适合多容器应用，单机用方案 1~4。

#### 3.6.8 实战速查（背下来）

```bash
# 清场：全部停 + 全部删
docker stop $(docker ps -qa) ; docker rm -f $(docker ps -qa)

# 批量清已退出的（保留运行中）
docker container prune -f

# 按 label 停一批
docker stop $(docker ps -qa --filter "label=project=blog")

# 按日期清理停超 24h 的
docker ps -qa --filter "status=exited" --filter "since=24h" | xargs -r docker rm

# 全栈清理（含构建缓存）
docker system prune -af
```

---

### 3.7 容器进入与分离（exit vs Ctrl+P+Q）

**问题：** `docker run -it ubuntu` 进入容器后，直接 `exit` 或 `Ctrl+D` 会让容器停止（因为 bash 是 PID 1）。

**三种保持容器运行的退出方式：**

| 方式 | 操作 | 说明 |
|------|------|------|
| **Ctrl + P + Q**（推荐） | 按住 Ctrl，先按 P 再按 Q，顺序不能错 | Docker 设计的"分离"快捷键 |
| **docker detach** | 另开终端 `docker detach <容器名或ID>` | 外部 detach 命令 |
| **启动时避免 PID 1 问题** | `docker run -itd ubuntu` + `docker exec -it bash` | exec 进入，bash 不是 PID 1 |

**关键区分：**
- `exit` / `Ctrl+D` → 退出 bash → **容器停止** ❌
- `Ctrl+P+Q` / `docker detach` → 分离终端 → **容器继续运行** ✅

**退出后重新进入：**

| 方式 | 说明 |
|------|------|
| `docker attach <容器>` | 重连 PID 1 进程 |
| `docker exec -it <容器> bash` | 开新进程（推荐） |

---

### 3.8 容器资源限制（-m / --cpus / --cpu-shares）

#### 内存限制（硬限制）

```bash
docker run -m 256m tylersmith22/docker-stress-ng --vm 2 --vm-bytes 256m
```

- `-m 256m`：Docker 给容器的硬上限（256MB）
- `--vm 2 × --vm-bytes 256m` = 容器内想要 512MB
- 结果：**OOM 被 kill**（想用 > 限制）

**内存是硬限制**：设多少就是多少，超了直接 OOM kill。

#### CPU 限制三剑客

| 参数 | 类型 | 作用 |
|------|------|------|
| `--cpus N` | 硬限制 | 最多用 N 个核心 |
| `--cpuset-cpus N` | 硬限制 | 绑定到指定核心 |
| `--cpu-shares N` | 软限制 | 权重（抢资源时按比例分配） |

**CPU 限制对比示例：**
```bash
# test1: cpu-shares=1024
docker run -d --cpus 1 --cpuset-cpus 0 --cpu-shares 1024 --name test1 ... --cpu 1

# test2: cpu-shares=2048（test1 的两倍）
docker run -d --cpus 1 --cpuset-cpus 0 --cpu-shares 2048 --name test2 ... --cpu 1
```

- 两个都被限制在 CPU 0，最多 1 核
- 抢资源时 test2 拿两倍时间片
- `docker stats` 显示 test1 ~33%，test2 ~66%

**关键理解：**
- **内存：硬限制**（设多少就是多少，超了 OOM kill）
- **CPU：硬限制**（`--cpus` / `--cpuset-cpus`）+ **软限制**（`--cpu-shares` 权重）
- `cpu-shares` 只在**抢资源时**才按比例生效

**一句话总结：** 内存限制是硬上限（`-m`），CPU 限制有绝对（`--cpus`）和相对（`--cpu-shares`）两种。

---

<!-- KB:INSERT:container-operations-additions -->
