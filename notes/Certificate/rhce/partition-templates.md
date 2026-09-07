---
id: "kb-rhce-partition-templates"
title: "RHCE 场景 11–12：分区与主机模板"
summary: "Parted 分区、Jinja 模板和主机文件生成。"
category: "认证考试"
status: "published"
order: 33
parent: "kb-certification-rhce"
tags: ["rhce", "parted", "jinja"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhce.md"
applicableVersion: "RHCE 9.0"
---

# RHCE 场景 11–12：分区与主机模板

## 十一、创建分区

### 题目要求

创建 `/home/devops/ansible/parted.yml`，在 dev 主机组上操作：
- 如果 `/dev/vdd` 存在，创建 1500MiB 分区，失败则创建 800MiB
- 如果 `/dev/vdb` 存在，创建 1500MiB 分区，失败则创建 800MiB
- 分区格式化为 ext4 并挂载到 `/mnt/fs01`

### 题目分析

1. **目标**：在指定磁盘上创建分区并挂载
2. **容错**：1500MiB 不行就创建 800MiB（block/rescue）
3. **条件判断**：先判断磁盘是否存在（when + ansible_devices）
4. **格式化+挂载**：无论成功失败都执行（always）
5. **关键逻辑**：vdb 只在 vdd 不存在时才操作（避免两个磁盘挂载到同一点）

### 准备工作（重置磁盘）

正式考试不需要做，但练习时需要先清理上一题的 LVM。

```bash
# 1. 删除逻辑卷
ansible all -m shell -a 'lvremove /dev/research/data -y'

# 2. 删除卷组
ansible all -m shell -a 'vgremove research -y'

# 3. 删除物理卷
ansible all -m shell -a 'pvremove /dev/vdb1'

# 4. 用零填充磁盘开头，清除分区表
ansible all -m shell -a 'dd if=/dev/zero of=/dev/vdb bs=512 count=1'

# 5. 验证：fdisk -l /dev/vdb 没有分区信息即为成功
ansible all -m shell -a 'fdisk -l /dev/vdb'
```

### 完整 Playbook（parted.yml）

```yaml
- hosts: dev
  tasks:
    - name: vdd exists
      block:
        - name: Create 1500m
          parted:
            device: /dev/vdd
            number: 1
            state: present
            part_end: 1501MiB
      rescue:
        - name: Output fail msg
          debug:
            msg: Could not create partition of that size
        - name: Create 800m
          parted:
            device: /dev/vdd
            number: 1
            state: present
            part_end: 801MiB
      always:
        - name: format partition
          filesystem:
            fstype: ext4
            dev: /dev/vdd1
        - name: mount device
          mount:
            path: /mnt/fs01
            src: /dev/vdd1
            fstype: ext4
            opts: defaults
            state: mounted
      when: "'vdd' in ansible_devices"

    - name: vdd not exits
      debug:
        msg: disk /dev/vdd does not exist
      when: "'vdd' not in ansible_devices"

    - name: vdb exists
      block:
        - name: Create 1500m
          parted:
            device: /dev/vdb
            number: 1
            state: present
            part_end: 1501MiB
      rescue:
        - name: Output fail msg
          debug:
            msg: Could not create partition of that size
        - name: Create 800m
          parted:
            device: /dev/vdb
            number: 1
            state: present
            part_end: 801MiB
      always:
        - name: format partition
          filesystem:
            fstype: ext4
            dev: /dev/vdb1
        - name: mount device
          mount:
            path: /mnt/fs01
            src: /dev/vdb1
            fstype: ext4
            opts: defaults
            state: mounted
      when: "'vdb' in ansible_devices and 'vdd' not in ansible_devices"

    - name: vdb not exists
      debug:
        msg: disk /dev/vdb does not exist
      when: "'vdb' not in ansible_devices and 'vdd' not in ansible_devices"
```

### 代码逐行解析

#### 第一部分：vdd exists

```yaml
- name: vdd exists           # 给 task 起个名字，更清晰
  block:
    - name: Create 1500m
      parted:
        device: /dev/vdd      # 操作的磁盘
        number: 1             # 分区号（第一个分区）
        state: present        # present = 创建分区
        part_end: 1501MiB   # ⚠️ 参数名是 part_end，不是 parted_end
  rescue:
    - name: Output fail msg
      debug:
        msg: Could not create partition of that size
    - name: Create 800m
      parted:
        device: /dev/vdd
        number: 1
        state: present
        part_end: 801MiB    # 退而求其次
  always:
    - name: format partition
      filesystem:
        fstype: ext4
        dev: /dev/vdd1        # ⚠️ 分区设备 = 磁盘 + 分区号
    - name: mount device
      mount:
        path: /mnt/fs01       # 挂载点
        src: /dev/vdd1        # 设备路径
        fstype: ext4          # 文件系统类型
        opts: defaults        # 挂载选项（默认）
        state: mounted        # 挂载并写入 fstab
  when: "'vdd' in ansible_devices"  # 只在 vdd 存在时执行
```

**关键点**：
- `part_end: 1501MiB` 而不是 `1500MiB`，多 1MiB 避免边界计算问题
- `when` 和 `- name:` / `block:` 对齐（任务级指令），不是和模块参数对齐
- `always` 里的任务无论 block 成功还是失败都会执行

#### 第二部分：vdd 不存在

```yaml
- name: vdd not exits
  debug:
    msg: disk /dev/vdd does not exist
  when: "'vdd' not in ansible_devices"
```

#### 第三部分：vdb exists（关键逻辑）

```yaml
- name: vdb exists
  block:
    # ... 同 vdd 的处理 ...
  # ⚠️ 关键：复合条件！
  when: "'vdb' in ansible_devices and 'vdd' not in ansible_devices"
```

**为什么 vdb 的条件要加 `and 'vdd' not in ansible_devices`？**

因为 vdd 和 vdb 都挂载到 `/mnt/fs01`，只能选一块盘：
- vdd 存在 → 用 vdd
- vdd 不存在，vdb 存在 → 用 vdb
- 都不存在 → 都跳过

#### 第四部分：vdb 不存在

```yaml
- name: vdb not exists
  debug:
    msg: disk /dev/vdb does not exist
  when: "'vdb' not in ansible_devices and 'vdd' not in ansible_devices"
```

> ⚠️ 注意：vdb 的 when 条件里 `and` 前后都是 vdd，这是题目原文的 typo，正常应该是一个 vdb 一个 vdd。

### 扩展知识点

#### block/rescue/always 错误处理

| 关键字 | 作用 | 类比 |
|--------|------|------|
| `block` | 正常执行的任务 | try |
| `rescue` | block 中任一任务失败时执行 | catch |
| `always` | 无论成功失败都执行 | finally |

#### Facts 变量判断

| 变量 | 用途 |
|------|------|
| `ansible_lvm.vgs` | 包含所有卷组信息的字典 |
| `'research' in ansible_lvm.vgs` | 判断卷组是否存在 |

#### lvol 模块

| 参数 | 含义 |
|------|------|
| `vg` | 卷组名 |
| `lv` | 逻辑卷名 |
| `size` | 大小（m = MiB，按 1024 进制计算） |

#### filesystem 模块

| 参数 | 含义 |
|------|------|
| `fstype` | 文件系统类型（ext4/xfs 等） |
| `dev` | 设备路径（/dev/research/data） |

### 常见错误

1. **`when` 缩进错误**：必须和 `- name:` 对齐，不能和模块参数对齐
2. **单位混淆**：`lvol` 用 `m`（MiB），`parted` 用 `MiB`，效果一样都是 1024 进制
3. **卷组不存在时的处理**：需要单独的 task 用 `when` 判断，不能放在 block 里

### 验证

```bash
# 查看逻辑卷
ssh root@servera lvs

# 查看卷组
ssh root@servera vgs
```

---

## 十二、生成主机文件

### 题目要求

创建 Jinja2 模板 `hosts.j2` 和 playbook `hosts.yml`，在 dev 主机组生成 `/etc/myhosts` 文件。

### 模板 hosts.j2

```jinja
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
::1 localhost localhost.localdomain localhost6 localhost6.localdomain6
{% for host in groups.all %}
&#123;&#123; hostvars[host].ansible_eth0.ipv4.address }} &#123;&#123; hostvars[host].ansible_fqdn }} &#123;&#123; hostvars[host].ansible_hostname }}
{% endfor %}
```

### 模板逐行解析

#### 第一行：IPv4 localhost 条目

```
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
```

| 字段 | 含义 |
|------|------|
| `127.0.0.1` | IPv4 回环地址（本机） |
| `localhost` | 主机名（短名） |
| `localhost.localdomain` | 完全限定域名（FQDN） |
| `localhost4` | IPv4 专用别名 |
| `localhost4.localdomain4` | IPv4 别名的 FQDN |

#### 第二行：IPv6 localhost 条目

```
::1 localhost localhost.localdomain localhost6 localhost6.localdomain6
```

| 字段 | 含义 |
|------|------|
| `::1` | IPv6 回环地址（相当于 IPv4 的 127.0.0.1） |
| `localhost` | 主机名（和 IPv4 共用） |
| `localhost.localdomain` | FQDN（和 IPv4 共用） |
| `localhost6` | IPv6 专用别名 |
| `localhost6.localdomain6` | IPv6 别名的 FQDN |

#### 第三行：Jinja2 循环（渲染每台主机的条目）

```jinja
{% for host in groups.all %}
&#123;&#123; hostvars[host].ansible_eth0.ipv4.address }} &#123;&#123; hostvars[host].ansible_fqdn }} &#123;&#123; hostvars[host].ansible_hostname }}
{% endfor %}
```

**Jinja2 语法分解**：

```jinja
{% for host in groups.all %}    ← 循环开始：遍历所有主机
  ...                           ← 循环体：对每台主机执行
{% endfor %}                    ← 循环结束
```

**循环体内的变量**：

```jinja
&#123;&#123; hostvars[host].ansible_eth0.ipv4.address }}   ← 该主机的 IPv4 地址
&#123;&#123; hostvars[host].ansible_fqdn }}                 ← 该主机的完全限定域名
&#123;&#123; hostvars[host].ansible_hostname }}             ← 该主机的主机名
```

**`hostvars[host]` 结构图**：

```
hostvars["servera"]
├── ansible_eth0
│   └── ipv4
│       └── address: "172.25.250.10"
├── ansible_fqdn: "servera.lab.example.com"
└── ansible_hostname: "servera"
```

**渲染结果示例**（假设 dev 组有 servera 和 serverb）：

```
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
::1 localhost localhost.localdomain localhost6 localhost6.localdomain6
172.25.250.10 servera.lab.example.com servera
172.25.250.11 serverb.lab.example.com serverb
```

### Playbook

```yaml
- hosts: all

- hosts: dev
  tasks:
    - name: copy hosts.j2 to dev
      template:
        src: hosts.j2
        dest: /etc/myhosts
```

### Playbook 逐行解析

```yaml
- hosts: all          # 第一个 play：空 play，触发 gather_facts 采集所有主机信息

- hosts: dev          # 第二个 play：在 dev 主机组上执行
  tasks:
    - name: copy hosts.j2 to dev
      template:                  # template 模块：渲染 Jinja2 模板并复制
        src: hosts.j2            # 源模板文件
        dest: /etc/myhosts       # 目标路径
```

**为什么第一个 play 是 `hosts: all` 且没有 tasks？**

1. Ansible 默认在执行 play 时 `gather_facts: true`
2. 这个空 play 触发收集所有主机的 Facts（IP、主机名、FQDN 等）
3. 第二个 play 渲染模板时需要引用 `hostvars[host].ansible_eth0.ipv4.address`
4. 如果不先采集 facts，模板里的变量会是空的

**为什么第二个 play 在 dev 上执行，但模板里写的是 `groups.all`？**

- `template` 模块只在 dev 主机上运行，但模板里的 `groups.all` 可以访问**所有主机**的变量
- 这样就能在 dev 主机上生成包含所有主机信息的 hosts 文件

### 扩展知识点

#### Jinja2 模板语法

| 语法 | 含义 | 示例 |
|------|------|------|
| `&#123;% %}` | 逻辑语句（循环、条件） | `&#123;% for %}`, `&#123;% if %}` |
| `&#123;&#123; }}` | 变量输出 | `&#123;&#123; host }}` |
| `{# #}` | 注释 | `{# 这是注释 #}` |

#### 常用 Jinja2 语句

```jinja
{# 循环 #}
{% for item in list %}
  &#123;&#123; item }}
{% endfor %}

{# 条件 #}
{% if condition %}
  ...
{% elif other %}
  ...
{% else %}
  ...
{% endif %}
```

#### Ansible Facts 变量

| 变量 | 含义 |
|------|------|
| `groups.all` | 所有主机列表 |
| `groups.dev` | dev 主机组的主机列表 |
| `hostvars` | 所有主机的变量字典 |
| `hostvars[host].ansible_eth0.ipv4.address` | 指定主机的 IPv4 地址 |
| `hostvars[host].ansible_fqdn` | 指定主机的完全限定域名 |
| `hostvars[host].ansible_hostname` | 指定主机的主机名 |
| `inventory_hostname` | 当前主机的主机名 |

#### template 模块 vs copy 模块

| 模块 | 用途 |
|------|------|
| `template` | 渲染 Jinja2 模板，支持变量替换 |
| `copy` | 直接复制文件，不支持变量 |

### 验证

```bash
# 在 dev 主机上查看生成的文件
ssh root@servera 'cat /etc/myhosts'

# 预期输出：
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
::1 localhost localhost.localdomain localhost6 localhost6.localdomain6
172.25.250.10 servera.lab.example.com servera
172.25.250.11 serverb.lab.example.com serverb
```

### 常见错误

1. **没有第一个空 play**：模板渲染时变量为空，生成的文件没有主机信息
2. **模板路径错误**：`src: hosts.j2` 要确保文件在 playbook 同目录或 roles 目录下
3. **FQDN 拼写**：`ansible_fqdn` 不是 `ansible_domain` |

---
