---
id: "kb-rhcsa-storage-containers-1"
title: "RHCSA 场景 8–14：存储、查找与容器"
summary: "挂载、查找、归档、镜像构建和容器自启考试场景。"
category: "认证考试"
status: "published"
order: 22
parent: "kb-certification-rhcsa"
tags: ["rhcsa", "storage", "container"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhcsa.md"
applicableVersion: "RHCSA 9.0"
---

# RHCSA 场景 8–14：存储、查找与容器

> 通用存储原理参见 [Linux 磁盘、LVM 与 Swap](/linux/storage)；通用容器原理参见 [云计算与容器](/cloud)。

## 8. 配置文件系统自动挂载

### 题目要求

配置 autofs，自动挂载 serverb 的 NFS 共享 `/rhome/remoteuser0` 到本地 `/rhome/remoteuser0`。

### 实际操作

```bash
# 安装
yum install autofs -y

# 查看共享
showmount -e serverb.lab.example.com

# 配置主映射文件
echo '/rhome /etc/nfs.auto' >> /etc/auto.master

# 创建映射文件
cat > /etc/nfs.auto << 'EOF'
remoteuser0 -rw serverb.lab.example.com:/rhome/remoteuser0
EOF

# 启动服务
systemctl enable --now autofs.service
```

### 扩展开的知识点

#### autofs 架构

```
/etc/auto.master (主映射)
    ↓
/rhome    /etc/nfs.auto     # /rhome 目录由 /etc/nfs.auto 管理
    ↓
remoteuser0  -rw  serverb:/rhome/remoteuser0   # 具体挂载规则
```

#### 映射文件格式

```
挂载点  选项  源位置
key      -rw   server:/path
```

| 选项 | 含义 |
|------|------|
| `-rw` | 读写挂载 |
| `-ro` | 只读挂载 |
| `-rw,soft` | 软挂载（超时后返回错误） |

#### NFS 相关命令

| 命令 | 作用 |
|------|------|
| `showmount -e HOST` | 查看 NFS 共享列表 |
| `exportfs -v` | 查看本机 NFS 导出 |
| `systemctl restart nfs-server` | 重启 NFS 服务 |

### 验证

```bash
su - remoteuser0
df -Th | grep rhome
touch /rhome/remoteuser0/test.txt   # 能写入
```

---

## 9. 配置用户账户

### 题目要求

创建用户 john，UID 为 2023，密码 redhat。

### 实际操作

```bash
useradd -u 2023 john
echo redhat | passwd --stdin john
```

---

## 10. 查找文件

### 题目要求

查找属于用户 john 的文件，复制到 `/root/findfiles`。

### 实际操作

```bash
mkdir -p /root/findfiles
find / -user john -exec cp {} /root/findfiles/ \;
```

### 扩展开的知识点

#### find 常用选项

| 选项 | 含义 |
|------|------|
| `-user USER` | 按文件所有者查找 |
| `-group GROUP` | 按文件所属组查找 |
| `-name PATTERN` | 按文件名查找 |
| `-type f/d/l` | 按类型（文件/目录/链接）查找 |
| `-size +100M` | 按大小查找 |
| `-mtime -7` | 最近 7 天修改的文件 |
| `-perm MODE` | 按权限查找 |
| `-exec CMD {} \;` | 对找到的文件执行命令 |

#### exec 语法

```bash
find ... -exec COMMAND {} \;
# {} 代表找到的文件
# \; 表示 exec 结束
```

### 验证

```bash
ls /root/findfiles/
```

---

## 11. 查找字符串

### 题目要求

从 `/etc/man_db.conf` 中找所有含 `sbin` 的行，导入 `/root/out.txt`（不含空行）。

### 实际操作

```bash
grep sbin /etc/man_db.conf > /root/out.txt
```

### 扩展开的知识点

#### grep 常用选项

| 选项 | 含义 |
|------|------|
| `-i` | 忽略大小写 |
| `-v` | 反向匹配（排除） |
| `-n` | 显示行号 |
| `-r` | 递归搜索目录 |
| `-c` | 只显示匹配行数 |
| `-E` | 扩展正则表达式 |
| `-w` | 匹配整个单词 |

### 验证

```bash
cat /root/out.txt
```

---

## 12. 创建归档

### 题目要求

创建 `/root/backup-YYYY-MM-DD.tar.bz2` 归档 `/usr/local`。

### 实际操作

```bash
tar -cjf /root/backup-$(date +%F).tar.bz2 /usr/local/
```

### 扩展开的知识点

#### tar 压缩选项

| 选项 | 压缩格式 |
|------|---------|
| `-z` | gzip（`.tar.gz`） |
| `-j` | bzip2（`.tar.bz2`） |
| `-J` | xz（`.tar.xz`） |

#### tar 操作选项

| 选项 | 作用 |
|------|------|
| `-c` | 创建归档 |
| `-x` | 解压归档 |
| `-t` | 列出归档内容 |
| `-f` | 指定文件名 |
| `-v` | 显示详细信息 |

#### date 命令

| 格式 | 输出 |
|------|------|
| `date +%F` | 2023-11-10 |
| `date +%Y%m%d` | 20231110 |
| `date +%H:%M` | 14:30 |

### 验证

```bash
file /root/backup-*.tar.bz2
```

---

## 13. 创建容器镜像

### 题目要求

以 sashat 用户，使用 `http://content.example.com/Containerfile` 创建 `modify_file:latest` 镜像。

### 实际操作

```bash
# 以 sashat 身份
ssh sashat@servera

# 下载 Containerfile
wget http://content.example.com/Containerfile

# 登录镜像仓库
podman login registry.lab.example.com
# admin / redhat321

# 构建镜像
podman build -t modify_file:latest .
```

### 扩展开的知识点

#### podman build

| 参数 | 含义 |
|------|------|
| `-t NAME:TAG` | 指定镜像名和标签 |
| `.` | 构建上下文（当前目录） |

#### 镜像仓库配置

```toml
# /etc/containers/registries.conf
unqualified-search-registries = ['registry.lab.example.com']

[[registry]]
location = "registry.lab.example.com"
insecure = true
blocked = false
```

### 验证

```bash
podman images
```

---

## 14. 配置容器开机自启

### 题目要求

创建 rootless 容器 `txt2pdf`，使用 `modify_file` 镜像，配置为 systemd 服务自动启动。

### 实际操作

```bash
# 创建映射目录
mkdir /opt/{txt,pdf}
chown sashat:sashat /opt/{txt,pdf}

# 以 sashat 身份运行容器
ssh sashat@servera
podman run -d --name txt2pdf \
  -v /opt/txt/:/opt/txt:Z \
  -v /opt/pdf:/opt/pdf:Z \
  localhost/modify_file:latest

# 生成 systemd 服务文件
mkdir -p ~/.config/systemd/user
cd ~/.config/systemd/user
podman generate systemd txt2pdf --files --name --new

# 启用服务
systemctl --user daemon-reload
systemctl --user enable container-txt2pdf.service
```

### 扩展开的知识点

#### Rootless 容器

- 普通用户（非 root）运行的容器
- systemd 服务文件在 `~/.config/systemd/user/`
- 使用 `systemctl --user` 管理

#### podman run 参数

> → 完整参数详解见 [第 18 题 podman run 参数详解](#18-运行一个容器rsyslog)

| 参数 | 含义 |
|------|------|
| `-d` | 后台运行 |
| `--name NAME` | 容器名称 |
| `-v HOST:CONTAINER:Z` | 挂载卷（`:Z` 为 SELinux 标签） |

#### podman generate systemd

| 参数 | 含义 |
|------|------|
| `--files` | 生成 .service 文件 |
| `--name` | 使用容器名命名 |
| `--new` | 每次启动创建新容器 |

#### lingering（持久化）

```bash
loginctl enable-linger sashat
```
确保用户退出后服务仍在运行。

### 验证

```bash
# 测试
podman rm -f txt2pdf
systemctl --user restart container-txt2pdf.service
podman ps
echo "hello rhcsa" > /opt/txt/rhcsa.txt
ls /opt/pdf/
```

---
