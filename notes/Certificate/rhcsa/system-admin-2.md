---
id: "kb-rhcsa-system-admin-2"
title: "RHCSA 场景 15–20：系统管理"
summary: "sudo、密码策略、监控、容器、Root 密码和仓库场景。"
category: "认证考试"
status: "published"
order: 23
parent: "kb-certification-rhcsa"
tags: ["rhcsa", "sudo", "root"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhcsa.md"
applicableVersion: "RHCSA 9.0"
---

# RHCSA 场景 15–20：系统管理

## 15. 配置 sudo 提权

### 题目要求

允许 admins 组成员以 root 身份执行任何命令，无需密码。

### 实际操作

```bash
echo '%admins ALL=(root) NOPASSWD:ALL' > /etc/sudoers.d/admins
chmod 440 /etc/sudoers.d/admins
```

### 扩展开的知识点

#### sudoers 格式

```
谁    在哪台机器=(以谁的身份) 命令
%admins ALL=(root) NOPASSWD:ALL
```

| 字段 | 含义 |
|------|------|
| `%admins` | `%` 表示组 |
| `ALL` | 所有主机 |
| `(root)` | 以 root 身份 |
| `NOPASSWD:` | 不需要密码 |
| `ALL` | 所有命令 |

#### 验证安全配置

```bash
visudo -c       # 检查 sudoers 语法
```

### 验证

```bash
su - harry
sudo id
# uid=0(root)
```

---

## 16. 设置默认密码策略

### 题目要求

新创建用户密码默认 20 天后过期。

### 实际操作

```bash
vim /etc/login.defs
# PASS_MAX_DAYS  20
```

### 扩展开的知识点

#### /etc/login.defs 密码策略

| 参数 | 含义 |
|------|------|
| `PASS_MAX_DAYS` | 密码最长使用天数 |
| `PASS_MIN_DAYS` | 密码最短使用天数 |
| `PASS_MIN_LEN` | 密码最小长度 |
| `PASS_WARN_AGE` | 过期前警告天数 |

#### chage 命令

| 命令 | 作用 |
|------|------|
| `chage -l USER` | 查看密码过期信息 |
| `chage -M DAYS USER` | 设置密码最大天数 |
| `chage -E DATE USER` | 设置账户过期日期 |

### 验证

```bash
useradd testuser
chage -l testuser
# Maximum number of days between password change: 20
userdel -r testuser
```

---

## 17. 创建系统监控脚本

### 题目要求

创建 `/usr/local/bin/exam_sysinfo` 脚本，按 CPU 百分比排序输出进程信息。

### 实际操作

```bash
cat > /usr/local/bin/exam_sysinfo << 'EOF'
#!/bin/bash
ps -xao user,pid,vsz,rss,%cpu --sort=%cpu
EOF

chmod +x /usr/local/bin/exam_sysinfo
```

### 扩展开的知识点

#### ps 输出参数

| 参数 | 含义 |
|------|------|
| `user` | 进程所有者 |
| `pid` | 进程 ID |
| `vsz` | 虚拟内存大小 |
| `rss` | 实际内存大小 |
| `%cpu` | CPU 使用率 |

#### ps 选项

| 选项 | 含义 |
|------|------|
| `-x` | 包含无终端的进程 |
| `-a` | 所有用户的进程 |
| `-o` | 自定义输出格式 |
| `--sort=%cpu` | 按 CPU 排序 |

---

## 18. 运行一个容器（rsyslog）

### 题目要求

从 tar 包导入 rsyslog 镜像，推送到仓库，运行容器，用 logger 发送日志。

### 实际操作

```bash
# 下载并导入
wget http://content.example.com/rsyslog.tar
podman load < rsyslog.tar

# 标记并推送
podman image tag localhost/rsyslog:latest registry.lab.example.com/library/rsyslog:latest
podman login registry.lab.example.com
podman push registry.lab.example.com/library/rsyslog:latest

# 运行容器
mkdir /home/sashat/syslog
podman run -d --privileged --name logserver \
  -v /home/sashat/syslog:/var/log:Z \
  registry.lab.example.com/library/rsyslog:latest

# 进入容器写日志
podman exec -it logserver /bin/bash
logger "This is a rhcsa exam"
```

### podman run 参数详解

| 参数 | 含义 | 详细说明 |
|------|------|----------|
| `-d` | 后台运行（detach） | 容器在后台执行，不占用当前终端 |
| `--privileged` | 特权模式 | 赋予容器几乎等同于宿主机 root 的权限，可访问设备、内核参数等。**题目需要挂载卷并写入日志，必须加此参数** |
| `-v HOST:CONTAINER:Z` | 挂载卷 | 将宿主机目录映射到容器内；`:Z` 为 SELinux 私有标签（仅本容器可访问），`:z` 为共享标签 |
| `--name NAME` | 容器命名 | 方便后续 podman exec/restart/rm 操作 |

### 镜像来源说明

本地 (`localhost/rsyslog:latest`) 和远程仓库 (`registry.lab.example.com/library/rsyslog:latest`) **都能运行**，本质是同一个镜像。

**考试建议**：用远程仓库地址运行，因为题目要求推送到仓库，用远程地址能验证推送是否成功。

### 扩展开的知识点

#### podman 镜像操作

| 命令 | 作用 |
|------|------|
| `podman load < FILE` | 从 tar 文件导入镜像 |
| `podman save IMAGE > FILE` | 导出镜像到 tar |
| `podman image tag SRC DEST` | 给镜像打标签 |
| `podman push IMAGE` | 推送镜像到仓库 |
| `podman pull IMAGE` | 拉取镜像 |
| `podman exec -it CMD` | 在运行容器中执行命令 |

### 验证

```bash
grep rhcsa /home/sashat/syslog/messages
```

---

## 19. 重置 root 密码 (serverb)

### 题目要求

将 serverb 的 root 密码重置为 `Young`。

### 实际操作

```
1. 重启系统
2. 在 GRUB 菜单，选择要启动的内核，按 e 编辑
3. 找到 linux 开头的行，删除到 ro 后面，添加 rd.break
4. 按 Ctrl+X 启动

5. 进入紧急模式后：
switch_root:/# mount -o remount,rw /sysroot
switch_root:/# chroot /sysroot
sh-4.4# echo Young | passwd --stdin root
sh-4.4# touch /.autorelabel
sh-4.4# exit
switch_root:/# exit
```

### 扩展开的知识点

#### mount 命令详解

```bash
mount -o remount,rw /sysroot
│    │    │         │
│    │    │         └─ 挂载点：真实的系统根目录
│    │    └─ 选项：remount（重新挂载，不卸载直接改选项）+ rw（读写模式）
│    └─ -o：指定挂载选项
└─ mount：挂载命令
```

| 参数 | 含义 |
|------|------|
| `-o remount` | 重新挂载，不卸载直接修改挂载选项 |
| `rw` | 读写模式（默认 /sysroot 是只读的） |
| `/sysroot` | 真实系统根目录（chroot 环境下的根） |

**为什么需要这步？** 安全启动后 `/sysroot` 以只读方式挂载，改密码需要写权限，所以必须 remount 为 rw。

#### rd.break 流程

```
reboot → GRUB 菜单 → 按 e 编辑内核行 → 添加 rd.break → Ctrl+X 启动
→ mount -o remount,rw /sysroot → chroot /sysroot → 改密码 → touch /.autorelabel
```

#### 关键步骤

| 步骤 | 命令 | 含义 |
|------|------|------|
| 1 | `mount -o remount,rw /sysroot` | 以读写方式挂载系统根 |
| 2 | `chroot /sysroot` | 切换到真实系统根目录 |
| 3 | `passwd` | 修改密码 |
| 4 | `touch /.autorelabel` | 创建标签重打标记（SELinux） |

---

## 20. 配置软件仓库 (serverb)

### 题目要求

在 serverb 上配置 YUM 仓库，操作与 [第 2 题](#2-配置软件仓库-servera) 完全相同。

### 实际操作

```bash
# 与第 2 题操作一致，详见 [第 2 题](#2-配置软件仓库-servera)
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

dnf clean all && dnf makecache
```

> 💡 **同一套操作，只是换了个服务器。** 仓库配置项含义详见 [第 2 题扩展知识点](#2-配置软件仓库-servera)。

---
