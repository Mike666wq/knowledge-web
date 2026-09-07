---
id: "kb-linux-permissions"
title: "Linux 用户与权限管理"
summary: "用户、用户组、sudo 与文件权限的日常管理。"
category: "操作系统"
status: "published"
order: 12
parent: "kb-linux-operations"
tags: ["user", "permission", "sudo"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Linux 用户与权限管理

## 3. 用户与权限管理
### 语法公式

```
用户/组  主机=(目标用户)  NOPASSWD:命令
```

### 示例

```
%admins ALL=(root) NOPASSWD:ALL
  ①         ②          ③    ④
```

| 字段 | 值 | 含义 |
|---|---|---|
| ① `%admins` | `%` = 组，`admins` = 组名 | admins 组所有成员 |
| ② `ALL` | 主机名 | 在任何主机上生效 |
| `(root)` | 目标用户 | 可切换到 root |
| ③ `NOPASSWD` | 无需密码 | 执行 sudo 不需要输密码 |
| ④ `ALL` | 命令范围 | 可执行任何命令 |

### 常见写法速查

```bash
# 用户 harry 可 sudo，需要密码
harry ALL=(root) ALL

# 用户 harry 可 sudo，不需要密码
harry ALL=(root) NOPASSWD:ALL

# wheel 组可 sudo（RHEL 默认）
%wheel ALL=(ALL) ALL

# 用户 bob 只能重启 httpd
bob ALL=(root) /usr/bin/systemctl restart httpd

# users 组可 sudo，不需要密码
%users ALL=(root) NOPASSWD:ALL
```

### 配置文件位置

```
/etc/sudoers              ← 主配置文件（一般不动）
/etc/sudoers.d/admins     ← 额外配置文件（推荐在这里写）
```

⚠️ `/etc/sudoers.d/` 下的文件名不要有 `.`（如 `admin.conf`），否则可能不被加载。

### 验证

```bash
su - harry
sudo id
# uid=0(root) gid=0(root) groups=0(root)  ← sudo 提权成功
```

---


---

### 密码策略 + chage 命令
### 全局默认策略：/etc/login.defs

```bash
vim /etc/login.defs
```

| 参数 | 含义 | 默认值 |
|---|---|---|
| `PASS_MAX_DAYS` | 密码最长有效天数（过期时间） | 99999 |
| `PASS_MIN_DAYS` | 密码最短修改间隔（天） | 0 |
| `PASS_MIN_LEN` | 密码最小长度（会被 PAM 覆盖） | 5 |
| `PASS_WARN_AGE` | 密码到期前警告天数 | 7 |

考试常考：修改 `PASS_MAX_DAYS 20` 表示新用户密码 20 天后过期。

⚠️ `/etc/login.defs` 只对**新创建的用户**生效，已存在的用户不受影响。

### 验证新用户策略

```bash
useradd user1
chage -l user1
# Maximum number of days between password change : 20  ← 确认生效
```

### chage 命令：精确控制单个用户

```bash
chage [选项] 用户名
```

| 参数 | 含义 | 示例 |
|---|---|---|
| `-l` | 列出用户的密码策略信息 | `chage -l harry` |
| `-M` | 设置密码最大有效期（天） | `chage -M 90 harry` |
| `-m` | 设置密码最短修改间隔（天） | `chage -m 7 harry` |
| `-W` | 设置密码到期提前警告天数 | `chage -W 14 harry` |
| `-I` | 密码过期后强制停用天数 | `chage -I 30 harry` |
| `-E` | 设置账户过期日期 | `chage -E 2026-12-31 harry` |
| `-d` | 设置上次改密码日期 | `chage -d 2026-01-01 harry` |

**常用场景：**

```bash
chage -M 90 harry           # 密码 90 天过期
chage -I 3 harry            # 过期后 3 天不改就锁定
chage -E 2026-12-31 intern1 # 账户 2026-12-31 过期
chage -d 0 harry            # 强制下次登录必须改密码
```

### chage -l 输出解读

```
Last password change                : Jan 01, 2026
Password expires                    : Mar 02, 2026
Password inactive                   : never
Account expires                     : never
Minimum number of days between password change : 0
Maximum number of days between password change : 90    ← 关键字段
Number of days of warning before password expires : 7
```

### login.defs vs chage 区别

| | `/etc/login.defs` | `chage` |
|---|---|---|
| 作用范围 | **全局默认**，只影响新用户 | **单个用户**，精确控制 |
| 生效时机 | 创建用户时读取 | 立即生效 |
| 适合场景 | 改默认策略 | 改已有用户 |

---


---

### useradd -g 与 -G 的区别
**`-g`（小写）= 主组（primary group）**
- 指定用户登录时的默认组
- 用户只能有一个主组
- 示例：`useradd -g admins harry` → harry 的主组是 admins

**`-G`（大写）= 附加组（supplementary groups）**
- 指定用户额外属于的组，可以有多个（逗号分隔）
- 示例：`useradd -G admins harry` → harry 主组是默认的 harry 组，admins 是附加组

**记忆技巧：** 小 g = group（一个），大 G = Groups（多个）

**验证：** `id harry` 可以看到 gid（主组）和 groups（所有组）

---

### umask 详解（user file-creation mask）

#### 一句话
**`umask` = 「新创建的文件/目录默认要扣掉的权限」**，进程级别，全称 user file-creation mask。

#### 核心算式
```
最终权限 = 基权限 - umask（按位减，更准确地说：& ~umask）
```

| 类型 | 基权限 | 八进制 |
|------|--------|--------|
| 文件（无 x） | rw-rw-rw- | **666** |
| 目录（含 x） | rwxrwxrwx | **777** |

为什么文件默认没 x？避免刚建的文件能被意外执行，是历史约定。

#### umask 常见值对照
| umask | 文件 | 目录 | 场景 |
|-------|------|------|------|
| 022（默认） | 644 rw-r--r-- | 755 rwxr-xr-x | 普通文件 |
| 027 | 640 rw-r----- | 750 rwxr-x--- | 严格组权限 |
| **077** | **600 rw-------** | **700 rwx------** | **私钥 / 密码文件** |
| 002 | 664 rw-rw-r-- | 775 rwxrwxr-x | 团队共享 |

算式（umask=077）：
```
文件：666 & ~077 = 110 110 110 & 111 000 111 = 600（-rw-------）
目录：777 & ~077 = 700（drwx------）
```

#### 老大的命令拆解
```bash
(umask 077; openssl genrsa -out devman.key 2048)
```

| 部分 | 含义 |
|------|------|
| `( ... )` | **子 shell**：括号里是新 shell，不影响当前 shell 的 umask |
| `umask 077` | 子 shell 里临时设 umask 为 077 |
| `openssl genrsa -out devman.key 2048` | 生成 2048 位 RSA 私钥到 devman.key |
| 效果 | 生成的私钥自动是 **600**（只有 owner 读写） |

**为什么必须用子 shell `( )`？**
直接 `umask 077` 会污染当前 shell；`{ }` 是同 shell；`( )` 退出后自动还原，是一次性改 umask 的标准安全写法。

**为什么私钥一定要 600？**
```bash
# 默认 umask 022 + 生成私钥：
$ umask        # 系统默认 022
$ openssl genrsa -out bad.key 2048
$ ls -l bad.key
-rw-r--r-- ... bad.key       # 其他用户可读！危险

# 用子 shell 加 umask 077：
$ (umask 077; openssl genrsa -out good.key 2048)
$ ls -l good.key
-rw------- ... good.key      # 只有 owner 读写
```
私钥泄露 = 任何能读这文件的用户都能解密/伪装身份。**私钥几乎一定要 600，是行业铁规**。

#### 相关实用命令
```bash
umask               # 当前 umask（数字）
umask -S            # 当前 umask（符号格式）
umask 077           # 设为 077（影响当前 shell 及后续子进程）

stat -c '%a %n' file      # 看文件八进制权限：600 devman.key
stat -c '%A %n' file      # 看文件符号权限：-rw------- devman.key

chmod 600 file            # 手动改，不依赖 umask
```

#### 易踩坑清单
1. **子 shell `( )` vs 命令组 `{ ; }`**：`( )` 真子 shell、退出环境还原；`{ ; }` 同 shell、大括号右侧需空格
2. **`openssl genrsa` 默认不锁权限**：跟 umask 强依赖，不主动 chmod 就会按默认 umask 走
3. **SSH 私钥要求 600**：否则 `ssh` 直接报错 `Permissions 0644 for 'xxx' are too open`
4. **root 创建文件默认也是 644**：root 不自动 600，同样依赖 umask
5. **umask 只决定新文件默认权限**：已存在文件改动用 chmod，不跟 umask 走
6. **umask 不能加可执行位**：就算 `umask 000`，文件也是 666，想可执行必须显式 `chmod +x`
7. **Docker / k8s 容器内 umask 跟宿主机可能不同**：跨环境生成文件要醒一下
8. **台子里 `umask 027` 很常见**：很多发行版在 `/etc/profile` 设过，影响所有交互登录
9. **一些系统命令（比如 `install`）有自己的 mode 覆盖**：不会顺着 umask

---


---
