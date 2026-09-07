---
id: "kb-cloud-container-networking"
title: "容器网络与服务通信"
summary: "容器 DNS、NAT、自定义网络、旧 link 迁移与 IP 排查。"
category: "云计算"
status: "published"
order: 13
parent: "kb-cloud-containers"
tags: ["container-network", "dns", "docker-link"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# 容器网络与服务通信

## 4. 容器网络

### 4.1 容器内部 DNS（127.0.0.11）

**问题：** OpenVPN Docker 容器推送 DNS `127.0.0.11` 给客户端，客户端解析失败。

**原因：**
- Docker 容器内部有内置 DNS 解析器，监听 `127.0.0.11`
- 这个地址**只在容器内有效**，宿主机和外部客户端都不存在
- 客户端拿到这个 DNS 配置后无法解析域名

**解决：**
```bash
# 修改容器 /etc/resolv.conf 为公共 DNS
docker exec openvpn sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"
# OpenVPN AS 推送 DNS 设置（用 sacli 工具）
sacli ConfigPut "vpn.client.routing.dns.0/1" "8.8.8.8,1.1.1.1"
sacli Start
```

---

### 4.2 容器 NAT（MASQUERADE）

**问题：** VPN 客户端连接后能访问部分网站，但部分网站访问不了。

**原因：** VPN 子网 `172.27.0.0/16` 没做 NAT，包出去了回不来。

**解决：**
```bash
# 容器内添加 iptables NAT
iptables -t nat -A POSTROUTING -s 172.27.0.0/16 -o eth0 -j MASQUERADE

# 持久化：修改 entrypoint 脚本，使重启后规则还在
```

⚠️ 容器重启后 iptables 规则会丢失，**必须修改 entrypoint 让规则持久化**。

---

## 4.3 Docker --link 与容器间通信

### 4.3.1 `--link` 详细解读

**格式：** `--link 源容器:别名`

```bash
docker run ... --link web01:web01 --link web02:web02 --link web03:web03
```

| 位置 | 含义 | 是否必填 |
|------|------|----------|
| 左 `web01` | 被链接的源容器名（已存在的容器） | 必填 |
| 右 `web01` | 在新容器里用什么名字访问它 | 可省，省略则等于左边 |

> 省略右边时，默认就用源容器名。



### 格式：`--link 源容器:别名`

```bash
docker run ... --link web01:web01
```

| 位置 | 含义 | 是不是一定要写 |
|------|------|----------------|
| 左 `web01` | 被链接的源容器名（已存在的容器） | 必填 |
| 右 `web01` | 在新容器里用什么名字访问它 | 可省，省略就等于左边 |

省略右边等价：
```bash
--link web01           # 等价于 --link web01:web01
--link web01:myweb     # lb01 里访问要写 myweb
--link web01:web01.backend.local   # 用子域名访问
```

### Docker 在背后干了什么

在 `lb01` 容器里 `cat /etc/hosts`，会看到（**Docker 自动注入**）：

```
172.17.0.2   web01
172.17.0.3   web02
172.17.0.4   web03
```

左边是源容器在 default bridge 网络的 IP。

**本质：** `--link` 就是往新容器的 `/etc/hosts` 里塞几条解析记录。

附带效果（一般用不上）：
- 注入一堆环境变量，如 `WEB01_PORT_80_TCP=tcp://172.17.0.2:80`
- 老容器可以看到新容器反向连过来（默认单向，只有 link 发起方能连源容器）

### --link 的三大缺点

1. **只能在 default bridge 网络用**：其他网络（host / none / 自定义）直接失效
2. **Docker 官方已废弃**：未来版本会移除
3. **启动顺序敏感**：lb01 启动时，web01/02/03 必须已经存在

---

#### Docker 自定义网络（替代 --link）

### 第 1 步：建网络

```bash
docker network create lnmp-net
```

任意名字都可。这是一个虚拟网桥，凡挂上来的容器互通。

```bash
docker network ls
# 能看到：
# NETWORK ID     NAME       DRIVER    SCOPE
# abc123...      lnmp-net   bridge    local
```

### 第 2 步：所有容器接进来

```bash
docker network connect lnmp-net web01
docker network connect lnmp-net web02
docker network connect lnmp-net web03
```

`connect` 可以把运行中的容器插到网络上，**不需要重启**。

### 第 3 步：启动 lb01，挂网络

```bash
docker run -d --restart=always \
  -p 80:80 \
  --name lb01 \
  -v `pwd`/lb01:/etc/nginx \
  --network lnmp-net \
  nginx:latest
```

### 背后原理

自定义网络里 Docker 自带一个**内置 DNS 服务器**（通常 `127.0.0.11`）。

所有接入容器的 `/etc/resolv.conf` 自动注入：
```
nameserver 127.0.0.11
```

lb01 nginx 访问 `web01` 时：
1. 查 `/etc/resolv.conf` → `127.0.0.11`
2. Docker DNS 返回 web01 在 lnmp-net 上的 IP（如 `172.18.0.3`）
3. 请求发过去

**验证：**

```bash
docker exec -it lb01 bash

cat /etc/resolv.conf
# nameserver 127.0.0.11 说明 DNS OK

getent hosts web01
# 输出：172.18.0.3    web01

ping -c 1 web01
```

### 两种方式对比

| 维度 | `--link` | 自定义网络 |
|------|----------|-----------|
| 实现原理 | 改 `/etc/hosts`（硬塞 IP 解析） | Docker 内置 DNS（动态解析） |
| 容器必须先存在？ | 是（启动顺序敏感） | 否 |
| 能跨自定义网桥？ | 否，只能 default bridge | 是 |
| 重启后解析还在？ | 在（IP 可能变，要重建） | 在（DNS 自动跟上） |
| 支持别名？ | `web01:别的名字` | `--network-alias` 参数 |
| Docker 推荐？ | ❌ 已废弃 | ✅ 推荐 |

### 网络别名（替代 `--link` 别名）

```bash
# 给 web01 多挂一个别名
docker network connect --alias api.local lnmp-net web01

# 启动时挂别名
docker run --network lnmp-net --network-alias api.local nginx
```

---

#### 完整的从 --link 迁移到自定义网络

```bash
# 1. 停 lb01（web01-03 保持运行）
docker stop lb01

# 2. 删 lb01（--link 配置在容器里，重建最干净）
docker rm lb01

# 3. 建网络
docker network create lnmp-net

# 4. web01/02/03 加入新网络（不需要停）
docker network connect lnmp-net web01
docker network connect lnmp-net web02
docker network connect lnmp-net web03

# 5. 重启 lb01，挂自定义网络
docker run -d --restart=always \
  -p 80:80 \
  --name lb01 \
  -v `pwd`/lb01:/etc/nginx \
  --network lnmp-net \
  nginx:latest

# 6. 验证
docker exec -it lb01 getent hosts web01
curl http://localhost
```

跑完这几步，原来的 WARNING 就再也不会出现。

---

---

### 4.3.2 `--link` "容器外:容器里"的本质

> **一句话本质：** `--link` = 启动新容器时，往新容器内部的 `/etc/hosts` 里塞一行 IP+名字。

| 位置 | 真实含义 | 在哪生效 |
|------|----------|----------|
| 左 `web01`（容器外） | Docker daemon 这边告诉 docker：「我要链接源容器 web01」 | dockerd 这边处理 |
| 右 `web01`（容器里） | 在新容器内部 `/etc/hosts` 里写下的别名 | 新容器内 |

> 容器外并不是物理意义"宿主机"，而是 docker daemon 视角的源容器侧；右边才是新容器内解析时看到的名字。



### 一句话本质

`--link` = 启动新容器时，往**新容器内部的 `/etc/hosts`** 里塞一行 IP+名字。

### 拆开左右两半

| 位置 | 真实含义 | 在哪生效 |
|------|----------|----------|
| 左 `web01`（容器外） | docker daemon 找到叫 web01 的容器，取它的 IP | **宿主机/Docker CLI 侧** |
| 右 `web01`（容器里） | 把那个 IP + 这个名字写进新容器的 /etc/hosts | **新容器内部** |

两个动作：
1. **外侧**：找到源容器（**源容器必须先存在**）
2. **内侧**：写 /etc/hosts

左右可以不一样：
```bash
--link web01:phpbackend
# 进 lb01 后：cat /etc/hosts 会看到 "172.17.0.2  phpbackend"（没有 web01 这一行）
```

---

#### 这台架构每个容器内的 /etc/hosts 长啥样

### lb02 启动后
```bash
docker exec lb02 cat /etc/hosts
```
```
127.0.0.1   localhost
172.17.0.5  php-fpm01
172.17.0.6  php-fpm02
```

### web01 启动后（web02/03 一样）
```bash
docker exec web01 cat /etc/hosts
```
```
127.0.0.1   localhost
172.17.0.4  lb02
```

### lb01 启动后
```bash
docker exec lb01 cat /etc/hosts
```
```
127.0.0.1   localhost
172.17.0.2  web01
172.17.0.3  web02
172.17.0.4  web03
```

---

#### 为啥这台架构所有东西都写主机名而不是 IP

容器 IP 是动态的：
```bash
docker rm -f web01
docker run ... --name web01 ...   # 新容器 IP 跟之前可能不一样
```

- 写 IP（如 `172.17.0.2`）→ 重启后失效
- 写名字（如 `web01`）→ nginx/OS 每次查 /etc/hosts 总能找到当下正确 IP

**所有负载均衡配置用主机名是 Docker 场景的标配写法**（不管 --link / compose / k8s）。

---

#### 一次完整请求，名字解析在哪台机器发生

`curl http://localhost/index.php`：

```
【客户端/宿主机】
curl http://localhost
    → "localhost" 在宿主机 /etc/hosts 解析到 127.0.0.1

【LB01 容器内】
nginx 收到请求 → proxy_pass http://web01;
    → OS 解析 "web01" → 查 lb01 内的 /etc/hosts → 命中 172.17.0.2
    → TCP 发到 172.17.0.2:80

【WEB01 容器内】
web01 nginx 收到 → proxy_pass http://lb02;
    → OS 解析 "lb02" → 查 web01 内的 /etc/hosts → 命中 172.17.0.4
    → TCP 发到 172.17.0.4:80

【LB02 容器内】
lb02 nginx 收到 → proxy_pass http://php-fpm01:9000;
    → OS 解析 "php-fpm01" → 查 lb02 内的 /etc/hosts → 命中 172.17.0.5
    → TCP 发到 172.17.0.5:9000

【PHP-FPM01 容器内】
PHP-FPM 处理 index.php，返结果
```

每跳都是"新容器内的 nginx"查"新容器内的 /etc/hosts"。
**不在宿主机查，不在原容器查，每台容器独立解决自己的 DNS**。

---

#### --link vs 自定义网络 解析路径对比

### --link（静态 /etc/hosts）
```
nginx → OS getaddrinfo("web01") → 读 /etc/hosts → 拿 IP → connect
```

### 自定义网络（动态 DNS）
```
nginx → OS getaddrinfo("web01") → /etc/resolv.conf → 127.0.0.11
                                  ↓
                                  Docker 内置 DNS 实时查 daemon → 拿 IP → 返回
```

**关键差别**：
- `/etc/hosts` 静态文件，启动时写啥就是啥，**容器重启 IP 变了不更新** → 错的解析
- Docker DNS 实时查 daemon，**重启后下次自动用新 IP** → 永远正确

`--link` 弃用的本质：**用的是静态文件，不是动态 DNS**。

---

#### 两边写不一样会变成啥样

```bash
# 例：web01 启动时改成 --link lb02:phpapp
docker run ... --link lb02:phpapp --name web01 ...
```

那 web01 内部 `/etc/hosts`：
```
172.17.0.4  phpapp      ← 改名了
```

web01 的 nginx 配置也得跟着改：
```nginx
proxy_pass http://phpapp;   # 不再是 lb02
```

应用层（nginx 配置）用的名字 = link 时写的**右半边**。内外要一致。

你这套架构全用同名写法（外叫啥内也叫啥），本质是"省心"。

---

#### 一句话总结

`--link 容器外:容器里` 整个链路逻辑：

> **"去外侧把 `源容器` 找到，把它当前的 IP 拿到，把它和 `容器内这个名字` 绑成一条解析，塞进 `新容器` 的 /etc/hosts 里。"**

"都是主机名" = 容器名当 hostname 用，**省得 IP 写死**，nginx 配置就写容器名，运行时 OS 查 /etc/hosts 拿当下 IP。

---

#### nginx 配置对应写法的猜测（你这套架构）

### lb01 里的 nginx 配置（应该是 http 块或 stream 块）
```nginx
upstream web_cluster {
    server web01:80;
    server web02:80;
    server web03:80;
}
server {
    listen 80;
    proxy_pass web_cluster;
}
```

### web01/02/03 里的 nginx 配置（每个容器都一样的）
```nginx
location / {
    proxy_pass http://lb02;
}
```

### lb02 里的 nginx 配置
```nginx
upstream php_backend {
    server php-fpm01:9000;
    server php-fpm02:9000;
}
location ~ \.php$ {
    proxy_pass http://php_backend;
}
```

每一处的"目标名字"（web01、lb02、php-fpm01）都必须是 **link 时绑进本机 /etc/hosts 的那个名字**。

---

---

### 4.3.3 Docker 自定义网络（替代 `--link` 的现代方法）

⚠️ **`--link` 在默认 bridge 网络上已弃用**（会有 WARNING），必须用自定义网络替代。



### 第 1 步：建网络

```bash
docker network create lnmp-net
```

任意名字都可。这是一个虚拟网桥，凡挂上来的容器互通。

```bash
docker network ls
# 能看到：
# NETWORK ID     NAME       DRIVER    SCOPE
# abc123...      lnmp-net   bridge    local
```

### 第 2 步：所有容器接进来

```bash
docker network connect lnmp-net web01
docker network connect lnmp-net web02
docker network connect lnmp-net web03
```

`connect` 可以把运行中的容器插到网络上，**不需要重启**。

### 第 3 步：启动 lb01，挂网络

```bash
docker run -d --restart=always \
  -p 80:80 \
  --name lb01 \
  -v `pwd`/lb01:/etc/nginx \
  --network lnmp-net \
  nginx:latest
```

### 背后原理

自定义网络里 Docker 自带一个**内置 DNS 服务器**（通常 `127.0.0.11`）。

所有接入容器的 `/etc/resolv.conf` 自动注入：
```
nameserver 127.0.0.11
```

lb01 nginx 访问 `web01` 时：
1. 查 `/etc/resolv.conf` → `127.0.0.11`
2. Docker DNS 返回 web01 在 lnmp-net 上的 IP（如 `172.18.0.3`）
3. 请求发过去

**验证：**

```bash
docker exec -it lb01 bash

cat /etc/resolv.conf
# nameserver 127.0.0.11 说明 DNS OK

getent hosts web01
# 输出：172.18.0.3    web01

ping -c 1 web01
```

### 两种方式对比

| 维度 | `--link` | 自定义网络 |
|------|----------|-----------|
| 实现原理 | 改 `/etc/hosts`（硬塞 IP 解析） | Docker 内置 DNS（动态解析） |
| 容器必须先存在？ | 是（启动顺序敏感） | 否 |
| 能跨自定义网桥？ | 否，只能 default bridge | 是 |
| 重启后解析还在？ | 在（IP 可能变，要重建） | 在（DNS 自动跟上） |
| 支持别名？ | `web01:别的名字` | `--network-alias` 参数 |
| Docker 推荐？ | ❌ 已废弃 | ✅ 推荐 |

### 网络别名（替代 `--link` 别名）

```bash
# 给 web01 多挂一个别名
docker network connect --alias api.local lnmp-net web01

# 启动时挂别名
docker run --network lnmp-net --network-alias api.local nginx
```

---



**完整的迁移步骤：**



```bash
# 1. 停 lb01（web01-03 保持运行）
docker stop lb01

# 2. 删 lb01（--link 配置在容器里，重建最干净）
docker rm lb01

# 3. 建网络
docker network create lnmp-net

# 4. web01/02/03 加入新网络（不需要停）
docker network connect lnmp-net web01
docker network connect lnmp-net web02
docker network connect lnmp-net web03

# 5. 重启 lb01，挂自定义网络
docker run -d --restart=always \
  -p 80:80 \
  --name lb01 \
  -v `pwd`/lb01:/etc/nginx \
  --network lnmp-net \
  nginx:latest

# 6. 验证
docker exec -it lb01 getent hosts web01
curl http://localhost
```

跑完这几步，原来的 WARNING 就再也不会出现。

---

---

### 4.3.4 多层 nginx + `--link` 架构解读（run.sh 拆解）



### 整体架构

```
                    Client 请求
                        ↓ :80
               ┌─────── LB01 ───────┐    ← 总入口（stream / 反代）
               ↓        ↓        ↓
            web01    web02    web03       ← 三台 web（nginx 容器）
            ↓         ↓         ↓         ← 各自 nginx 反代给 lb02
               ┌──── LB02 ────┐           ← 第二层负载均衡
               ↓             ↓
         php-fpm01      php-fpm02         ← 真正的 PHP 处理
```

**一共 3 层 nginx 反代**：
```
client → LB01 → web01/02/03 → LB02 → php-fpm
```

### 逐个 --link 解读

#### 1. lb02 link php-fpm01/02 ✅

```bash
docker run -d --name lb02 ... 
  --link php-fpm01:php-fpm01 
  --link php-fpm02:php-fpm02
```

- **作用**：让 lb02 容器里的 nginx 解析 `php-fpm01:9000` / `php-fpm02:9000`
- **性质**：正向——lb02 是反代目标，要转发到上游（php-fpm）
- **依赖**：php-fpm 必须先启动

对应 lb02 里的 nginx 配置（推测）：

```nginx
upstream php_backend {
    server php-fpm01:9000;
    server php-fpm02:9000;
}
location ~ \.php$ {
    proxy_pass http://php_backend;
}
```

#### 2. web01/02/03 link lb02 ⚠️（看架构）

```bash
docker run -d --name web01 ... 
  --link lb02:lb02
```

- **作用**：让 web01-03 解析 `lb02`
- **性质**：web01-03 内的 nginx 把请求再反代给 lb02 处理 PHP
- **依赖**：lb02 必须先启动

#### 3. lb01 link web01/02/03 ✅

```bash
docker run -d --name lb01 ... 
  --link web01:web01 
  --link web02:web02 
  --link web03:web03
```

- **作用**：让 lb01 解析三台 web
- **性质**：正向——总入口转轮询到后端
- **依赖**：web01/02/03 必须先启动

### 总结：必须的 link

| 容器 | link 目标 | 必要？ | 说明 |
|------|-----------|--------|------|
| lb02 | php-fpm01/02 | ✅ 必须 | 反代目标，靠 DNS 解析 |
| web01/02/03 | lb02 | ⚠️ 看你架构 | 如果 web 直接处理 PHP 就可省 |
| lb01 | web01/02/03 | ✅ 必须 | 反代目标，三台要轮询 |

---





### 怪点 1：架构绕弯路

有 **3 层 nginx 反代**，web01/02/03 自己也是 nginx 容器，但**自己不处理 PHP**，反而把所有请求甩给 LB02，再分给两个 php-fpm。

web01/02/03 里那个 nginx **完全是传话筒**，啥也没干。

**生产常见做法：**

- **简化 A**：web01/02/03 每台是完整的 nginx + php-fpm 一体（LEMP），自己处理 PHP，根本不需要 LB02 这一层
- **简化 B**：web01/02/03 只装 nginx 起静态或反代到 Apache/PHP-FPM 一体，不会**再**反代到 LB02 这种"中间再 LB 一次"

这套脚本很像**练手**用——把三层负载全部分离，每层独立容器，能看清每层干嘛。
生产里叫"过度架构"，**实验场景直观**，生产去掉中间层。

### 怪点 2：--link 启动顺序被强绑死

```
php-fpm01/02 ──先起──┐
                     ↓ 必须存在
                   lb02 ──先起──┐
                                  ↓ 必须存在
                              web01/02/03 ──先起──┐
                                                  ↓ 必须存在
                                              lb01
```

整个 run.sh **严格串行**，靠 `sleep 3` 凑合缓冲。某一台启动慢，后面全挂。

**自定义网络方案**：

```bash
docker network create lnmp-net

# 任意顺序启动都行
docker run --network lnmp-net php-fpm01 ...
docker run --network lnmp-net lb02 ...
docker run --network lnmp-net web01 ...
docker run --network lnmp-net lb01 ...
```

启动顺序**完全无关**。

### 怪点 3：docker rm -f 断 link 关系

```bash
docker rm -f web01          # ← link 关系一起销毁
docker run -d --link lb02:lb02 --name web01 ...
```

**容器本身不持久化 link**，每条 run 命令都要带。

**正经做法**：写 `docker-compose.yml`：

```yaml
version: '3'
services:
  php-fpm01:
    image: php:7.4-fpm
    volumes:
      - ./blog/www:/usr/share/nginx/html
  lb02:
    image: nginx:latest
    volumes:
      - ./lb02:/etc/nginx
    depends_on:
      - php-fpm01
      - php-fpm02
  web01:
    image: nginx:latest
    volumes:
      - ./blog/nginx:/etc/nginx
      - ./blog/www:/usr/share/nginx/html
    depends_on:
      - lb02
  lb01:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./lb01:/etc/nginx
    depends_on:
      - web01
      - web02
      - web03

networks:
  default:
    name: lnmp-net
```

`depends_on` 表达依赖顺序，**声明式**而不是命令式。
`docker compose up -d` 一键起。

---





| 维度 | `--link` | 自定义网络 |
|------|----------|-----------|
| 实现原理 | 改 `/etc/hosts`（硬塞 IP 解析） | Docker 内置 DNS（动态解析） |
| 容器必须先存在？ | 是（启动顺序敏感） | 否 |
| 能跨自定义网桥？ | 否，只能 default bridge | 是 |
| Docker 推荐？ | ❌ 已废弃 | ✅ 推荐 |

完整迁移命令：

```bash
docker stop lb01
docker rm lb01
docker network create lnmp-net
docker network connect lnmp-net web01
docker network connect lnmp-net web02
docker network connect lnmp-net web03
docker network connect lnmp-net lb02
docker network connect lnmp-net php-fpm01
docker network connect lnmp-net php-fpm02

docker run -d --restart=always \
  -p 80:80 \
  --name lb01 \
  -v `pwd`/lb01:/etc/nginx \
  --network lnmp-net \
  nginx:latest
```

---

> 💡 **一句话：** `--link` 在新容器里塞 hosts 解析；自定义网络用 docker 内置 DNS 解析（127.0.0.11）。前者是早期方案已弃用，后者是现代标准做法。

---

## 4.4 在宿主机（容器外）查容器 IP 的几种方法



### 1. docker inspect --format（最实用）

```bash
docker inspect --format='&#123;&#123;range .NetworkSettings.Networks}}&#123;&#123;.IPAddress}}&#123;&#123;end}}' web01
# 输出：172.17.0.2
```

`--format` 是 Go template，把字段抠出来。

**多个容器一起查：**

```bash
docker inspect \
  --format='&#123;&#123;.Name}} -> &#123;&#123;range .NetworkSettings.Networks}}&#123;&#123;.IPAddress}}&#123;&#123;end}}' \
  web01 web02 web03

# /web01 -> 172.17.0.2
# /web02 -> 172.17.0.3
# /web03 -> 172.17.0.4
```

### 2. 完整 docker inspect（信息巨多）

```bash
docker inspect web01
# 一坨 JSON：IP、挂载、端口、网络、环境变量……
```

太长的话 grep：
```bash
docker inspect web01 | grep -i ipaddress
```

### 3. 自定义网络的 IP（多网络容器必看）

容器挂多个网络时，每个网络一个 IP，必须带网络名过滤：

```bash
# 容器同时挂 default bridge 和 lnmp-net
docker inspect --format='&#123;&#123;.NetworkSettings.Networks.lnmp_net.IPAddress}}' web01
```

**⚠️ 坑：** `lnmp-net` 在 Go template 里**点 `.` 写不了**，自动替换成下划线（`lnmp-net` → `lnmp_net`）。

### 4. docker network inspect（从网络视角看所有容器）

```bash
docker network inspect bridge          # default bridge
docker network inspect lnmp-net        # 自定义网络
```

输出 JSON 里有 `Containers` 字段，每个容器对应一个 IP。**批量看**最合适。

### 5. 一行列出所有容器的 IP + 状态

```bash
docker inspect \
  --format='&#123;&#123;.Name}} | &#123;&#123;range .NetworkSettings.Networks}}&#123;&#123;.IPAddress}}&#123;&#123;end}} | &#123;&#123;.State.Status}}' \
  $(docker ps -aq)

# 输出：
# /php-fpm01 | 172.17.0.5 | running
# /php-fpm02 | 172.17.0.6 | running
# /lb02 | 172.17.0.7 | running
# /web01 | 172.17.0.2 | running
# /web02 | 172.17.0.3 | running
# /web03 | 172.17.0.4 | running
# /lb01 | 172.17.0.8 | running
```

`docker ps -aq` 取所有容器 ID（包括停的）。

### 6. 进容器内部看（验证 --link）

```bash
docker exec lb01 cat /etc/hosts
# 这就是 --link 注入到容器内的解析表
# 能看到 Docker 把 link 源容器的 IP 写进去
```

### 总结：常用的就这 3 个

| 命令 | 用途 |
|------|------|
| `docker inspect --format '...' <容器>` | **最常用**，精确抠字段 |
| `docker network inspect <网络>` | 看某网络上所有容器的 IP |
| `docker exec <容器> cat /etc/hosts` | 进容器看 --link 注入表 |

**万能模板（多网络、要看状态都行）：**

```bash
docker inspect --format='&#123;&#123;.Name}}: &#123;&#123;range .NetworkSettings.Networks}}&#123;&#123;.IPAddress}} &#123;&#123;end}}-&#123;&#123;.State.Status}}' <容器>
```

---

---
