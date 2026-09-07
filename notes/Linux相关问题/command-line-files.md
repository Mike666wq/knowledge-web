---
id: "kb-linux-command-line-files"
title: "Linux 文件与文本命令"
summary: "归档、查找、文件属性与 sed 文本替换。"
category: "操作系统"
status: "published"
order: 11
parent: "kb-linux-operations"
tags: ["tar", "find", "chattr", "sed"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Linux 文件与文本命令

## 1. tar 压缩选项速查

| 选项 | 压缩格式 | 文件后缀 | 解压命令 |
|------|----------|----------|----------|
| `-czf` | gzip | `.tar.gz` / `.tgz` | `-xzf` |
| `-cjf` | bzip2 | `.tar.bz2` | `-xjf` |
| `-cJf` | xz | `.tar.xz` | `-xJf` |
| `-caf` | 自动检测 | 任意 | `-xaf` |

**常用示例：**

```bash
# 压缩
tar -czf archive.tar.gz /path/to/dir      # gzip
tar -cjf archive.tar.bz2 /path/to/dir     # bzip2
tar -cJf archive.tar.xz /path/to/dir      # xz

# 解压
tar -xzf archive.tar.gz
tar -xjf archive.tar.bz2
tar -xJf archive.tar.xz
tar -xaf archive.tar.gz                    # 自动检测格式
```

**gzip 与 bzip2 格式对比：**

| | gzip | bzip2 |
|---|---|---|
| **魔数 (Magic)** | `1f 8b` | `42 5a` ("BZ") |
| **头部结构** | 10 字节固定头 | 4 字节魔数 + 1 字节版本 |
| **压缩算法** | DEFLATE (LZ77 + Huffman) | Burrows-Wheeler + Huffman |
| **尾部** | CRC32 + 原始大小 (各 4 字节) | CRC + 原始大小 |

⚠️ 两者格式完全不同，不能互相替换或混合使用。

---


---

## 7. find 命令综合题

### 脚本内容

```bash
#!/bin/bash
find /usr -size +30k -size -50k -perm -4000 -type f > /root/myfile
```

### 参数拆解

| 参数 | 含义 |
|---|---|
| `/usr` | 从 `/usr` 目录开始搜索 |
| `-size +30k` | 大于 30KB |
| `-size -50k` | 小于 50KB |
| `-perm -4000` | 包含 SUID 权限位 |
| `-type f` | 只找普通文件 |
| `> /root/myfile` | 结果写入文件 |

两个 `-size` 同时使用是 AND 关系：`30k < 文件 < 50k`

### 特殊权限位

| 权限位 | 数字 | 含义 |
|---|---|---|
| SUID | 4000 | 执行时以文件所有者身份运行 |
| SGID | 2000 | 执行时以文件所属组身份运行 |
| SBIT | 1000 | 粘滞位（如 /tmp） |

### 创建和运行

```bash
vim /usr/local/bin/mysearch
chmod a+x /usr/local/bin/mysearch
/usr/local/bin/mysearch
cat /root/myfile
```

### 脚本命名说明

Linux 里文件扩展名不影响执行。系统只关心：
1. 文件有没有执行权限（`chmod +x`）
2. 文件开头有没有 shebang（`#!/bin/bash`）

`.sh` 后缀只是给人看的，考试/规范推荐不加后缀（像系统命令 `ls`、`grep` 一样）。




---

## 8. chattr -i 锁定文件属性

```bash
chattr +i /etc/resolv.conf   # 加 immutable 属性，文件不可改/删/重命名（root 也不行）
chattr -i /etc/resolv.conf   # 去掉 immutable 属性，恢复可编辑
```

**用途**：RHEL 7+ 的 `/etc/resolv.conf` 被 NetworkManager 管理，手动改 DNS 后用 `chattr +i` 锁死防止被覆盖；需要再改时先 `chattr -i` 解锁。

**考试常考**：改 DNS 配置前先解锁，改完再锁上。

---


---

## 10. sed 替换命令详解

```bash
sed -i "s/^Listen  80/Listen 82/g"
```

### 参数拆解

| 参数 | 含义 |
|------|------|
| `sed` | Stream Editor，流编辑器 |
| `-i` | 原地编辑（in-place），直接修改文件 |
| `s/` | 替换命令（substitute） |
| `^Listen  80` | 匹配内容（`^` = 行首锚定） |
| `Listen 82` | 替换内容 |
| `g` | 全局替换（一行中多个匹配全换） |

### 正则说明

- `^` 行首锚定：只匹配行开头的，不匹配行中间的
- 没有 `^`：一行中任何位置出现都替换
- 有 `g`：一行中所有匹配都替换
- 没有 `g`：只替换每行第一个匹配

### 常见用法

```bash
# 替换并备份原文件
sed -i.bak "s/old/new/g" file.conf

# 只输出不改文件（不加 -i）
sed "s/old/new/g" file.conf

# 删除空行
sed -i '/^$/d' file.conf

# 删除行首空格
sed -i 's/^[[:space:]]*//' file.conf
```

---


---

<!-- KB:INSERT:linux-command-additions -->
