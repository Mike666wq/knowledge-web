---
id: "kb-rhce-content-reports"
title: "RHCE 场景 13–15：文件、Web 与报告"
summary: "文件替换、Web 内容目录和硬件报告 Playbook。"
category: "认证考试"
status: "published"
order: 34
parent: "kb-certification-rhce"
tags: ["rhce", "web", "report"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhce.md"
applicableVersion: "RHCE 9.0"
---

# RHCE 场景 13–15：文件、Web 与报告

## 十三、修改文件内容

### 题目要求

创建 `/home/devops/ansible/issue.yml`，根据主机组不同写入不同的 `/etc/issue`：
- dev → "Development"
- test → "Test"
- prod → "Production"

### Playbook

```yaml
- hosts: all
  tasks:
    - name: write Development to dev
      copy:
        content: "Development\n"
        dest: /etc/issue
      when: "'dev' in group_names"

    - name: write Test to test
      copy:
        content: "Test\n"
        dest: /etc/issue
      when: "'test' in group_names"

    - name: write Production to prod
      copy:
        content: "Production\n"
        dest: /etc/issue
      when: "'prod' in group_names"
```

### 扩展开的知识点

#### when 条件判断

| 条件 | 含义 |
|------|------|
| `'dev' in group_names` | 当前主机属于 dev 组 |
| `group_names` | 当前主机所属的所有组列表 |

#### copy 模块 content 参数

- `content`：直接写入字符串内容（不需要源文件）
- `dest`：目标文件路径

### 验证

```bash
ansible dev,test,prod -m shell -a 'cat /etc/issue'
```

---

## 十四、创建 Web 内容目录

### 题目要求

创建 Playbook，在 dev 主机组：
1. 安装启动 httpd
2. 创建 `/webdev` 目录（SGID），拥有组 devops
3. 符号链接 `/var/www/html/webdev` → `/webdev`
4. 创建 `/webdev/index.html` 内容为 "Development"

### Playbook

```yaml
- hosts: dev
  tasks:
    - name: install httpd
      yum:
        name: httpd
        state: present

    - name: enable httpd
      systemd:
        name: httpd
        enabled: yes
        state: started

    - name: enable 80/tcp
      firewalld:
        service: http
        immediate: yes
        permanent: yes
        state: enabled

    - name: Create webdev directory
      file:
        path: /webdev
        state: directory
        owner: root
        group: devops
        mode: '2775'
        setype: httpd_sys_content_t

    - name: Create file
      copy:
        content: "Development\n"
        dest: /webdev/index.html
        setype: httpd_sys_content_t

    - name: Create soft link
      file:
        src: /webdev
        dest: /var/www/html/webdev
        state: link
```

### 扩展开的知识点

#### HTTPD 工作原理与软链接

**为什么需要软链接？**

```
httpd 默认网站根目录：/var/www/html/
访问 http://servera.lab.example.com/webdev/
       ↓
httpd 实际查找：/var/www/html/webdev/
```

**但题目要求文件放在 `/webdev/`（根目录下），不是 `/var/www/html/webdev/`**

```
实际文件位置：/webdev/index.html        ← 根目录下的 webdev
httpd 期望位置：/var/www/html/webdev/     ← 网站根目录下

两个位置不同！httpd 找不到文件！
```

**解决方案：创建软链接**

```yaml
- name: Create soft link
  file:
    src: /webdev                    # 原始位置（实际文件在这）
    dest: /var/www/html/webdev      # httpd 期望的位置
    state: link                     # 创建符号链接
```

**流程图**：

```
用户访问 http://servera.lab.example.com/webdev/
    ↓
httpd 查找 /var/www/html/webdev/
    ↓
发现是软链接 → 跳转到 /webdev/
    ↓
读取 /webdev/index.html
    ↓
返回 "Development"
```

**一句话理解**：内容放在 `/webdev`，但 httpd 只认 `/var/www/html/`，所以用软链接“骗”一下 httpd。

#### 文件权限 mode

| mode | 含义 |
|------|------|
| `2775` | SGID（`2`）+ rwxrwxr-x |

- `2`（首位）= SGID：在该目录下创建的文件继承目录的组
- `7` = rwx（owner）
- `7` = rwx（group）
- `5` = r-x（other）

#### SELinux 上下文

| 参数 | 含义 |
|------|------|
| `setype: httpd_sys_content_t` | 设置 SELinux 类型标签为 Web 内容 |

#### 符号链接 file 模块参数

| 参数 | 含义 |
|------|------|
| `src` | 原始文件/目录路径 |
| `dest` | 链接文件路径 |
| `state: link` | 创建符号链接 |
| `state: hard` | 创建硬链接 |
| `state: absent` | 删除 |

#### 符号链接 vs 硬链接

| 类型 | 特点 |
|------|------|
| 符号链接（软链接） | 独立文件，指向源文件路径，源文件删除后链接失效 |
| 硬链接 | 和源文件共享 inode，源文件删除后仍可访问 |

### 验证

```bash
curl http://servera.lab.example.com/webdev/index.html
```

---

## 十五、生成硬件报告

### 题目要求

创建 `/home/devops/ansible/hwreport.yml`，生成 `/root/hwreport.txt`，包含：主机名、内存、BIOS 版本、vda/vdb 磁盘大小。

### Playbook

```yaml
- hosts: all
  tasks:
    - name: Create report file
      get_url:
        url: http://172.25.254.254/content/hwreport.empty
        dest: /root/hwreport.txt

    - name: Get inventory_hostname
      replace:
        path: /root/hwreport.txt
        regexp: 'inventoryhostname'
        replace: '&#123;&#123; inventory_hostname }}'

    - name: Get memory total size
      replace:
        path: /root/hwreport.txt
        regexp: 'memory_in_MB'
        replace: "&#123;&#123; ansible_memtotal_mb | string }}"

    - name: Get bios version
      replace:
        path: /root/hwreport.txt
        regexp: 'BIOS_version'
        replace: "&#123;&#123; ansible_bios_version }}"

    - name: Get disk vda size
      replace:
        path: /root/hwreport.txt
        regexp: 'disk_vda_size'
        replace: "&#123;&#123; ansible_devices.vda.size | default('NONE') }}"

    - name: Get disk vdb size
      replace:
        path: /root/hwreport.txt
        regexp: 'disk_vdb_size'
        replace: "&#123;&#123; ansible_devices.vdb.size | default('NONE') }}"
```

### 代码逐行解析

#### replace 模块基本逻辑

```yaml
replace:
  path: /root/hwreport.txt      # 目标文件
  regexp: '占位符文本'           # 用正则找到要替换的字符串
  replace: "实际值"              # 替换成什么
```

文件里预先有一堆占位符（如 `memory_in_MB`、`BIOS_version` 等），playbook 的任务就是把它们替换成真实的系统信息。

#### 各变量详解

| 变量 | 含义 | 类型 |
|------|------|------|
| `inventory_hostname` | inventory 中定义的主机名 | 字符串，直接用 |
| `ansible_memtotal_mb` | 目标主机总内存（MB），如 2048 | 整数(int) |
| `ansible_bios_version` | BIOS/固件版本号 | 字符串 |
| `ansible_devices.vda.size` | 第一块虚拟磁盘大小 | 字符串 |
| `ansible_devices.vdb.size` | 第二块虚拟磁盘大小 | 字符串 |

#### `ansible_memtotal_mb | string` 详解 ⭐

- `ansible_memtotal_mb`：setup 模块自动采集的 facts，返回**整数**（如 2048）
- `| string`：Jinja2 类型转换过滤器，`2048`(int) → `"2048"`(string)
- **为什么加**：`replace` 模块的 `replace` 参数期望字符串，直接用整数可能报类型错误
- 类比 Python：`str(2048)` 的效果
- 考试里如果忘了加 `| string`，可能不会报错（不同版本行为不同），但加上是保险写法

#### `default('NONE')` 过滤器

- 用法：`&#123;&#123; ansible_devices.vda.size | default('NONE') }}`
- 含义：如果值不存在（比如机器没有 vda 盘），返回 `'NONE'` 而不是报 UndefinedError
- 用于处理硬件项不存在的情况（如 bastion 没有 vdb 磁盘）

### 扩展开的知识点

#### get_url 模块

- 从 URL 下载文件到目标主机

#### replace 模块

| 参数 | 含义 |
|------|------|
| `path` | 要修改的文件路径 |
| `regexp` | 正则表达式匹配 |
| `replace` | 替换内容 |

#### default 过滤器

- `&#123;&#123; var | default('NONE') }}`：如果变量不存在则使用默认值
- 用于处理硬件项不存在的情况（如 bastion 没有 vdb 磁盘）

#### 常用 Facts 变量

| 变量 | 含义 |
|------|------|
| `ansible_memtotal_mb` | 内存总量（MB） |
| `ansible_bios_version` | BIOS 版本 |
| `ansible_devices.vda.size` | vda 磁盘大小 |

### 验证

```bash
ansible all -m shell -a 'cat /root/hwreport.txt'
```

---
