---
id: "kb-cloud-container-persistence"
title: "容器持久化与实战"
summary: "Rootless 自启、挂载、OpenVPN 和 LNMP 容器化案例。"
category: "云计算"
status: "published"
order: 14
parent: "kb-cloud-containers"
tags: ["volume", "rootless", "lnmp"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# 容器持久化与实战

## 5. 容器持久化与开机自启

### 5.1 为什么需要先运行临时容器？

`podman generate systemd` 需要读取**已存在**的容器配置来生成 `.service` 文件。

**正确流程：**
```
run 临时容器（配好所有参数） → generate systemd 生成服务文件 → 删除临时容器 → systemd 接管
```

---

### 5.2 完整操作流程（rootless 容器）

```bash
# 1. 准备挂载目录（root）
mkdir /opt/txt.pdf
chown sashat:sashat /opt/txt.pdf

# 2. 切换到用户
ssh sashat@servera

# 3. 运行临时容器
podman run -d --name txt2pdf \
  -v /opt/txt/:/opt/txt:Z \
  -v /opt/pdf:/opt/pdf:Z \
  localhost/modify_file:latest

# 4. 生成 systemd 服务文件
mkdir -p ~/.config/systemd/user
cd ~/.config/systemd/user
podman generate systemd txt2pdf --files --name new

# 5. 启用开机自启
systemctl --user daemon-reload
systemctl --user enable container-txt2pdf.service

# 6. 清理临时容器并重启服务
podman rm -f txt2pdf
systemctl --user restart container-txt2pdf.service

# 7. 验证
podman ps
echo "hello rhcsa" > /opt/txt/rhcsa.txt
ls /opt/pdf/
```

**`podman generate systemd` 关键参数：**

| 参数 | 含义 |
|------|------|
| `--files` | 生成 `.service` 文件 |
| `--name` | 使用容器名命名服务 |
| `--new` | 每次启动**创建新容器**（推荐，避免容器已存在的错误） |

---

### 5.3 Rootless 容器要点

**Rootless 容器：** 普通用户（非 root）运行的容器

| 项目 | 路径/命令 |
|------|----------|
| systemd 服务文件位置 | `~/.config/systemd/user/container-xxx.service` |
| 服务管理命令 | `systemctl --user <动作> container-xxx.service` |
| 服务启动用户 | 当前用户 |
| 用户退出后保留 | 需要 `loginctl enable-linger 用户名` |

**Lingering（持久化）：**
```bash
loginctl enable-linger sashat
# 确保用户退出后（SSH 断开）服务仍在运行
```

⚠️ **Rootless 容器必须用用户级 systemd（`--user`），不能用系统级**（会报权限错误）。

---

## 6. 容器实战案例

### 6.1 OpenVPN Docker 容器故障排查

**故障现象：** 手机通过 OpenVPN 连接后能访问 GitHub，但 Google/YouTube 无法访问。

**根本原因：**

| 故障点 | 原因 |
|--------|------|
| **DNS 配置错误** | OpenVPN AS 推送的 DNS 是 `127.0.0.11`（Docker 内部 DNS），手机上不存在 |
| **NAT 缺失** | VPN 子网 `172.27.0.0/16` 没做 MASQUERADE，包出去了回不来 |

**完整解决步骤：**

```bash
# 1. 修改容器 DNS 为公共 DNS
docker exec openvpn sh -c "echo 'nameserver 8.8.8.8\nnameserver 1.1.1.1' > /etc/resolv.conf"

# 2. OpenVPN AS 推送 DNS 配置（用 sacli 写入数据库）
sacli ConfigPut "vpn.client.routing.dns.0/1" "8.8.8.8,1.1.1.1"

# 3. 容器内添加 iptables NAT
docker exec openvpn iptables -t nat -A POSTROUTING -s 172.27.0.0/16 -o eth0 -j MASQUERADE

# 4. 修改 entrypoint 脚本，让修复持久化（容器重启后规则不丢）
```

**关键知识点：**
- Docker 容器 `127.0.0.11` 是内部 DNS 解析器，**只在容器内有效**
- OpenVPN AS 配置要用 `sacli` 工具写入数据库，**直接改 config-local.json 不生效**
- `sacli ConfigPut` → 写入配置；`sacli Start/Stop` → 重启服务
- VPN 子网需要 NAT 才能访问外网，容器重启后 iptables 规则会丢失

---

### 6.2 Nginx 测试容器（一行启动）

```bash
# 启动一个临时 Nginx 容器，端口映射到 8080
docker run --name nginx_container_test -d -p 8080:80 nginx

# 浏览器访问测试
# http://localhost:8080  → 看到 Nginx 欢迎页

# 查看容器日志
docker logs nginx_container_test

# 进入容器调试
docker exec -it nginx_container_test /bin/bash

# 停止并删除
docker stop nginx_container_test
docker rm nginx_container_test
```

---

## 6.3 LNMP 容器化项目：挂载点的关键逻辑

### 核心思想

> **让容器本身"无状态"，把配置、代码、数据全部从容器内部拎出来放到宿主机。**

### 6.3.1 挂载点对照表



### 挂载点对照表

| 容器 | 宿主机路径 | 容器内路径 | 挂的是啥 |
|------|-----------|-----------|----------|
| redis | ./redis/config | /usr/local/etc/redis | redis.conf 配置 |
| redis | ./redis/data | /data | RDB/AOF 持久化数据 |
| mysql | ./mysql/config | /etc/mysql/conf.d | **覆盖式**配置（追加生效） |
| mysql | ./mysql/data | /var/lib/mysql | 库、表、binlog |
| php-fpm01/02 | ./blog/www | /usr/share/nginx/html | PHP 应用代码 |
| php-fpm01/02 | ./blog/php | /usr/local/etc | php.ini + pool 配置 |
| web01/02/03 | ./blog/nginx | /etc/nginx | web 容器的 nginx 配置 |
| web01/02/03 | ./blog/www | /usr/share/nginx/html | 代码（5 容器同一份） |
| lb01 / lb02 | ./lb01 ./lb02 | /etc/nginx | 各自 nginx 配置 |

---

### 几个容易迷糊的细节

#### 1. 为什么 mysql 挂 /etc/mysql/conf.d 而不是 /etc/mysql/my.cnf

mysql 启动读 `/etc/mysql/my.cnf`，里面一行：
```
!includedir /etc/mysql/conf.d/
```
**自动 include conf.d 下所有 .cnf**，与主配置共存。

直接挂 my.cnf 会**整个覆盖** → 可能漏 socket、pid-file → 容器起不来。
**挂 conf.d 是最稳的自定义配置方式**。

#### 2. redis 命令行还有 redis-server --save 60 1 --loglevel warning

```bash
redis-server --save 60 1 --loglevel warning
#   ├ 每 60 秒 ├ 至少 1 个 key 变更 → 触发 RDB
#   └ warning 日志级别
```

也可以写进 redis.conf 挂进去。命令行更直观，两条路都行。

#### 3. ./blog/www 同时被 5 个容器挂载

```bash
./blog/www → /usr/share/nginx/html
# php-fpm01、php-fpm02、web01、web02、web03
```

意义：
- 改一份代码，5 个容器全部生效
- 不需要 re-build 镜像
- 生产里这目录应该是 git pull + rsync，容器只是消费者

---



### 6.3.2 容器化部署的核心思想



### ① 容器是"无状态"的

容器随时可删，"会变的东西"必须留在容器外。

### ② 配置和数据生命周期不同，分开存放

```bash
mysql/
├── config/    # 文本配置，改动少
└── data/      # 二进制数据，时刻在增长
```

- 备份：data 必须，config 次要
- 扩容：data 占磁盘，config 大小稳定
- **混在一起 → 没法单独管理**
- 这是运维原则："动静分离、按价值分级"

### ③ 配置不进容器，从外部注入

容器内配置默认是镜像里固化的。
这套用 -v 覆盖到宿主机：

- 改配置 = 改宿主机文件，**不重建镜像**
- 同一镜像 + 不同挂载 = 不同实例（dev/stage/prod）
- 这就是 **12-Factor App Config 原则**：
  > "配置应该存在环境（env）或外部文件，不进代码"

### ④ 宿主机拿到全权（运维真正的自由）

| 能做的事 | 没挂载宿主机 | 这个项目 |
|----------|-------------|----------|
| 直接 vim 改配置后热重载 | 得进容器改/重建 | ✅ 直接改宿主机 |
| 备份数据库 | 进容器 mysqldump | ✅ 直接 tar ./mysql/data |
| Git 管理配置 | 镜像里拿不出 | ✅ ./blog/nginx 全在宿主机，git init 即可 |
| 跨机迁移 | 整容器打包 | ✅ 整个目录 scp 过去，docker run 起来 |
| 实时看日志 | 进容器 tail | ✅ 挂个 ./blog/log |

**容器只是"工人"，宿主机才是"真"环境**。

### ⑤ 容器没挂载部分 = 临时/不可信任

- 应用代码、数据库、配置 → 必须挂（✅ 这项目做了）
- 日志 → 建议挂（❌ 这项目没挂，是优化点）
- /tmp 临时文件 → 可不挂（丢了无所谓）

---



### 6.3.3 改进方向



### 1. 用 docker-compose.yml 替代 run.sh

```yaml
version: '3.8'
services:
  redis:
    image: redis:7.4
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - ./redis/config:/usr/local/etc/redis
      - ./redis/data:/data
    restart: always

  mysql:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: ***
    volumes:
      - ./mysql/config:/etc/mysql/conf.d
      - ./mysql/data:/var/lib/mysql
    restart: always

  php-fpm01:
    image: myphp:7.4-fpm
    volumes:
      - ./blog/www:/usr/share/nginx/html
      - ./blog/php:/usr/local/etc
    depends_on: [mysql, redis]
```

一行 `docker compose up -d` 全起。

### 2. --link 改自定义网络

前面讲过，自定义网络替代 --link，去掉 deprecated 警告。

### 3. web01-03 容器"浪费"

web01-03 是 nginx:latest，但它们不服务用户（还得反代给 lb02）。
生产里 web 应是 nginx + php-fpm 一体（LEMP），整套少一层反代。

---



> 💡 **一句话：** 容器无状态化 = 配置 + 代码 + 数据全部从容器内部拎到宿主机，容器本身只跑进程逻辑。

---
