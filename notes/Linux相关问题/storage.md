---
id: "kb-linux-storage"
title: "Linux 磁盘、LVM 与 Swap"
summary: "磁盘分区、文件系统、LVM 扩缩容和 Swap 管理。"
category: "操作系统"
status: "published"
order: 13
parent: "kb-linux-operations"
tags: ["disk", "lvm", "swap"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Linux 磁盘、LVM 与 Swap

## 4. 磁盘与存储管理
### LVM 三层架构

```
物理硬盘/分区 → 物理卷(PV) → 卷组(VG) → 逻辑卷(LV) → 格式化 → 挂载
   /dev/vdb      pvcreate      vgcreate     lvcreate      mkfs     mount
```

| 层级 | 命令 | 含义 |
|---|---|---|
| **物理卷 (PV)** | `pvcreate` | 把硬盘/分区注册进 LVM |
| **卷组 (VG)** | `vgcreate` | 把 PV 合成一个大存储池 |
| **逻辑卷 (LV)** | `lvcreate` | 从 VG 里切出一块空间 |
| 格式化 | `mkfs` | 创建文件系统 |
| 挂载 | `mount` | 接到目录树上 |

### 扩容逻辑卷

```bash
lvextend -r -L 512M /dev/exam/rhel
```

| 参数 | 含义 |
|---|---|
| `lvextend` | 扩展逻辑卷大小 |
| `-r` | 同时调整文件系统大小（自动 resize） |
| `-L 512M` | 目标大小（绝对大小） |

⚠️ 传统方式需两步：先 `lvextend` 再 `resize2fs`（ext4）或 `xfs_growfs`（xfs）。加 `-r` 一步搞定。

### 创建逻辑卷（含 PE 大小设置）

**题目要求：** 卷组 `myvg`，逻辑卷 `mylv`，PE 大小 16M，LV 大小 50 个 PE（= 800M），文件系统 ext3，挂载 `/mnt/mydata`

```bash
# 1. 创建分区
fdisk /dev/vdb
# n → p → 默认分区号 → +1G

# 2. 设置分区类型为 LVM
# t → 分区号 → 8e

# 3. 保存
# w

# 4. 创建卷组，PE 大小 16M（关键！）
vgcreate -s 16M myvg /dev/vdb3

# 5. 创建逻辑卷（50 个 PE）
lvcreate -l 50 -n mylv myvg

# 6. 格式化为 ext3
mkfs.ext3 /dev/myvg/mylv

# 7. 创建挂载点并永久挂载
mkdir /mnt/mydata
echo '/dev/myvg/mylv /mnt/mydata ext3 defaults 0 0' >> /etc/fstab
mount -a

# 8. 验证
df -Th /mnt/mydata/
```

### `-L` vs `-l` 区别

| 参数 | 含义 | 示例 |
|---|---|---|
| `-L`（大写） | 指定**绝对大小** | `-L 800M` |
| `-l`（小写） | 指定**PE 数量** | `-l 50` |

### PE (Physical Extent) 说明

- PE 是 LVM 最小的存储分配单位，默认 4M
- 逻辑卷大小必须是 PE 大小的整数倍
- 用 `vgcreate -s 16M` 可以修改 PE 大小

### 易错点

| 易错点 | 正确做法 |
|---|---|
| PE 大小忘了改 | `vgcreate -s 16M`，不是默认 4M |
| 用 `-L` 而不是 `-l` | `-l 50`（PE 数量），不是 `-L 50M` |
| 格式化用 ext4 | 题目要求 **ext3** |
| 缩容顺序反了 | 必须先缩文件系统，再缩 LV（扩容顺序相反） |

⚠️ **扩缩容顺序相反：** 扩容先扩 LV 再扩文件系统；缩容先缩文件系统再缩 LV。xfs 文件系统**不能缩容**。

---


---

### Swap 交换区配置
### 完整流程

```bash
# 1. 创建分区
fdisk /dev/vdb
# n → p → 2 → +512M

# 2. 设置分区类型为 swap
# t → 2 → 82

# 3. 保存
# w

# 4. 格式化为 swap
mkswap /dev/vdb2

# 5. 临时启用
swapon /dev/vdb2

# 6. 写入 fstab 永久生效
echo '/dev/vdb2 swap swap defaults 0 0' >> /etc/fstab

# 7. 验证 fstab
swapoff -a
mount -a
swapon -a

# 8. 确认生效
free -m
```

### Swap 是什么？

物理内存 (RAM) 不够用时，把不活跃的数据暂时放到硬盘上，这块硬盘空间就是 Swap。

**为什么需要 Swap？**
- 当物理内存不足时，系统把不活跃的数据从内存搬到磁盘上的 swap 空间，腾出内存给当前需要的进程
- 好处：防止 OOM (Out of Memory) killer 杀进程
- 坏处：磁盘比内存慢几十倍，swap 频繁使用会导致系统变慢

**两种创建 swap 的方式：**

```bash
# 方式一：用文件创建（简单，推荐小容量）
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 方式二：用分区创建（正式环境，已在上方详述）
# fdisk → t → 82 → mkswap → swapon → fstab
```

⚠️ `fallocate` 方式不支持 ZFS 和某些旧内核。创建后记得 `chmod 600`，否则 swap 可能不生效。

### 关键参数说明

| 步骤 | 命令 | 含义 |
|---|---|---|
| 格式化 | `mkswap /dev/vdb2` | 把分区格式化为 swap 格式 |
| 临时启用 | `swapon /dev/vdb2` | 告诉内核开始使用这个 swap |
| 永久生效 | fstab 中 `swap swap defaults 0 0` | 开机自动启用 |
| 停用 | `swapoff -a` | 停用所有 swap |

### fstab 中 swap 条目格式

```
设备文件      挂载目录  格式   选项      备份  自检
/dev/vdb2    swap     swap   defaults   0     0
```

### free -h vs free -m

| 参数 | 输出格式 | 示例 |
|---|---|---|
| `free -h` | 人类可读（G/M/K） | `Mem: 3.7Gi 1.2Gi 2.1Gi ...` |
| `free -m` | 以 MB 为单位 | `Mem: 3812 1234 2156 ...` |
| `free -g` | 以 GB 为单位 | `Mem: 3 1 2 ...` |

**推荐：** 日常使用 `free -h` 最直观，脚本中用 `free -m` 方便解析。

```bash
free -h
#               total   used   free   shared  buff/cache  available
# Mem:          3.7Gi  1.2Gi  2.1Gi   128Mi     400Mi      2.3Gi
# Swap:         2.0Gi  0.0Gi  2.0Gi
```

**输出字段含义：**
| 字段 | 含义 |
|---|---|
| `total` | 总物理内存 |
| `used` | 已用内存（包含 buffer/cache） |
| `free` | 完全空闲的内存 |
| `shared` | 多进程共享的内存 |
| `buff/cache` | 缓冲区/缓存（可回收） |
| `available` | 可用内存（free + 可回收的 cache） |

⚠️ 看内存够不够用，看 `available` 而不是 `free`。

### free -m 输出解读

```
              total   used   free
Swap:           511      0    511     ← 看这行，511M ≈ 512M
```

### 易错点

| 易错点 | 正确做法 |
|---|---|
| 分区号选错 | vdb1 已被 LVM 用，swap 用 vdb2 |
| 没改分区类型 | 必须 `t` → `82` 设为 swap 类型 |
| 只 swapon 没写 fstab | 必须写 fstab 否则重启失效 |
| 忘了验证 fstab | 写完用 `swapoff -a && swapon -a` 测试 |

---


---

### fdisk Partition number 默认值
- `Partition number (1, 2, default 2):` 中默认是 2 的原因：`/dev/vdb1` 已被占用
- MBR 分区表的分区号从 1 开始编号，fdisk 检测到 1 号已被使用，所以默认给出第一个空闲号 2
- 如果磁盘是全新的，默认就是 1
- MBR 最多 4 个主分区（编号 1-4）

---


---

### 分区类型（Partition Type）与修改方法
**分区类型是什么：** 只是一个标签，告诉系统这个分区的用途，不影响实际功能

**常见类型：**
- 83 = Linux（普通分区）
- 82 = Linux swap
- 8e = Linux LVM
- fd = Linux RAID
- ef = EFI System

**修改方法：**
- `fdisk /dev/sdb` → 按 `t` → 输入类型编号
- `gdisk /dev/sdb` → 按 `t` → 输入 GUID 代码
- `parted /dev/sdb set 1 lvm on`（非交互式）
- `sfdisk /dev/sdb <<< ',8e'`（脚本化）

**RHCSA 考试流程（创建 LVM）：**
1. fdisk 创建分区 → t → 改为 8e（LVM）
2. pvcreate /dev/sdb1
3. vgcreate vg0 /dev/sdb1
4. lvcreate -n lv0 -L 500M vg0

**注意：** 改类型只是改标签，不丢数据；但 pvcreate 会写入 LVM 元数据，会清掉原有数据

---


---

### MBR vs GPT 分区表类型
**MBR（Master Boot Record）：**
- 最大 2TB 磁盘
- 最多 4 个主分区（或 3主+1扩展，扩展里分逻辑分区）
- BIOS 启动用
- 工具：fdisk、parted（默认 MBR）

**GPT（GUID Partition Table）：**
- 支持超 2TB 磁盘
- 最多 128 个主分区
- UEFI 启动用
- 工具：gdisk、parted

**查看分区表类型：**
- `lsblk -f`
- `parted /dev/sdb print`（看 Label：msdos=MBR，gpt=GPT）
- `fdisk -l /dev/sdb`（看 disklabel type）

**创建分区表：**
- `fdisk /dev/sdb` → 默认 MBR
- `parted /dev/sdb mklabel msdos` → MBR
- `parted /dev/sdb mklabel gpt` → GPT

**RHCSA 考试：** 一般用 MBR + fdisk，简单直接

---


---


---
