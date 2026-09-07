---
id: "kb-rhce-vault-users-cron"
title: "RHCE 场景 16–19：Vault、用户与计划任务"
summary: "Ansible Vault、用户账户、库密钥与 Cron 场景。"
category: "认证考试"
status: "published"
order: 35
parent: "kb-certification-rhce"
tags: ["rhce", "vault", "user", "cron"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhce.md"
applicableVersion: "RHCE 9.0"
---

# RHCE 场景 16–19：Vault、用户与计划任务

## 十六、创建密码库

### 题目要求

创建 Ansible Vault 存储密码，加密密码为 `fgydsxsxsbxs`。

### 实际操作

```bash
# 创建变量文件
vim locker.yml
# 内容：
# pw_developer: Imadev
# pw_manager: Imamgr

# 创建密码文件
echo fgydsxsxsbxs > secret.txt

# 加密
ansible-vault encrypt --vault-password-file=secret.txt locker.yml
```

### 扩展开的知识点

#### ansible-vault 命令

| 命令 | 作用 |
|------|------|
| `ansible-vault encrypt` | 加密文件 |
| `ansible-vault decrypt` | 解密文件 |
| `ansible-vault view` | 查看加密文件内容 |
| `ansible-vault edit` | 编辑加密文件 |
| `ansible-vault rekey` | 更改密码 |
| `ansible-vault create` | 创建新加密文件 |

#### 运行 playbook 时解密

```bash
ansible-playbook --vault-password-file=secret.txt playbook.yml
ansible-playbook --ask-vault-pass playbook.yml
```

---

## 十七、创建用户账户

### 题目要求

创建 `/home/devops/ansible/users.yml`，根据 `user_list.yml` 和 `locker.yml` 创建用户。

### Playbook

```yaml
- hosts: dev, test
  vars_files:
    - locker.yml
    - user_list.yml
  tasks:
    - name: Ensure group "devops" exists
      group:
        name: devops
        state: present

    - name: Create user in developer
      user:
        name: "&#123;&#123; item.name }}"
        uid: "&#123;&#123; item.uid }}"
        groups: devops
        password: "&#123;&#123; pw_developer | password_hash('sha512') }}"
      loop: "&#123;&#123; users }}"
      when: item.job == 'developer'

- hosts: prod
  vars_files:
    - locker.yml
    - user_list.yml
  tasks:
    - name: Ensure group "opsmgr" exists
      group:
        name: opsmgr
        state: present

    - name: Create user in manager
      user:
        name: "&#123;&#123; item.name }}"
        uid: "&#123;&#123; item.uid }}"
        groups: opsmgr
        password: "&#123;&#123; pw_manager | password_hash('sha512') }}"
      loop: "&#123;&#123; users }}"
      when: item.job == 'manager'
```

### 代码逐行解析

#### `item` 变量的来源 ⭐

关键在 `loop: "&#123;&#123; users }}"`：

- `users` 是从 `user_list.yml` 加载的变量，结构是一个**列表（list）**，每个元素是一个**字典（dict）**
- `user_list.yml` 内容示例：

```yaml
users:
  - name: alice
    uid: 1010
    job: developer
  - name: bob
    uid: 1011
    job: manager
  - name: charlie
    uid: 1012
    job: developer
```

- 当 Ansible 执行 `loop: "&#123;&#123; users }}"` 时，**遍历列表，每次循环把当前元素赋值给 `item` 变量**

| 循环次数 | `item` 的值 | `item.name` | `item.job` |
|---------|-----------|------------|-----------|
| 第1次 | `{name: alice, uid: 1010, job: developer}` | alice | developer |
| 第2次 | `{name: bob, uid: 1011, job: manager}` | bob | manager |
| 第3次 | `{name: charlie, uid: 1012, job: developer}` | charlie | developer |

#### `item.job` 属性详解

- `item` 是字典，`item.job` 用**点号访问字典的键**
- 类比 Python：`item["job"]` 等价于 `item.job`
- `when: item.job == 'developer'` 按条件过滤，只处理 job 为 developer 的用户

#### `loop` + `when` 执行逻辑

```
loop 遍历 users 列表
    │
    ├─ item = {name: alice, job: developer}
    │   when: item.job == 'developer' → ✅ 执行创建任务
    │
    ├─ item = {name: bob, job: manager}
    │   when: item.job == 'developer' → ❌ 跳过
    │
    └─ item = {name: charlie, job: developer}
        when: item.job == 'developer' → ✅ 执行创建任务
```

**一句话**：`item` 是 `loop` 循环自动提供的变量，每次循环指向列表中的当前元素。`item.job` 就是取这个元素字典里 `job` 键的值。

#### `when` 为什么不需要 `&#123;&#123; }}`？⭐

```yaml
when: item.job == 'developer'      # ✅ 不需要 &#123;&#123; }}
name: "&#123;&#123; item.name }}"            # ❌ 模块参数必须加 &#123;&#123; }}
```

| 位置 | 是否自动解析 | 写法 |
|------|------------|------|
| `when:` | ✅ 自动当成 Jinja2 表达式 | `when: item.job == 'developer'` |
| `loop:` | ✅ 自动当成 Jinja2 表达式 | `loop: "&#123;&#123; users }}"` |
| 模块参数（name、uid 等） | ❌ 默认是字符串，不会自动解析 | `name: "&#123;&#123; item.name }}"` |

**原因**：
- `when` 是 Ansible **关键字**，从设计上就知道后面要跟条件表达式，自动解析
- 模块参数（如 user 的 `name`）是模块自己定义的，Ansible 不知道你传的是变量还是字面字符串，必须用 `&#123;&#123; }}` 显式插值

**类比 Python**：
```python
# when 类比 — 直接写表达式
if item.job == 'developer':

# name 类比 — 字符串里要插值
name = f"{item['name']}"
```

**一句话记住**：`when` 后面永远不需要 `&#123;&#123; }}`，它是关键字自动解析。模块参数默认是字符串，要插变量必须加 `&#123;&#123; }}`。

### 扩展开的知识点

#### vars_files

- 从外部 YAML 文件加载变量
- 可以加载加密的 Vault 文件
- 变量在 play 级别可用

#### password_hash 过滤器

- `&#123;&#123; pw | password_hash('sha512') }}`：生成 SHA512 哈希密码
- 配合 user 模块的 `password` 参数使用

#### user 模块

| 参数 | 含义 |
|------|------|
| `name` | 用户名 |
| `uid` | 用户 ID |
| `groups` | 附加组 |
| `password` | 加密后的密码字符串 |

#### 执行方式

```bash
ansible-playbook --vault-password-file=secret.txt users.yml
ansible-navigator run users.yml -m stdout --vault-password-file=secret.txt
```

---

## 十八、更新 Ansible 库的密钥

### 题目要求

更改 Vault 密码：旧密码 `insecure4sure` → 新密码 `bbe2de98389b`。

### 实际操作

```bash
ansible-vault rekey salaries.yml
# Vault password: insecure4sure
# New Vault password: bbe2de98389b
# Confirm New Vault password: bbe2de98389b
```

### 扩展开的知识点

#### ansible-vault rekey

- 更改 Vault 加密文件的密码
- 交互式输入旧密码和新密码
- 文件内容不变，只改变加密密钥

---

## 十九、创建计划任务

### 题目要求

为 natasha 用户创建计划任务，每隔 2 分钟执行 `echo hello`，playbook 文件为 `cron.yml`，在 dev 组运行。

### Playbook

```yaml
- hosts: dev
  tasks:
    - name: create natasha
      user:
        name: natasha
        state: present

    - name: create cron tasks
      cron:
        name: "exec tasks every 2 minute"
        minute: "*/2"
        user: natasha
        job: "echo hello"
```

### 扩展开的知识点

#### cron 模块

| 参数 | 含义 | 取值 |
|------|------|------|
| `name` | 任务描述（用于标识和删除） | 任意字符串 |
| `minute` | 分钟 | `*/2`（每2分钟） |
| `hour` | 小时 | `*`（每小时） |
| `day` | 日 | `*`（每天） |
| `month` | 月 | `*`（每月） |
| `weekday` | 星期 | `*`（每天） |
| `user` | 执行用户 | 用户名 |
| `job` | 执行的命令 | 命令字符串 |
| `state` | absent 删除任务 | `present`/`absent` |

#### 删除任务

```yaml
- cron:
    name: "exec tasks every 2 minute"
    state: absent
```

### 验证

```bash
crontab -l -u natasha
# #Ansible: exec tasks every 2 minute
# */2 * * * * echo hello
```

---
