---
id: "kb-certification-redhat"
title: "Red Hat 认证概览"
category: "认证考试"
status: "published"
order: 1
---

# 🔴 Red Hat 认证（RHCSA / RHCE）考试专项

> 从 `linux.md` 拆分出来的考证相关内容，专注于 RHCSA 和 RHCE 考试场景。
>
> 通用 Linux 运维知识请看 `linux.md`。
> 系统性知识点请看 `rhcsa.md` 和 `rhce.md`。

---

## 1. 容器题 3 合 1 考试变化

### 模拟题 vs 正式考试对比

| 对比项 | 模拟题 | 正式考试 |
|---|---|---|
| 容器数量 | 3 道独立容器题 | **3 合 1**，一道题考完 |
| 镜像来源 | 自定义构建（Containerfile + build） | **自行拉取**（podman pull） |
| 镜像地址 | 固定地址 | **每人不同**，和座位号相关 |

### 镜像地址规律

```
座位号 10 → registries.server10.example.com/library/...
座位号 5  → registries.server5.example.com/library/...
```

### 操作流程

```bash
# 1. 登录仓库（地址看考前须知）
podman login registries.serverXX.example.com

# 2. 搜索镜像确认路径
podman search registries.serverXX.example.com watch

# 3. 拉取镜像
podman pull registries.serverXX.example.com/library/watch:latest

# 4. 准备挂载目录
mkdir -p /opt/txt /opt/pdf

# 5. 运行临时容器
podman run -d --name txt2pdf \
  -v /opt/txt:/opt/txt:Z \
  -v /opt/pdf:/opt/pdf:Z \
  registries.serverXX.example.com/library/watch:latest

# 6. 生成 systemd 服务文件
mkdir -p ~/.config/systemd/user
cd ~/.config/systemd/user
podman generate systemd txt2pdf --files --name new

# 7. 启用开机自启
systemctl --user daemon-reload
systemctl --user enable container-txt2pdf.service

# 8. 清理并重启
podman rm -f txt2pdf
systemctl --user restart container-txt2pdf.service

# 9. 验证
podman ps
```

⚠️ 镜像地址每人不同，务必先查考前须知，用 `podman search` 确认路径后再拉取。

---

## 2. 重置 root 密码

### 完整流程

```
重启 → GRUB 按 e → linux 行改为 rd.break → Ctrl+x 启动
→ mount -o remount,rw /sysroot → chroot /sysroot
→ echo Young | passwd --stdin root → touch /.autorelabel
→ exit × 2 → 重启等 SELinux 打标签
```

### 详细步骤

**1. 重启进入 GRUB 菜单，选中内核按 `e` 编辑**

**2. 找到 `linux` 开头的行，把参数改为 `rd.break`**

```
修改前: linux /vmlinuz-... ro crashkernel=auto ... rhgb quiet
修改后: linux /vmlinuz-... ro rd.break
```

**3. 按 `Ctrl + x` 启动，进入紧急模式**

```
switch_root:/#
```

**4. 重新挂载 /sysroot 为读写**

```bash
mount -o remount,rw /sysroot
```

**5. 切换到真正的根目录**

```bash
chroot /sysroot
```

**6. 重置密码**

```bash
echo Young | passwd --stdin root
```

**7. 打 SELinux 标签**

```bash
touch /.autorelabel
```

**8. 退出并重启**

```bash
exit    # 退出 chroot
exit    # 退出紧急模式，系统继续启动
```

### 各步骤原理解释

| 步骤 | 命令 | 原理 |
|---|---|---|
| `rd.break` | GRUB 引导参数 | 在内核启动过程中中断，进入紧急 shell（initramfs 环境） |
| `remount,rw` | `mount -o remount,rw /sysroot` | 紧急模式下根文件系统只读挂载，改密码需要写文件 |
| `chroot` | `chroot /sysroot` | 把当前 shell 的 `/` 切换到真正的系统根目录 |
| `--stdin` | `passwd --stdin` | 从标准输入读取密码，不用交互输入 |
| `.autorelabel` | `touch /.autorelabel` | 告诉系统下次启动时重新打 SELinux 标签 |

⚠️ **`touch /.autorelabel` 极其重要！** 不打 SELinux 标签，重启后可能进不去系统。启动时 SELinux 重新打标签会比较慢，耐心等待。

---

## 3. SELinux 调试脚本

### 脚本内容

```bash
#!/bin/bash
echo 'This is RHCSA Exam' > /var/www/html/file1
semanage port -a -t http_port_t -p tcp 82
chcon -t httpd_sys_content_t /var/www/html/*
```

### 逐行拆解

| 命令 | 含义 |
|---|---|
| `echo ... > /var/www/html/file1` | 在 Apache 默认网页目录创建网页文件 |
| `semanage port -a -t http_port_t -p tcp 82` | 允许 Apache 监听 82 端口（SELinux 默认不允许非标端口） |
| `chcon -t httpd_sys_content_t /var/www/html/*` | 修改文件 SELinux 上下文，让 Apache 能读取 |

### 为什么需要这些步骤？

```
写网页文件 → SELinux 允许 82 端口 → SELinux 允许 Apache 读文件 → curl 验证
```

- `semanage port`：Apache 默认只监听 80，用非标端口必须告诉 SELinux
- `chcon`：新建文件的 SELinux 上下文可能是 `default_t`，Apache 不认识，需改为 `httpd_sys_content_t`

### 验证

```bash
curl http://servera:82/file1
```

### 易错点

| 易错点 | 正确做法 |
|---|---|
| 忘了 `semanage port` | Apache 用非标端口必须加这条 |
| `chcon` 漏了 | 新文件需要改上下文 |
| 端口写错 | 82，不是 80 |
