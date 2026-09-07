---
id: "kb-rhce-reference-changes"
title: "RHCE 综合速查与变题分析"
summary: "验证命令、补充知识、变题分析和 Ansible 字段辨析。"
category: "认证考试"
status: "published"
order: 36
parent: "kb-certification-rhce"
tags: ["rhce", "reference", "changes"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhce.md"
applicableVersion: "RHCE 9.0"
---

# RHCE 综合速查与变题分析

## 综合速查

### 执行 playbook 两种方式

```bash
# 方式一：ansible-navigator（容器执行环境）
ansible-navigator run playbook.yml -m stdout
ansible-navigator run playbook.yml -i inventory -m stdout

# 方式二：ansible-playbook（直接执行）
ansible-playbook playbook.yml
ansible-playbook playbook.yml --vault-password-file=secret.txt
```

### ansible-navigator 注意事项

- 需要正确的 PATH 环境变量（包含 ansible/python 路径）
- `su - devops`（login shell，完整加载环境变量）✅
- `su devops`（非 login shell）❌
- 使用 `-m stdout` 参数让输出直接在终端显示

### 常用验证命令

```bash
ansible all -m ping                               # 连接测试
ansible all -m shell -a 'command'                # 批量执行命令
ansible-inventory --list                          # 查看清单
ansible-navigator images                          # 获取导航器镜像
podman login utility.lab.example.com             # 登录镜像仓库
```

---

## 二十、补充知识点（2026-05-12）

### Roles.yml 中空 Play 的作用

```yaml
- hosts: webservers        # 空 play，没有 roles

- hosts: balancers
  roles:
    - balancer

- hosts: webservers
  roles:
    - phpinfo
```

**第一个 `- hosts: webservers` 为什么是空的？**

目的：提前采集 webservers 的 facts（IP、主机名等）。

Ansible 默认在执行 play 时自动 gather_facts。这个 play 虽然没写 roles 和任务，但执行后 webservers 的 facts 就被采集了。

**为什么需要？** 后面的 balancer 角色要配置负载均衡，需要知道 webservers 的 IP 地址（写进 httpd 的 BalancerMember 配置）。如果不先采集 facts，balancer 角色拿不到 IP，模板渲染会出错。

**常见套路：先跑一个空 play 采集目标主机 facts，后面再用。**

| play | 作用 |
|------|------|
| `hosts: webservers`（空） | 采集 facts，让 balancer 能拿到 webservers 的 IP |
| `hosts: balancers` + balancer | 配置负载均衡 |
| `hosts: webservers` + phpinfo | 配置 phpinfo 页面 |

### Balancer 角色中的 haproxy + httpd 配合

**场景**：bastion 主机作为负载均衡器，需要同时运行 haproxy 和 httpd。

**原理**：
- haproxy 监听 80 端口，负责请求分发（负载均衡）
- httpd 提供本地服务（如 stats 页面或 fallback 页面）
- 两个服务必须同时运行才能实现完整的负载均衡效果

**常见问题**：多次运行 ansible-playbook 后，可能出现 haproxy 占用 80 端口导致 httpd 无法启动的情况。

**排查步骤**：
```bash
# 1. 检查端口占用
ssh root@bastion 'ss -tlnp | grep :80'

# 2. 如果 haproxy 占用 80 端口，先停掉
ssh root@bastion 'systemctl stop haproxy && systemctl disable haproxy'

# 3. 杀掉残留进程
ssh root@bastion 'fuser -k 80/tcp'

# 4. 重新跑 playbook
ansible-playbook roles.yml
```

**关键教训**：
- `Connection refused` 不一定是防火墙问题，先查端口占用
- 多次运行 ansible playbook 可能导致服务状态混乱
- 排查顺序：端口占用 → 服务状态 → 防火墙 → SELinux
- Galaxy 下载的 role 可能同时管理多个服务（haproxy + httpd），要注意服务间的依赖关系

### LVM 模块的单位差异（parted vs lvol）

**问题**：为什么 `parted` 模块用 `MiB`，而 `lvol` 模块用 `m`？

**答案**：两个模块的单位约定不同，但实际效果一样，都是按 1024 进制计算。

| 模块 | 单位 | 含义 |
|------|------|------|
| `parted` | `MiB` | Mebibyte，1 MiB = 1024² bytes（二进制，标准命名） |
| `lvol` | `m` | LVM 内部按 MiB 计算，简写为 m |

**实际对比**：
```yaml
parted:  part_start: 1MiB   # 1 × 1024 × 1024 bytes
lvol:    size: 600m         # 600 × 1024 × 1024 bytes（LVM 按 MiB 算）
```

**考试速记**：
- `parted` → 写 `MiB`（如 `600MiB`）
- `lvol` → 写 `m`（如 `600m`）
- 两个效果一样，按模块约定写就行

### parted 和 lvol 创建逻辑卷的流程

**典型步骤**：
1. `parted` 创建分区（`part_start: 1MiB`, `part_end: 600MiB`）
2. `lvg` 创建卷组（`vg: vg-data`, `pvs: /dev/sdb1`）
3. `lvol` 创建逻辑卷（`lv: lv-data`, `size: 500m`, `vg: vg-data`）

**注意**：分区大小和逻辑卷大小可以不一样，分区是物理层面，逻辑卷是逻辑层面，逻辑卷不能超过卷组总大小。

### dd 命令清除分区表

**命令**：`dd if=/dev/zero of=/dev/vdb bs=512 count=1`

| 参数 | 含义 |
|------|------|
| `dd` | 底层磁盘复制工具 |
| `if=/dev/zero` | 输入源，`/dev/zero` 提供无限空字节（\x00） |
| `of=/dev/vdb` | 输出目标，直接写到 vdb 磁盘 |
| `bs=512` | 每次读写 512 字节（= 1 个扇区） |
| `count=1` | 只写 1 次 |

**效果**：vdb 第 1 个扇区（MBR 分区表位置）被全写成零，分区表消失。

**为什么用 dd 而不是 mkfs？**
- `dd` 是最底层操作，直接写磁盘原始数据，不需要文件系统存在
- `mkfs` 需要先有分区才能格式化，dd 连分区表都能干掉
- 考试里清分区表最快的方式

**⚠️ 危险**：if 和 of 写反就全完了，千万别搞错盘符！

**验证是否清除成功**：
```bash
fdisk -l /dev/vdb
```
成功标志：没有 `Device Boot / Start / End` 分区表头出现。

### RHCE 第11题：关键逻辑补充

**核心逻辑**：vdd 和 vdb 二选一，vdd 优先。

```yaml
when: "'vdb' in ansible_devices and 'vdd' not in ansible_devices"
```

**为什么？** 两块盘都挂载到 `/mnt/fs01`，只能选一块。

**part_end 用 1501MiB 而不是 1500MiB**：多 1MiB 避免边界计算问题。

**准备工作（重置磁盘）**：
```bash
lvremove /dev/research/data -y
vgremove research -y
pvremove /dev/vdb1
dd if=/dev/zero of=/dev/vdb bs=512 count=1  # 清除分区表
```

**验证**：`fdisk -l /dev/vdb` 没有分区信息即为成功。

### parted 模块参数名变更

**正确参数名**：`part_end`（不是 `parted_end`）

```yaml
# 正确写法（考试推荐）
parted:
  device: /dev/vdd
  number: 1
  state: present
  part_end: 1501MiB

# ❌ 错误写法
parted:
  device: /dev/vdd
  number: 1
  state: present
  parted_end: 1501MiB  # 这个参数名不对！
```

**给 task 起名字的好处**：`- name: vdd exists` 比直接写 `- block:` 更清晰，执行时报错也更容易定位。

---

## 二十一、补充知识点（2026-05-16）

### ansible-navigator 与 ansible-playbook 的区别

| | ansible-playbook | ansible-navigator |
|---|---|---|
| 执行环境 | 宿主机本地 | 容器内（Podman） |
| 输出 | 直接打到终端 | 默认进交互界面，加 `-m stdout` 才打到终端 |
| 环境隔离 | ❌ | ✅ |
| 配置文件 | ansible.cfg | ansible-navigator.yml（指定容器镜像） |

**考试关键**：配置文件 `ansible-navigator.yml` 指定容器镜像地址，考试镜像在 `registry.lab.example.com`。

```bash
ansible-navigator run site.yml -i inventory -m stdout  # 跑 playbook
ansible-navigator logs                                  # 查看日志
ansible-navigator explore                               # 交互式调试
```

### navigator 为什么加 -i inventory

- `ansible-playbook`（本机执行）→ 读 `ansible.cfg` 里的 inventory 配置，自动找到
- `ansible-navigator`（容器里执行）→ 容器内"当前目录"可能和宿主机不同，`ansible.cfg` 里的相对路径可能找不到
- `-i inventory` 是显式指定 inventory 路径的保险写法，防止 `No inventory was parsed` 警告
- **简单记**：本地跑一般不用加，容器跑加 `-i` 更稳

### ansible all -m shell 远程批量执行

```bash
ansible all -m shell -a 'cat /etc/yum.repos.d/rhel_dvd.repo'
ansible all -m shell -a 'yum clean all && yum makecache'
```

- `all` = 所有主机（可换成组名或单台主机）
- `-m shell` = 使用 shell 模块（支持管道、重定向、$变量）
- `-a '命令'` = 传给模块的参数
- **shell vs command 模块**：shell 支持管道/重定向但安全性低，command 不支持管道但更安全

### Ansible yml 中双引号和单引号的区别

**大多数情况没区别**，YAML 对字符串处理宽松。真正有区别的三个场景：

| 场景 | 双引号 | 单引号 |
|------|--------|--------|
| 特殊字符（`:` `#`） | ✅ 正常解析 | 必须加引号 |
| 转义（`\n` `\t`） | ✅ 支持转义 | 不转义，字面量 |
| 变量替换（`&#123;&#123; var }}`） | ✅ 会替换 | 不替换，当普通字符串 |

**考试建议**：统一用单引号最省心，不容易出坑。

### RHCE 第四题验证方式

**任务一：install Development Tools**
```bash
ansible dev -m shell -a 'rpm -q "Development Tools"'
ansible dev -m shell -a 'yum groupinfo "Development Tools"'  # 更靠谱
```

**任务二：update pkgs**
```bash
ansible dev -m shell -a 'yum check-update'  # 空输出 = 全部最新
# 退出码 0 = 没有可更新的包 ✅
# 退出码 100 = 还有包没更新 ❌
```

### Ansible roles 两种写法 + become 位置

```yaml
# 写法一：完整写法
roles:
  - role: selinux

# 写法二：简写（效果完全一样）
roles:
  - selinux
```

**become 的位置区别**：
```yaml
# become 在 role 下面 → 只对这个 role 生效
roles:
  - role: selinux
    become: true

# become 在 play 顶层 → 对整个 play 所有 task 生效
roles:
  - selinux
become: true
```

多个 role 时，become 放 role 下面更精准，只给需要的角色提权。

### 安装集合用 yml 文件的写法

**方法一：requirements.yml（推荐）**
```yaml
collections:
  - name: ansible-posix
    source: http://content.example.com/ansible-posix-1.5.1.tar.gz
  - name: community.general
    source: http://content.example.com/community-general-6.3.0.tar.gz
```

**方法二：playbook 里用 collections 关键字**
```yaml
- name: Install Collections
  hosts: localhost
  connection: local
  collections:
    - name: ansible-posix
      source: http://content.example.com/ansible-posix-1.5.1.tar.gz
```

**区别**：requirements.yml 纯下载集合更简洁，考试更常用。

### Ansible playbook 中 name 和 hosts 的顺序

- YAML 的 play 是字典（key-value 对），**key 的顺序随便写**
- `- name: xxx` 开头和 `- hosts: xxx` 开头效果完全一样
- 参考书多用 `hosts` 在前只是习惯/风格，不是语法要求
- **结论**：两种写法都合法，考试里用哪种都行

---

## 二十二、补充知识点（2026-05-17）

### Ansible IPv4 变量两种写法对比

| 变量 | 含义 | 适用场景 |
|------|------|----------|
| `ansible_default_ipv4.address` | 系统默认路由的 IP | 通用，不依赖网卡名 |
| `ansible_eth0.ipv4.address` | eth0 网卡的 IP | 考试环境网卡就叫 eth0 |

**考试中的使用**：
- CE 第 8 题（template）用 `ansible_default_ipv4.address`
- CE 第 12 题（hosts 模板）用 `hostvars[host].ansible_eth0.ipv4.address`
- 生产环境优先用 `ansible_default_ipv4.address`，不绑死网卡名

### CE 第 12 题 - hosts 文件模板原理补充

**Playbook 两个 play 的作用**：
1. `hosts: all`（空 play）→ 触发 gather_facts，控制节点 SSH 到所有主机采集信息
2. `hosts: dev`（执行 template）→ 只在 dev 组机器上渲染并写入 `/etc/myhosts`

**关键理解**：
- gather_facts 在**所有主机**上采集，但 template 只在**目标主机**上执行
- 模板里 `groups.all` 能访问所有主机的 facts，所以 dev 主机上能生成包含全部主机信息的 hosts 文件

### service vs systemd 模块区别

| 模块 | 调用 | 特点 | 适用场景 |
|------|------|------|----------|
| `service` | SysV init 脚本 | 兼容老系统 | 老版本 RHEL |
| `systemd` | systemctl | 支持 daemon_reload | RHEL 9，生产环境推荐 |

**考试要点**：
- 考试里两个都能得分，start/enable 效果一样
- 必须用 systemd 的场景：改了 unit 文件后需要 `daemon_reload`

### CE 第 17 题 - Vault 加密文件如何读取变量

**完整流程**：
1. `locker.yml` 用 `ansible-vault encrypt` 加密 → 磁盘上是乱码
2. 执行时加 `--vault-password-file=secret.txt` 提供密码
3. Ansible 在**内存中解密** locker.yml，变量 `pw_developer`/`pw_manager` 正常可用
4. 磁盘上的 locker.yml **始终保持加密状态**

**设计目的**：
- 密码文件（secret.txt）可以提交 git
- vault 密码本地保管不泄露

**Playbook 变量加载**：
```yaml
vars_files:
  - locker.yml      # 加密的变量文件
  - user_list.yml   # 明文变量文件
loop: "&#123;&#123; users }}"      # 遍历 users 列表
when: item.job == 'developer'  # 条件过滤
password_hash 过滤器: &#123;&#123; pw_developer | password_hash('sha512') }}  # 明文转 SHA512 哈希
```

---

## 二十三、RHCE 变题分析 (2026-05-24)

### 题目 1：生成主机文件

- j2 模板 + playbook，部分可直接下载 hosts.yml
- 模板用 `groups['dev']` 遍历主机组

### 题目 2：创建用户账户（新增 30 天过期）

**新增字段**：

| 字段 | 含义 |
|------|------|
| `password_expire_max: 30` | 密码最长有效期（/etc/shadow 第5字段） |
| `expires` | 账号过期时间（/etc/shadow 第8字段） |

**两个字段区别**：

- `password_expire_max` = 密码本身有效期，30天后必须改密码
- `expires` = 账号有效期，30天后账号失效

**playbook 结构**：
- Play 1: dev + test 主机组 → developer 用户 → devops 组
- Play 2: prod 主机组 → manager 用户 → opsmgr 组
- 两个 play 都用 `vars_files` 引入 locker.yml + user_list.yml
- `when: item.job == "developer/manager"` 过滤用户

**执行命令**：
```bash
ansible-navigator run users.yml -m stdout --vault-password-file=secret.txt
# 或
ansible-playbook --vault-password-file=secret.txt users.yml
```

---

## 二十四、expires 字段详解 (2026-05-24)

**表达式**：`lookup('pipe', 'expr ($(date +%s) + 2592000) / 86400')`

**逐层拆解**：

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1 | `date +%s` | 获取当前 Unix 时间戳（秒数） |
| 2 | `+ 2592000` | 加上 30 天的秒数 |
| 3 | `/ 86400` | 转换成天数（86400 秒 = 1 天） |
| 4 | `expr` | Linux 算术计算 |
| 5 | `lookup('pipe', ...)` | Ansible 执行 shell 命令获取输出 |

**最终结果**：从 1970-01-01 起的天数，对应 /etc/shadow 第 8 字段（账号过期日期）

**⚠️ expr 计算顺序**：`expr $(date +%s) + 2592000 / 86400` 实际先算除法，可能有误。正确应加括号。但考试照抄图片答案即可。

---

## 二十五、Ansible lookup 详解 (2026-05-24)

**表达式**：`lookup('pipe', 'expr $(date +%s) + 2592000')`

**逐个拆解**：

| 部分 | 含义 |
|------|------|
| `lookup` | Ansible 查找函数，从外部获取数据 |
| `'pipe'` | lookup 类型，表示执行 shell 命令并返回输出 |
| `'expr $(date +%s) + 2592000'` | 要执行的 shell 命令 |

**lookup 常见类型**：

| 类型 | 用途 |
|------|------|
| `file` | 读文件内容 |
| `env` | 读环境变量 |
| `pipe` | 执行 shell 命令，返回输出 |
| `csvfile` | 读 CSV 文件 |
| `ini` | 读 ini 配置文件 |

**执行流程**：Ansible → 执行 shell 命令 → 拿到输出 → 填入变量
