---
id: "kb-rhce-ansible-foundations"
title: "RHCE 场景 1–5：Ansible 基础与系统角色"
summary: "Ansible 配置、仓库、软件包、Timesync 和 SELinux 系统角色。"
category: "认证考试"
status: "published"
order: 31
parent: "kb-certification-rhce"
tags: ["rhce", "ansible", "rhel-system-roles"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhce.md"
applicableVersion: "RHCE 9.0"
---

# RHCE 场景 1–5：Ansible 基础与系统角色

## 考试环境概览

| 主机 | IP | 角色 |
|------|-----|------|
| workstation.lab.example.com | 172.25.250.9 | Ansible 控制节点 |
| servera.lab.example.com | 172.25.250.10 | 受管节点 (dev) |
| serverb.lab.example.com | 172.25.250.11 | 受管节点 (test) |
| serverc.lab.example.com | 172.25.250.12 | 受管节点 (prod) |
| serverd.lab.example.com | 172.25.250.13 | 受管节点 (prod) |
| bastion.lab.example.com | 172.25.250.254 | 受管节点 (balancers) |

**关键信息：**

| 项目 | 值 |
|------|-----|
| root 密码 | `redhat` |
| Ansible 用户 | `devops` |
| 工作目录 | `/home/devops/ansible/` |
| 所有操作 | 以 devops 用户在 ansible 目录下执行 |
| 镜像仓库 | `utility.lab.example.com`，用户 `admin`，密码 `redhat` |
| 内容源 | `http://content.example.com` |
| 评分方式 | 重置受管节点 → 从控制节点运行你的 playbook → 评估结果 |

---

## 一、安装和配置 Ansible

### 题目要求

1. 安装 Ansible 软件包
2. 创建静态清单文件 `/home/devops/ansible/inventory`
3. 创建配置文件 `/home/devops/ansible/ansible.cfg`

### 清单文件

```ini
[dev]
servera

[test]
serverb

[prod]
serverc
serverd

[balancers]
bastion

[webservers:children]
prod
```

### 配置文件

```ini
[defaults]
inventory = /home/devops/ansible/inventory
remote_user = devops
roles_path = /home/devops/ansible/roles
host_key_checking = false
collections_path = /home/devops/ansible/mycollections:/usr/share/ansible/collections

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
```

### 扩展开的知识点

#### ansible.cfg 配置段

| 配置段 | 作用 |
|--------|------|
| `[defaults]` | 全局默认配置（inventory、remote_user、roles_path 等） |
| `[privilege_escalation]` | 权限提升专用配置（become、sudo 等） |

两个 section 是**并列关系**，不是嵌套。`[defaults]` 管"连谁"，`[privilege_escalation]` 管"用什么身份干活"。

#### 关键配置项

| 配置项 | 含义 |
|--------|------|
| `remote_user = devops` | SSH 连接用户名 |
| `roles_path` | 角色查找路径 |
| `host_key_checking = false` | 跳过 SSH 主机密钥确认 |
| `collections_path` | 集合查找路径，支持冒号分隔多个路径 |
| `become = True` | 启用 sudo 提权 |
| `become_user = root` | 提权目标用户 |
| `become_ask_pass = False` | 不询问 sudo 密码（已配置 NOPASSWD） |

#### 清单语法

| 语法 | 说明 |
|------|------|
| `[groupname]` | 定义主机组 |
| `[groupname:children]` | 定义组的组（父组包含子组成员） |

#### ansible-navigator 配置

```yaml
# /home/devops/.ansible-navigator.yml
ansible-navigator:
  execution-environment:
    image: utility.lab.example.com/ee-supported-rhel8:latest
    pull:
      policy: missing
```

#### Podman 镜像仓库配置

```toml
# /etc/containers/registries.conf
[registries.search]
registries = ['utility.lab.example.com']

[registries.insecure]
registries = ['utility.lab.example.com']
```

### 验证

```bash
ansible all -m ping
```

---

## 二、创建受管节点存储库

### 题目要求

创建 `/home/devops/ansible/yum_repo.yml`，在所有受管节点配置两个 YUM 仓库。

### Playbook

```yaml
- hosts: all
  tasks:
    - name: configure BaseOS repo
      ansible.builtin.yum_repository:
        name: rh294_BASE
        description: "rh294 base software"
        baseurl: http://content.example.com/rhel9.0/x86_64/dvd/BaseOS
        enabled: yes
        gpgcheck: yes
        gpgkey: http://content.example.com/rhel9.0/x86_64/dvd/RPM-GPG-KEY-redhat-release
        file: rhel_dvd

    - name: configure AppStream repo
      ansible.builtin.yum_repository:
        name: rh294_STREAM
        description: "rh294 stream software"
        baseurl: http://content.example.com/rhel9.0/x86_64/dvd/AppStream
        enabled: yes
        gpgcheck: yes
        gpgkey: http://content.example.com/rhel9.0/x86_64/dvd/RPM-GPG-KEY-redhat-release
        file: rhel_dvd
```

### 扩展开的知识点

#### yum_repository 模块参数

| 参数 | 含义 |
|------|------|
| `name` | 仓库标识名（.repo 文件中的 `[name]`） |
| `description` | 仓库描述（显示在 `dnf repolist`） |
| `baseurl` | 软件包下载地址 |
| `gpgcheck` | 是否启用 GPG 签名检查（`yes`/`no`） |
| `gpgkey` | GPG 公钥 URL |
| `enabled` | 是否启用仓库（`yes`/`no`） |
| `file` | repo 文件名（不带 `.repo` 后缀），模块**自动追加** `.repo` |

#### file 参数详解

- 不写 `file`：默认用 `name` 的值作为文件名
- 两个 task 共用 `file: rhel_dvd` → 合并写入 `/etc/yum.repos.d/rhel_dvd.repo`
- 一个 .repo 文件可以有多个 `[section]`
- 不要手动加 `.repo` 后缀，模块会自动加

### 执行

```bash
ansible-navigator run yum_repo.yml -i inventory -m stdout
# 或
ansible-playbook yum_repo.yml
```

### 验证

```bash
ansible all -m shell -a 'cat /etc/yum.repos.d/rhel_dvd.repo'
ansible all -m shell -a 'yum clean all && yum makecache'
```

---

## 三、安装软件包

### 题目要求

创建 `/home/devops/ansible/packages.yml`：
1. 将 php 和 mariadb 安装到 dev、test、prod 主机组
2. 将 Development Tools 包组安装到 dev 主机组
3. 将 dev 主机组中所有软件包更新到最新版

### Playbook

```yaml
- hosts: dev, test, prod
  tasks:
    - name: install mariadb php
      ansible.builtin.yum:
        name: "&#123;&#123; item }}"
        state: present
      loop:
        - php
        - mariadb

- hosts: dev
  tasks:
    - name: install Development Tools
      ansible.builtin.yum:
        name: "@Development Tools"
        state: present

- hosts: dev
  tasks:
    - name: update pkgs
      ansible.builtin.yum:
        name: '*'
        state: latest
```

### 扩展开的知识点

#### loop 循环

```yaml
name: "&#123;&#123; item }}"
loop:
  - php
  - mariadb
```

- `&#123;&#123; item }}` 是 Jinja2 模板的循环变量
- `loop` 列表中几个值就执行几次
- 更简洁写法：`name: [php, mariadb]`（不需要 loop）

#### yum 模块 state 参数

| state | 行为 |
|-------|------|
| `present` | 已装就跳过，没装就装上 |
| `latest` | 检查更新，有就更新 |
| `absent` | 卸载 |

#### 通配符和包组

| 写法 | 含义 |
|------|------|
| `name: '*'` | 所有软件包 |
| `name: "@Development Tools"` | `@` 前缀表示软件包组 |

#### 一个 YAML 多个 Play

一个 playbook 可以包含多个 Play（用 `- hosts:` 分隔），每个 Play 针对不同主机组执行不同任务。

### 验证

```bash
ansible dev,test,prod -m shell -a 'rpm -q php'
```

---

## 四、使用 Timesync RHEL 系统角色

### 题目要求

创建 `/home/devops/ansible/timesync.yml`，使用 timesync 角色配置 NTP 时间服务器 `classroom.example.com`。

### 前置准备

```bash
yum -y install rhel-system-roles
cp -r /usr/share/ansible/roles/rhel-system-roles.timesync/ roles/timesync
```

### Playbook

```yaml
- hosts: all
  vars:
    timesync_ntp_servers:
      - hostname: classroom.example.com
        iburst: yes
  roles:
    - timesync
```

### 扩展开的知识点

#### RHEL 系统角色

- 安装 `rhel-system-roles` 后，角色文件在 `/usr/share/ansible/roles/`
- 复制到本地 `roles/` 目录方便 playbook 引用和管理
- 复制的是角色的**定义文件**（tasks、defaults、templates 等），不是软件包

#### vars 变量

- `vars:` 定义变量，传递给 roles 控制角色行为
- `timesync_ntp_servers` 是 timesync 角色要求的变量名
- `iburst: yes` 启用快速同步（开机时连续发 8 个包快速校时）
- 可以配多个 NTP 服务器，按列表顺序优先级从高到低

### 验证

```bash
ansible all -m shell -a 'chronyc sources'
```

---

## 五、使用 SELINUX RHEL 系统角色

### 题目要求

在所有节点使用 SELinux 角色，将 SELinux 设置为 enforcing 强制模式。

### Playbook

```yaml
- hosts: all
  vars:
    selinux_policy: targeted
    selinux_state: enforcing
  roles:
    - role: selinux
      become: true
```

### 扩展开的知识点

#### SELinux 变量

| 变量 | 值 | 含义 |
|------|-----|------|
| `selinux_policy` | `targeted` | 策略类型（只约束特定进程） |
| `selinux_state` | `enforcing` | 强制模式（违反就阻止） |

#### SELinux 三种状态

| 状态 | 命令 | 说明 |
|------|------|------|
| `enforcing` | `setenforce 1` | 强制模式 |
| `permissive` | `setenforce 0` | 宽容模式（只警告不阻止） |
| `disabled` | 改配置文件重启 | 完全关闭 |

#### become: true 详解

- 用 root 权限执行该角色（通过 sudo 提权）
- SELinux 状态修改需要 root 权限
- 跟 ansible.cfg 的 `[privilege_escalation]` 区别：
  - `become: true` 只对当前角色/play 生效
  - `[privilege_escalation]` 全局生效

### 验证

```bash
ansible all -m shell -a 'getenforce'
```

---
