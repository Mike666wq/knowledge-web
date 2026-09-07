---
id: "kb-linux-file-sharing-transfer"
title: "Linux 文件共享与传输"
summary: "Samba、终端传输和 lrzsz 工具。"
category: "操作系统"
status: "published"
order: 16
parent: "kb-linux-operations"
tags: ["samba", "scp", "lrzsz"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Linux 文件共享与传输

## 12. Samba 共享配置详解

### 配置示例
```ini
[share]
 path = /media/bbben/disk/share
 browseable = yes
 writable = yes
 valid users = @bbben
 create mask = 0660
 directory mask = 2770
```

### 逐项说明
- **[share]**：共享名，客户端连接时显示的名字（如 `\\IP\share`）
- **path**：共享目录的物理路径
- **browseable = yes**：在网络浏览中可见（no 则隐藏共享）
- **writable = yes**：允许写入（no 则只读）
- **valid users = @bbben**：`@` 表示用户组，只有 bbben 组内用户可访问（不带@是用户名）
- **create mask = 0660**：新建文件权限 rw-rw----（属主6+同组6+其他0）
- **directory mask = 2770**：新建目录权限 rwxrws---（770 + setgid位2，子文件自动继承父目录组）

### 部署注意
1. 确保系统有 bbben 组，用户已加入
2. Samba 密码独立设置：`smbpasswd -a 用户名`
3. 目录权限：`chown root:bbben /media/... && chmod 2770 /media/...`
4. 改完配置先 `testparm` 检查语法，再 `systemctl restart smbd`

### 查看连接与日志
- `sudo smbstatus`：查看当前活跃的 SMB 连接
- 日志目录：`/var/log/samba/`
  - `log.smbd`：核心日志
  - `log.nmbd`：名称解析日志
  - `log.<hostname>`：按客户端主机名分文件

### smb.conf 完整结构
```ini
[global]          # 全局配置（workgroup、security、hosts allow、log level）
[homes]           # 用户家目录共享（%S 自动指向当前用户目录）
[共享名]           # 自定义共享（path、writable、valid users、create mask）
```

### 关键配置项
- `security = user`：推荐模式，每个连接都要认证
- `hosts allow`：建议只放行需要的网段
- 常用变量：`%m`=客户端主机名，`%M`=客户端IP，`%S`=当前用户名

---

## 13. 终端传文件到服务器的方式

### 1. scp（最常用）

**核心语法：**
```bash
# 本地 → 远程
scp /本地/文件 用户@主机:/远程路径

# 远程 → 本地
scp 用户@主机:/远程/文件 /本地路径

# 路径格式必须是 用户@主机:/路径，冒号不能漏
```

**常用选项：**

| 选项 | 作用 | 注意 |
|------|------|------|
| `-r` | 递归传目录 | 传目录**必须加** |
| `-P 端口` | SSH 端口 | **大写 P** |
| `-p` | 保留文件属性（时间、权限） | **小写 p** |
| `-C` | 启用压缩 | 慢网络有用 |
| `-i 密钥` | 指定私钥 | 密钥登录时 |
| `-v` | 详细输出 | 调试用 |
| `-l 限速` | 限速 KB/s | 大文件避免占带宽 |

**实战例子：**
```bash
scp nginx.conf root@server:/etc/nginx/                     # 传配置
scp -r ./myapp/ root@server:/opt/                          # 传项目目录
scp -i ~/.ssh/id_rsa test.txt root@server:/root/            # 密钥登录
scp -P 2222 test.txt root@server:/root/                    # 改 SSH 端口
```

**常见坑：**
1. 远程目录必须存在，scp 不会自动创建
2. 冒号别漏（漏了就成本地路径，报错找不到）
3. 大写 `-P` 是端口，小写 `-p` 是保留属性，**别混**
4. 第一次连接要确认 fingerprint（输入 yes）

基于 SSH，简单直接，**无断点续传**（大文件用 rsync）。

### 2. rsync（推荐，增量同步）
```bash
rsync -avz 本地目录/ 用户名@IP:/远程路径/
```
支持断点续传、增量同步，适合大文件和目录同步。

### 3. sftp（交互式）
```bash
sftp 用户名@IP
# put/get/lcd/cd 等交互命令
```
适合不确定路径时慢慢操作。

### 4. cat + ssh（管道流，小文件）
```bash
cat 本地文件 | ssh 用户名@IP "cat > /远程路径/文件"
```
适合传配置文件等小内容。

### 5. ssh + tar（大批量传输）
```bash
tar czf - /本地目录 | ssh 用户名@IP "tar xzf - -C /远程路径/"
```
打包压缩传输，一次性大量文件。

### 6. lrzsz（rz/sz，终端内传）
```bash
rz    # 上传（弹文件选择框）
sz 文件   # 下载
```
需服务器安装 lrzsz，适合小文件，无断点续传。

### 日常推荐
- 小文件 → scp
- 目录同步 → rsync
- 覆盖 90% 场景

---


---

## 23. lrzsz 文件传输工具（rz 上传 / sz 下载）

> 配合 Xshell / SecureCRT / WindTerm / tabby 等支持 Zmodem 协议的终端使用。



### rz（上传）

```bash
rz
# 弹窗选本地文件上传到 Linux
```

**R**eceived by **z**modem —— 服务器接收客户端发来的文件。

### sz（下载）

```bash
sz /path/file.txt
sz file1.txt file2.log
sz /path/*.log              # 通配符
```

**S**end to **z**modem —— 服务器向客户端发送文件。

**注意要跟文件名**，不像 rz 直接回车。

### sz 不支持目录下载

```bash
sz /etc/nginx/         # ❌ 报错：找不到文件
sz -y /etc/nginx/      # ❌ 也不行
```

### 必须先打包再下载

```bash
# zip 包（Windows 用户友好）
cd /etc/nginx
zip -r nginx_conf.zip ./
sz nginx_conf.zip

# tar.gz 包（推荐，保留权限）
tar czf nginx_conf.tar.gz nginx/
sz nginx_conf.tar.gz
```

收下之后 Linux 命令：
```bash
unzip nginx_conf.zip         # 解 zip
tar xzf nginx_conf.tar.gz    # 解 tar.gz
```

### 常用参数

| 参数 | 作用 |
|------|------|
| `-y` | 覆盖时不提示（默认会问 y/n） |
| `-b` | 二进制传输（推荐，默认就行） |
| `-e` | 转义所有控制字符（传输脚本常用） |
| `-v` | 显示详细过程 |
| `-E` | sz 专属：文件存在时强制覆盖 |

```bash
sz -y /var/log/messages    # 强制覆盖，不问
sz -be script.sh           # 二进制 + 转义控制字符
sz -Ey file.conf           # 强制覆盖 + 二进制
```

### 终端兼容性

sz/rz 默认只支持：
- ✅ Xshell、SecureCRT、PuTTY（Xmodem 扩展）
- ✅ tabby、WindTerm、MobaXterm
- ❌ Windows Terminal、iterm2 默认不支持
  - 需要额外装 zmodem 脚本支持或者用别的终端

### 安装

```bash
# CentOS / RHEL
yum install -y lrzsz

# Debian / Ubuntu
apt install -y lrzsz
```

---
