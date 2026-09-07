---
id: "kb-rhcsa-reference"
title: "RHCSA 综合速查与命令辨析"
summary: "服务、SELinux、LVM、容器与常用命令参数速查。"
category: "认证考试"
status: "published"
order: 26
parent: "kb-certification-rhcsa"
tags: ["rhcsa", "reference"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhcsa.md"
applicableVersion: "RHCSA 9.0"
---

# RHCSA 综合速查与命令辨析

## 综合速查

### 系统服务管理

```bash
systemctl enable --now SERVICE   # 启用并立即启动
systemctl status SERVICE          # 查看状态
systemctl restart SERVICE         # 重启
systemctl reload SERVICE          # 重载配置
```

### SELinux 速查

```bash
getenforce                        # 查看当前状态
setenforce 1/0                    # enforcing/permissive
semanage port -l                  # 列出端口标签
semanage port -a -t TYPE -p PROTO PORT   # 添加端口
chcon -t TYPE FILE                # 临时改文件标签
restorecon -Rv DIR                # 恢复默认标签
ls -lZ                            # 查看上下文
```

### LVM 速查

```bash
pvcreate /dev/vdb1                # 创建 PV
vgcreate VGNAME PV                # 创建 VG
lvcreate -L SIZE -n LVNAME VG     # 创建 LV
lvextend -r -L SIZE DEV           # 扩容 LV + 文件系统
```

### 容器速查

```bash
podman build -t NAME:TAG .         # 构建镜像
podman run -d --name NAME IMAGE    # 运行容器
podman generate systemd NAME --files --name --new  # 生成 service
systemctl --user enable --now SERVICE
loginctl enable-linger USER       # 用户持久化
```

---

## 容器镜像构建方式对比：第13题 vs 第18题

### 核心区别
- **第13题**：给的是 Containerfile（构建配方），用 `podman build` 生成本地镜像
- **第18题**：给的是 tar 包（已打包的镜像），用 `podman load` 导入本地镜像

### 为什么不能互换？
- Containerfile 是文本配方，不能 `load`，只能 `build`
- tar 包是成品镜像，不能 `build`，只能 `load`
- 两者最终效果一样：先在本地存储生成镜像，再 `podman push` 推到仓库

### 关键命令对比

| 步骤 | 第13题 | 第18题 |
|------|--------|--------|
| 生成本地镜像 | `podman build -t name:tag .` | `podman load < file.tar` |
| 打标签 | build时 `-t` 直接指定 | `podman tag localhost/name:tag registry/name:tag` |
| 推送 | `podman push` | `podman push` |

### 记忆口诀
- 有菜谱（Containerfile）→ 自己炒菜（build）
- 有成品（tar包）→ 装盘上桌（load + tag + push）

---

## 25. chcon 命令与 SELinux 标签

```bash
chcon -t tmp_t /var/www/html/*
```

> → SELinux 端口管理、文件上下文命令详见 [第 3 题扩展知识点](#3-调试-selinuxweb-非标准端口)

### 参数拆解

| 参数 | 含义 |
|------|------|
| `chcon` | Change Context，修改 SELinux 安全上下文 |
| `-t` | 指定修改类型（type） |
| `tmp_t` | 临时文件类型标签 |
| `/var/www/html/*` | 目标文件 |

### SELinux 安全上下文格式

```
用户:角色:类型:级别
system_u:object_r:httpd_sys_content_t:s0
                ↑
              类型（type），决定进程能否访问
```

**核心规则**：进程只能访问和它类型匹配的文件。

### 常见类型标签

| 标签 | 含义 |
|------|------|
| `httpd_sys_content_t` | httpd 能访问的网页内容 |
| `httpd_sys_rw_t` | httpd 能读写的文件 |
| `tmp_t` | 临时文件 |
| `admin_home_t` | 管理员家目录文件 |

### chcon vs semanage

| 命令 | 效果 | 持久性 |
|------|------|--------|
| `chcon -t type file` | 临时改标签 | ❌ 重启/restorecon 后恢复 |
| `semanage fcontext -a -t type "path"` | 永久改策略 | ✅ 持久生效 |

**chcon 是临时补救，semanage 才是正解。**

---

## 26. ls -lz 命令（查看 SELinux 标签）

```bash
ls -lz /var/www/html/
```

> → SELinux 安全上下文格式详解见 [第 25 题](#25-chcon-命令与-selinux-标签)

### 参数

| 参数 | 含义 |
|------|------|
| `-l` | 长格式显示（权限、所有者、大小、时间） |
| `-z` | 显示 SELinux 安全上下文 |

### SELinux 上下文格式

```
unconfined_u:object_r:httpd_sys_content_t:s0
     ↑           ↑              ↑            ↑
   用户        角色            类型         级别
```

| 字段 | 含义 |
|------|------|
| 用户 | 文件属于哪个 SELinux 用户 |
| 角色 | 文件角色（文件固定 `object_r`） |
| 类型 | **关键字段**，决定哪些进程能访问 |
| 级别 | MLS 安全级别（单级系统固定 `s0`） |

### 其他查看方式

```bash
ls -lZ /var/www/html/      # 大写 Z，和 -z 效果一样
getfattr -n security.selinux /var/www/html/file1
```

### 一句话

`ls -lz` = 长格式 + 显示 SELinux 标签，检查文件安全上下文是否正确。

---

## 27. useradd -s /sbin/nologin 详解

```bash
useradd -s /sbin/nologin alice
```

### 参数

| 参数 | 含义 |
|------|------|
| `-s` | 指定用户的登录 shell |
| `/sbin/nologin` | 拒绝交互式登录的特殊 shell |

### 为什么不能登录？

- 用户登录时系统执行其登录 shell
- `/bin/bash` → 启动命令行，可交互
- `/sbin/nologin` → 直接拒绝，提示 "This account is currently not available"

### 使用场景

不是所有用户都需要登录。系统服务用的用户不需要交互：

```bash
useradd -s /sbin/nologin nginx   # nginx 服务账号
useradd -s /sbin/nologin mysql   # 数据库服务账号
```

**安全原则**：服务用专用用户跑，但不让登录，防止被利用。

### nologin vs false

| shell | 行为 |
|-------|------|
| `/sbin/nologin` | 拒绝登录，友好提示 |
| `/bin/false` | 拒绝登录，静默失败 |

---

## 28. ls -ld vs ls -lZ 对比

### ls -ld

```bash
ls -ld /home/tools
```

| 参数 | 含义 |
|------|------|
| `-l` | 长格式 |
| `-d` | 显示目录本身，不进入目录列内容 |

```bash
ls -l /home/tools       # 列出目录里面的文件
ls -ld /home/tools      # 只看目录自己的属性
```

### Set GID（权限里的 s）

```
drwxrws---. 2 root admins 6 Nov 10 13:19 /home/tools
       ↑
     Set GID
```

- 目录的组执行位出现 `s` = Set GID
- 效果：该目录下新建的文件，所属组自动继承 `admins` 组，而不是创建者的主组

### 对比

| 命令 | 用途 |
|------|------|
| `ls -ld /home/tools` | 查看目录本身的权限和属性 |
| `ls -lZ /home/tools` | 查看目录里文件的 SELinux 标签 |
| `ls -ldZ /home/tools` | 查看目录本身的 SELinux 标签（两者组合） |

**一句话**：`-d` 看目录自己，`-Z` 看 SELinux 标签，可以组合使用。

---
