---
id: "kb-rhcsa-core-system-1"
title: "RHCSA 场景 1–7：网络、仓库与权限"
summary: "考试环境、网络、仓库、SELinux、账户、计划任务和共享目录。"
category: "认证考试"
status: "published"
order: 21
parent: "kb-certification-rhcsa"
tags: ["rhcsa", "network", "selinux"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhcsa.md"
applicableVersion: "RHCSA 9.0"
---

# RHCSA 场景 1–7：网络、仓库与权限

## 考试环境概览

| 主机 | IP | 说明 |
|------|-----|------|
| servera.lab.example.com | 172.25.0.10 | 主要操作节点 |
| serverb.lab.example.com | 172.25.0.11 | 第二操作节点 |
| classroom.example.com | 172.25.250.254 | 网关/DNS/NTP/内容源 |
| content.example.com | — | 软件仓库和资源地址 |

**关键信息：**

| 项目 | 值 |
|------|-----|
| root 密码 | `redhat` |
| DNS 域 | `lab.example.com` |
| 子网 | `172.25.0.0/255.255.255.0` |
| 注册服务器 | `registry.lab.example.com` (admin / redhat321) |
| 软件仓库 | `http://content.example.com/rhel9.0/x86_64/dvd/BaseOS` / `AppStream` |
| 评分方式 | 系统重启后评测，所有配置和服务必须在重启后保留 |

---

## 1. 配置网络地址 (servera)

### 题目要求

配置 servera 的网络参数：主机名、IP、子网掩码、网关、DNS。

### 实际操作

```bash
# 设置主机名
hostnamectl set-hostname servera.lab.example.com

# 查看现有网络连接
nmcli connection show

# 删除默认连接
nmcli connection delete "Wired connection 1"

# 创建新连接
nmcli connection add type ethernet ifname eth0 con-name eth0 \
  ipv4.method manual ipv4.addresses 172.25.250.10/24 \
  ipv4.gateway 172.25.250.254 ipv4.dns 172.25.250.254 \
  autoconnect yes

# 激活连接
nmcli connection up eth0
```

### 扩展开的知识点

#### hostnamectl 命令

| 命令 | 作用 |
|------|------|
| `hostnamectl set-hostname NAME` | 设置主机名（永久） |
| `hostnamectl status` | 查看当前主机名信息 |

#### nmcli 网络管理

| 命令 | 作用 |
|------|------|
| `nmcli connection show` | 列出所有连接 |
| `nmcli connection delete NAME` | 删除连接 |
| `nmcli connection add ...` | 创建连接 |
| `nmcli connection up NAME` | 激活连接 |
| `nmcli connection modify NAME KEY VALUE` | 修改连接属性 |

#### nmcli add 关键参数

| 参数 | 含义 | 示例 |
|------|------|------|
| `type` | 连接类型 | `ethernet` |
| `ifname` | 网络接口名 | `eth0` |
| `con-name` | 连接名称 | `eth0` |
| `ipv4.method` | IP 获取方式 | `manual` / `auto` |
| `ipv4.addresses` | IP/子网掩码 | `172.25.250.10/24` |
| `ipv4.gateway` | 默认网关 | `172.25.250.254` |
| `ipv4.dns` | DNS 服务器 | `172.25.250.254` |
| `autoconnect` | 开机自动连接 | `yes` / `no` |

### 验证

```bash
ping classroom.example.com
```

---

## 2. 配置软件仓库 (servera)

### 题目要求

配置 servera 的 YUM 软件仓库。

### 实际操作

```bash
# 创建仓库文件
cat > /etc/yum.repos.d/rhel_dvd.repo << 'EOF'
[BaseOS]
name=RHEL9_BaseOS
baseurl=http://content.example.com/rhel9.0/x86_64/dvd/BaseOS
enabled=1
gpgcheck=0

[AppStream]
name=RHEL9_AppStream
baseurl=http://content.example.com/rhel9.0/x86_64/dvd/AppStream
enabled=1
gpgcheck=0
EOF

# 清理并重建缓存
dnf clean all
dnf makecache
```

### 扩展开的知识点

#### YUM 仓库配置文件

- 文件位于 `/etc/yum.repos.d/`，必须以 `.repo` 结尾
- 每个 `[section]` 定义一个仓库
- 考试对文件名和仓库名不作要求，可自主命名

#### 仓库配置项

| 配置项 | 含义 |
|--------|------|
| `name` | 仓库描述名称 |
| `baseurl` | 仓库地址 |
| `enabled` | 1=启用，0=禁用 |
| `gpgcheck` | 1=检查签名，0=不检查 |

### 验证

```bash
dnf repolist all
```

---

## 3. 调试 SELinux（Web 非标准端口）

### 题目要求

Web 服务器在端口 82 上运行失败，修复以确保：
- 能访问 `/var/www/html` 中的文件
- 通过 82 端口访问
- 系统启动时自动启动 httpd
- SELinux 保持 Enforcing 模式

### 实际操作

```bash
# 1. 确认端口
grep Listen /etc/httpd/conf/httpd.conf

# 2. 放行 SELinux 82 端口
semanage port -a -t http_port_t -p tcp 82

# 3. 修复文件上下文
chcon -t httpd_sys_content_t /var/www/html/*

# 4. 启动服务并设置开机自启
systemctl enable --now httpd.service
```

### 扩展开的知识点

#### SELinux 端口管理

| 命令 | 作用 |
|------|------|
| `semanage port -l` | 列出所有端口标签 |
| `semanage port -a -t TYPE -p PROTO PORT` | 添加端口标签 |
| `semanage port -d -t TYPE -p PROTO PORT` | 删除端口标签 |

#### SELinux 文件上下文

| 命令 | 作用 |
|------|------|
| `chcon -t TYPE FILE` | 临时修改文件类型标签（重启后 restorecon 会恢复） |
| `semanage fcontext -a -t TYPE "PATH(/.*)?"` | 永久定义默认上下文 |
| `restorecon -Rv PATH` | 恢复/应用默认上下文 |
| `ls -lZ` | 查看 SELinux 上下文 |

#### 常用 SELinux 类型

| 类型 | 用途 |
|------|------|
| `http_port_t` | HTTP/HTTPS 端口标签 |
| `httpd_sys_content_t` | Web 静态内容标签 |
| `tmp_t` | 临时文件标签（httpd 无法读取） |

### 验证

```bash
curl http://servera:82/file1
# Hello RHEL9 for file1
```

---

## 4. 创建用户账户

### 题目要求

创建组 admins，创建用户 harry、natasha（属于 admins 组）、alice（无登录 Shell，不属于 admins），密码均为 redhat。

### 实际操作

```bash
groupadd admins

useradd -G admins harry
useradd -G admins natasha
useradd -s /sbin/nologin alice

echo redhat | passwd --stdin harry
echo redhat | passwd --stdin natasha
echo redhat | passwd --stdin alice
```

### 扩展开的知识点

#### useradd 参数

| 参数 | 含义 |
|------|------|
| `-G GROUP` | 指定附加组 |
| `-s SHELL` | 指定登录 Shell |
| `-u UID` | 指定用户 ID |
| `-d DIR` | 指定家目录 |
| `-M` | 不创建家目录 |
| `-r` | 创建系统用户 |

#### passwd 命令

| 命令 | 作用 |
|------|------|
| `echo PWD \| passwd --stdin USER` | 非交互式设密码 |
| `passwd -l USER` | 锁定用户 |
| `passwd -u USER` | 解锁用户 |

#### 组管理

| 命令 | 作用 |
|------|------|
| `groupadd GROUP` | 创建组 |
| `groupmod` | 修改组 |
| `groupdel` | 删除组 |
| `usermod -aG GROUP USER` | 添加用户到附加组 |

### 验证

```bash
id harry
```

---

## 5. 配置周期性计划任务

### 题目要求

以 natasha 用户身份，每周三 15:30 执行 `logger "This is a rhcsa exam"`。

### 实际操作

```bash
crontab -u natasha -e
# 添加：
# 30 15 * * 3 logger 'This is a rhcsa exam'
```

### 扩展开的知识点

#### crontab 时间格式

```
分 时 日 月 周
30 15 *  *  3    # 每周三 15:30
```

| 字段 | 范围 | 特殊写法 |
|------|------|---------|
| 分钟 | 0-59 | `*/5` 每5分钟 |
| 小时 | 0-23 | `9-17` 9点到17点 |
| 日 | 1-31 | `1,15` 1号和15号 |
| 月 | 1-12 | `*` 每月 |
| 周 | 0-7 (0和7=周日) | `3` 周三 |

#### crontab 命令

| 命令 | 作用 |
|------|------|
| `crontab -u USER -e` | 编辑用户计划任务 |
| `crontab -u USER -l` | 列出计划任务 |
| `crontab -u USER -r` | 删除计划任务 |

### 验证

```bash
crontab -u natasha -l
```

---

## 6. 创建共享目录

### 题目要求

创建 `/home/tools`，拥有组 admins，组成员可读写访问，新文件自动继承 admins 组。

### 实际操作

```bash
mkdir /home/tools
chgrp admins /home/tools
chmod g+rwx,o=--- /home/tools
chmod g+s /home/tools
```

### 扩展开的知识点

#### SGID（Set Group ID）

- `chmod g+s DIR` 或 `chmod 2775 DIR`
- 在目录上设置 SGID 后，该目录下新建的文件/目录**自动继承**目录的组
- `ls -l` 显示为 `drwxrws---`（组执行位显示 `s` 而非 `x`）

#### chmod 权限

| 命令 | 含义 |
|------|------|
| `chmod g+rwx` | 组添加读写执行权限 |
| `chmod o=---` | 其他人无任何权限 |
| `chmod g+s` | 设置 SGID |
| `chmod 2775` | SGID + rwxrwxr-x |

#### chgrp

- `chgrp GROUP PATH` — 更改文件/目录的拥有组

### 验证

```bash
ls -ld /home/tools
# drwxrws---. 2 root admins 6 Nov 10 13:19 /home/tools
```

---

## 7. 配置网络时间同步

### 题目要求

配置 chrony 向 `classroom.example.com` 同步时间。

### 实际操作

```bash
vim /etc/chrony.conf
# 添加：
# server classroom.example.com iburst

systemctl restart chronyd.service
```

### 扩展开的知识点

#### chrony.conf 配置

| 配置行 | 含义 |
|--------|------|
| `server HOST iburst` | 指定 NTP 服务器，iburst 快速同步 |
| `pool POOL iburst` | 使用 NTP 服务器池 |

#### iburst 参数

- 前 4 个请求以 2 秒间隔发送（而非默认的 16-64 秒）
- 网络连接正常时可在 10 秒内完成首次同步

### 验证

```bash
chronyc sources
# ^* 表示正在同步
# 只要能看到配置的地址即可
```

---
