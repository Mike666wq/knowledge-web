---
id: "kb-rhce-roles-lvm"
title: "RHCE 场景 6–10：角色、集合与 LVM"
summary: "Galaxy、Collection、自定义角色和逻辑卷 Playbook。"
category: "认证考试"
status: "published"
order: 32
parent: "kb-certification-rhce"
tags: ["rhce", "ansible-role", "lvm"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhce.md"
applicableVersion: "RHCE 9.0"
---

# RHCE 场景 6–10：角色、集合与 LVM

## 六、使用 Ansible Galaxy 安装角色

### 题目要求

从 URL 下载角色并安装到 `/home/devops/ansible/roles`。

### 实际操作

```bash
# requirements.yml
- name: balancer
  src: http://classroom.example.com/content/haproxy.tar.gz
- name: phpinfo
  src: http://classroom.example.com/content/phpinfo.tar.gz

# 安装
ansible-galaxy install -r roles/requirements.yml -p roles/
```

### 扩展开的知识点

#### ansible-galaxy install

- Ansible Galaxy 是 Ansible 的角色市场/仓库，类似 pip/npm
- 两种安装方式：
  1. **从 Galaxy 仓库**：`ansible-galaxy install geerlingguy.docker`
  2. **从 URL**：`ansible-galaxy install -r requirements.yml -p roles/`

#### requirements.yml 格式

| 字段 | 含义 |
|------|------|
| `name` | 安装后的角色目录名 |
| `src` | 角色包的下载地址（URL） |

#### 命令参数

| 参数 | 含义 |
|------|------|
| `-r requirements.yml` | 从清单文件批量安装 |
| `-p roles/` | 指定安装目录 |

#### 流程

```
读取清单 → 下载 tar.gz → 解压到 roles/ 目录
```

---

## 七、安装集合

### 题目要求

将 `ansible-posix-1.5.1.tar.gz` 和 `community-general-6.3.0.tar.gz` 安装到 `/home/devops/ansible/mycollections/`。

### 实际操作

```bash
ansible-galaxy collection install http://content.example.com/ansible-posix-1.5.1.tar.gz -p mycollections/
ansible-galaxy collection install http://content.example.com/community-general-6.3.0.tar.gz -p mycollections/
```

### 扩展开的知识点

#### 两种安装方式

| 方法 | 命令 | 场景 |
|------|------|------|
| 直接 URL | `ansible-galaxy collection install URL -p dir/` | 集合少，简单直接 |
| requirements.yml | `ansible-galaxy collection install -r req.yml -p dir/` | 集合多，清单管理 |

#### 安装后目录结构

```
mycollections/
└── ansible_collections/
    ├── ansible.posix/
    └── community.general/
```

#### 关键知识点

- `ansible-galaxy collection install` 安装**集合**（不是角色）
- `-p mycollections/` 指定安装目录
- 需要在 `ansible.cfg` 配置 `collections_path` 指向安装目录
- `ansible-galaxy collection list` 列出已安装集合

### 验证

```bash
ls mycollections/ansible_collections/
```

---

## 八、创建和使用角色

### 题目要求

创建 `apache` 角色（安装 httpd、配置防火墙、部署 Jinja2 模板），在 `webservers` 主机组运行。

### 角色 tasks/main.yml

```yaml
- name: install http
  yum:
    name: httpd
    state: present

- name: config system service
  service:
    name: "&#123;&#123; item }}"
    state: started
    enabled: yes
  loop:
    - httpd
    - firewalld

- name: firewalld service
  firewalld:
    service: http
    permanent: yes
    immediate: yes
    state: enabled

- name: user templates
  template:
    src: index.html.j2
    dest: /var/www/html/index.html
```

### 角色 templates/index.html.j2

```
Welcome to &#123;&#123; ansible_fqdn }} on &#123;&#123; ansible_default_ipv4.address }}
```

### Playbook newrole.yml

```yaml
- name: use apache role
  hosts: webservers
  roles:
    - apache
```

### 扩展开的知识点

#### Role 目录结构（`ansible-galaxy init apache`）

自动生成标准目录：
```
apache/
├── tasks/main.yml        ← 主任务入口（Ansible 默认读这里）
├── handlers/main.yml     ← 处理器
├── templates/            ← Jinja2 模板文件
├── files/                ← 静态文件
├── vars/main.yml         ← 变量
├── defaults/main.yml     ← 默认变量
└── meta/main.yml         ← 角色元数据
```

**为什么写在 `tasks/main.yml`？** Ansible 执行角色时默认读 `tasks/main.yml`，这是约定的入口文件，相当于程序的 `main()`。

#### 常用 Facts 变量

| 变量 | 含义 |
|------|------|
| `ansible_fqdn` | 主机完全限定域名 |
| `ansible_default_ipv4.address` | 主机 IP 地址 |
| `ansible_hostname` | 主机短名称 |
| `ansible_distribution` | 发行版名称 |

#### Jinja2 模板（`.j2` 文件）

`index.html.j2` 是 Jinja2 模板，用变量动态生成文件：
```jinja
welcome to &#123;&#123; ansible_fqdn }} on &#123;&#123; ansible_default_ipv4.address }}
```

- `ansible_fqdn` → 被管节点的完全限定域名
- `ansible_default_ipv4.address` → 被管节点的 IP 地址
- 每台机器执行时自动替换为自己的值，生成专属页面

在 `tasks/main.yml` 中用 `template` 模块部署：
```yaml
- template:
    src: index.html.j2
    dest: /var/www/html/index.html
```

#### template 模块

- 将 Jinja2 模板渲染后复制到目标主机
- `src`: 模板文件路径（相对于 `templates/`）
- `dest`: 目标路径

#### firewalld 模块参数详解

```yaml
- firewalld:
    service: http
    permanent: yes
    immediate: yes
    state: enabled
```

| 参数 | 含义 | 等价命令 |
|------|------|----------|
| `permanent: yes` | 永久生效，重启后规则仍在 | `firewall-cmd --add-service=http --permanent` |
| `immediate: yes` | 立即生效，当前就加载，不用重启 firewalld | `firewall-cmd --add-service=http` |
| `state: enabled` | 启用/允许该服务 | `--add-service` |
| `state: disabled` | 禁用/拒绝该服务 | `--remove-service` |

`permanent` + `immediate` 组合 = 既写入配置文件又立即加载，缺一不可。

### 验证

```bash
curl serverc
# Welcome to serverc.lab.example.com on 172.25.250.12
curl serverd
# Welcome to serverd.lab.example.com on 172.25.250.13
```

---

## 九、从 Ansible Galaxy 使用角色

### 题目要求

创建 `/home/devops/ansible/roles.yml`，在 balancers 组使用 `balancer` 角色，在 webservers 组使用 `phpinfo` 角色。

### Playbook

```yaml
- hosts: balancers
  roles:
    - balancer

- hosts: webservers
  roles:
    - phpinfo
```

### 扩展开的知识点

#### 角色复用

- 通过 roles 关键字引用已安装的角色
- 角色放在 `roles/` 目录下（在 `ansible.cfg` 中配置了 `roles_path`）
- balancer 角色实现负载均衡，phpinfo 角色显示 PHP 信息

### 验证

```bash
curl http://bastion.lab.example.com/
# 轮流返回 serverc 和 serverd 的 Welcome 页面

curl http://serverc.lab.example.com/hello.php
# Hello PHP World from serverc.lab.example.com
```

---

## 十、创建和使用逻辑卷

### 题目要求

创建 `/home/devops/ansible/lv.yml`，在 `research` 卷组中创建 600MiB 的 `data` 逻辑卷，使用 ext4 格式化。如果无法创建 600MiB 则创建 400MiB，如果卷组不存在则报错。

### 题目分析

1. **目标**：在 `research` 卷组中创建逻辑卷 `data`
2. **容错**：600m 不行就创建 400m（block/rescue）
3. **异常处理**：卷组不存在时报错提示（when 判断）
4. **格式化**：无论成功失败都格式化为 ext4（always）

### 完整流程

```
判断卷组是否存在
    ├─ 存在 → 尝试创建 600m 逻辑卷
    │         ├─ 成功 → 格式化 ext4
    │         └─ 失败 → 创建 400m → 格式化 ext4
    └─ 不存在 → 输出错误信息
```

### Playbook

```yaml
- hosts: all
  tasks:
    - block:
        - name: create lvm 600m
          lvol:
            vg: research
            lv: data
            size: 600m
      rescue:
        - name: output fail msg
          debug:
            msg: Could not create logical volume of that size
        - name: create lvm 400m
          lvol:
            vg: research
            lv: data
            size: 400m
      always:
        - name: format lvm
          filesystem:
            fstype: ext4
            dev: /dev/research/data
      when: "'research' in ansible_lvm.vgs"

    - name: search not exists
      debug:
        msg: Volume group does not exist
      when: "'research' not in ansible_lvm.vgs"
```

### 代码逐行解析

#### 第一个 task：block/rescue/always

```yaml
- block:
    # 尝试创建 600m 逻辑卷
- rescue:
    # 如果 block 失败，输出提示 + 创建 400m
- always:
    # 无论成功失败都执行格式化
when: "'research' in ansible_lvm.vgs"  # 整个 block 的前置条件
```

**关键点**：`when` 是任务级指令，必须和 `- name:` 对齐（第8格），不是和模块参数对齐（第10格）。

#### 第二个 task：卷组不存在时的处理

```yaml
- name: search not exists
  debug:
    msg: Volume group does not exist
  when: "'research' not in ansible_lvm.vgs"  # 和 debug: 对齐
```

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
