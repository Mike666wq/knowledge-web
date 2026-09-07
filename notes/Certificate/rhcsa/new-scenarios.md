---
id: "kb-rhcsa-new-scenarios"
title: "RHCSA 新增题型与容器变化"
summary: "Umask、应用编辑、搜索脚本、SELinux 脚本和容器三合一变化。"
category: "认证考试"
status: "published"
order: 25
parent: "kb-certification-rhcsa"
tags: ["rhcsa", "changes"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhcsa.md"
applicableVersion: "RHCSA 9.0"
---

# RHCSA 新增题型与容器变化

## 29. RHCSA 新增题型：配置 Umask (2026-05-24)

### 题目要求

设置 natasha 用户 umask 为 044，永久生效。

### 实际操作

```bash
# 切换到 natasha 用户
su - natasha

# 设置 umask
umask 044

# 永久生效：写入 ~/.bashrc（用户级，不是 /etc/profile）
echo "umask 044" >> ~/.bashrc
source .bashrc

# 验证
mkdir testdir
touch testfile
ls -l
dr--r--r--.  目录权限 777-044=733
-r--r--r--.  文件权限 666-044=622
```

### 关键点

| 要点 | 说明 |
|------|------|
| umask 计算 | 目录: 777-044=733, 文件: 666-044=622 |
| 永久生效位置 | `~/.bashrc`（用户级），不是 `/etc/profile` |
| 追加用 `>>` | 不能用 `>` 覆盖，否则会清空原有内容 |
| `source .bashrc` | 让当前 shell 立即生效，不用重新登录 |

---

## 30. RHCSA 新增题型：编辑应用程序 (2026-05-24)

### 题目要求

在 `/usr/bin/ex200` 写入 echo 命令，执行后输出指定内容。

### 实际操作

```bash
# 写入命令（外单内双引号嵌套）
echo 'echo "This is RHCSA Exam"' > /usr/bin/ex200
chmod +x /usr/bin/ex200

# 验证
su - natasha
ex200
# This is RHCSA Exam
```

### 关键点

- `/usr/bin/` 在 PATH 里，放这里直接敲名字能执行
- 引号嵌套：外单内双，防止 shell 解析内层双引号

---

## 31. RHCSA 新增题型：搜索脚本 (2026-05-24)

### 题目要求

创建 `/usr/local/bin/mysearch` 脚本，使用 find 搜索文件并输出结果。

### 实际操作

```bash
cat > /usr/local/bin/mysearch << 'EOF'
#!/bin/bash
find / -size +30k -size -50k -perm -4000 -type f > /root/myfile
EOF

chmod a+x /usr/local/bin/mysearch
mysearch
```

### find 参数详解

| 参数 | 含义 |
|------|------|
| `-size +30k` | 大于 30KB |
| `-size -50k` | 小于 50KB |
| `-perm -4000` | 包含 SUID 位（`-` 是包含，不是精确匹配） |
| `-type f` | 普通文件 |

---

## 32. RHCSA 新增题型：SELinux 调试脚本 (2026-05-24)

### 题目要求

编写脚本完成 SELinux 三板斧操作：添加端口、修改文件标签。

> → SELinux 命令详解见 [第 3 题扩展知识点](#3-调试-selinuxweb-非标准端口) 和 [第 25 题](#25-chcon-命令与-selinux-标签)

### 实际操作

```bash
cat > /root/selinux_debug.sh << 'EOF'
#!/bin/bash
echo "Fixing SELinux..."
semanage port -a -t http_port_t -p tcp 82
chcon -t httpd_sys_content_t /var/www/html/*
EOF

chmod +x /root/selinux_debug.sh
```

### SELinux 三板斧

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1 | `getenforce` | 查看当前模式 |
| 2 | `semanage port -a -t http_port_t -p tcp 82` | 添加非标端口 |
| 3 | `chcon -t httpd_sys_content_t /var/www/html/*` | 给文件打 Web 标签 |

- `chcon` 是临时修改，考试环境够用
- 永久修改用 `semanage fcontext` + `restorecon`

---

## 33. RHCSA 容器题变化：三合一 (2026-05-24)

### 变化说明

从自定义构建镜像 → 拉取现成镜像，3道容器题合并1道。

### 完整流程

```bash
# 1. 登录仓库（考前须知给地址）
podman login registry.lab.example.com

# 2. 拉取镜像（地址因座位号不同）
podman search 搜索镜像
podman pull 拉取镜像

# 3. 生成 systemd 服务
podman generate systemd --new --name container-txt2pdf --files

# 4. 移动到用户级服务目录
mv container-txt2pdf.service ~/.config/systemd/user/

# 5. 启用服务
systemctl --user daemon-reload
systemctl --user enable --now container-txt2pdf.service

# 6. 关键：启用 linger（root 执行）
loginctl enable-linger sashat
```

### 关键点

| 要点 | 说明 |
|------|------|
| 镜像地址 | 不固定，看考前须知，用 `podman search` 确认 |
| 挂载加 `:Z` | SELinux 标签，否则容器可能无权限访问 |
| linger | 确保用户退出后服务继续运行，**必须 root 执行** |
| 用户级服务 | 用 `systemctl --user`，不能 sudo |

---
