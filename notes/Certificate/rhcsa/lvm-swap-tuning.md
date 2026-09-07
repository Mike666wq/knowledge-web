---
id: "kb-rhcsa-lvm-swap-tuning"
title: "RHCSA 场景 21–24：LVM、Swap 与调优"
summary: "逻辑卷扩容、Swap、LVM 创建和 tuned 考试流程。"
category: "认证考试"
status: "published"
order: 24
parent: "kb-certification-rhcsa"
tags: ["rhcsa", "lvm", "swap", "tuned"]
updatedAt: "2026-08-26"
source: "Migrated from docs/rhcsa.md"
applicableVersion: "RHCSA 9.0"
---

# RHCSA 场景 21–24：LVM、Swap 与调优

> 原理与日常运维以 [Linux 磁盘、LVM 与 Swap](/linux/storage) 为 Canonical；本文只保留考试步骤。

## 21. 调整逻辑卷大小

### 题目要求

将 `exam` 卷组中 `rhel` 逻辑卷扩容到 512M，保留文件系统内容。

### 实际操作

```bash
# 如果逻辑卷不存在，先创建 LVM 环境
# 1. 创建分区
parted /dev/vdb mklabel gpt
parted /dev/vdb mkpart primary 0% 100%

# 2. 创建 PV/VG/LV
pvcreate /dev/vdb1
vgcreate exam /dev/vdb1
lvcreate -L 480M -n rhel exam

# 3. 格式化并挂载
mkfs.xfs /dev/exam/rhel
mkdir /mnt/rhel
echo '/dev/exam/rhel /mnt/rhel xfs defaults 0 0' >> /etc/fstab
mount -a

# 扩容（题目核心操作）
lvextend -r -L 512M /dev/exam/rhel
```

### 扩展开的知识点

#### lvextend / lvreduce

| 参数 | 含义 |
|------|------|
| `-r` | 同时调整文件系统大小（resize2fs/xfs_growfs） |
| `-L SIZE` | 指定新大小（绝对） |
| `-L +SIZE` | 增加多少（相对） |

#### 验证命令详解

| 命令 | 用途 | 显示内容 |
|------|------|----------|
| `df -Th` | 查看已挂载文件系统 | 文件系统类型（xfs/ext4）+ 使用率 + 挂载点 |
| `lsblk` | 查看块设备树 | 所有块设备层级关系（含未挂载的分区/LV） |
| `lvs` | 查看逻辑卷 | 逻辑卷名、大小、所属 VG |

#### df -Th vs lsblk 区别

- `df -Th`：显示**已挂载**文件系统的实际使用情况，看不到未挂载的分区
- `lsblk`：显示**所有块设备**的层级关系（磁盘→分区→VG→LV），不管有没有挂载

#### 其他相关命令

```bash
lvs              # 查看逻辑卷信息
vgs              # 查看卷组信息
pvs              # 查看物理卷信息
blkid            # 查看设备 UUID 和文件系统类型
```

#### LVM 常用命令

| 命令 | 作用 |
|------|------|
| `lvs` / `lvdisplay` | 查看逻辑卷 |
| `vgs` / `vgdisplay` | 查看卷组 |
| `pvs` / `pvdisplay` | 查看物理卷 |
| `lvcreate` | 创建逻辑卷 |
| `lvextend` | 扩容逻辑卷 |
| `lvreduce` | 缩减逻辑卷 |
| `lvremove` | 删除逻辑卷 |

### 验证

```bash
df -Th /mnt/rhel
# Size 在 507M 左右正常
# 确认 fstab 中有自动挂载项
```

---

## 22. 配置 swap 交换分区

### 题目要求

向 serverb 添加一个 512MiB 交换分区，开机自动挂载。

### 实际操作

```bash
# 1. 创建分区
fdisk /dev/vdb
# n → 直接回车 → 分区号默认 → 起始扇区默认 → +512M → t → 分区号默认 → 82 → w

# 2. 格式化 swap
mkswap /dev/vdb2

# 3. 配置开机自动挂载
echo '/dev/vdb2 swap swap defaults 0 0' >> /etc/fstab

# 4. 启用所有 swap
swapon -a
```

### 扩展开的知识点

#### fdisk 操作

| 键 | 作用 |
|-----|------|
| `n` | 新建分区 |
| `d` | 删除分区 |
| `p` | 打印分区表 |
| `t` | 更改分区类型 |
| `w` | 保存并退出 |
| `q` | 不保存退出 |

#### 分区类型代码

| 代码 | 类型 |
|------|------|
| `82` | Linux swap |
| `83` | Linux 标准 |
| `8e` | Linux LVM |

#### fstab 格式

```
设备        挂载点  类型   选项     dump  fsck
/dev/vdb2  swap    swap   defaults 0     0
```

### 验证

```bash
free -m  # 查看 swap 大小
```

---

## 23. 创建逻辑卷

### 题目要求

创建逻辑卷 `myvg/mylv`：50 个 PE（每个 PE 16MiB），ext3 格式化，挂载到 `/mnt/mydata`。

### 实际操作

```bash
# 1. 创建分区
fdisk /dev/vdb
# n → 分区号默认 → +1G → t → 分区号默认 → 8e → w

# 2. 创建卷组（指定 PE 大小）
vgcreate -s 16M myvg /dev/vdb3

# 3. 创建逻辑卷（50 个 PE）
lvcreate -l 50 -n mylv myvg

# 4. 格式化
mkfs.ext3 /dev/myvg/mylv

# 5. 挂载
mkdir /mnt/mydata
echo '/dev/myvg/mylv /mnt/mydata ext3 defaults 0 0' >> /etc/fstab
mount -a
```

### 扩展开的知识点

#### PE（Physical Extent）概念

- PE 是 LVM 的最小分配单元
- `-s 16M` 设置 PE 大小为 16MiB
- 逻辑卷大小 = PE 数量 × PE 大小
- 50 × 16MiB = 800MiB

#### lvcreate 参数

| 参数 | 含义 |
|------|------|
| `-L SIZE` | 按绝对大小创建 |
| `-l NUM` | 按 PE 数量创建 |
| `-n NAME` | 逻辑卷名称 |

### 验证

```bash
df -Th /mnt/mydata
```

---

## 24. 配置系统调优

### 题目要求

将系统调优配置设置为 tuned 推荐的配置。

### 实际操作

```bash
# 查看推荐配置
tuned-adm recommend

# 设置为推荐配置
tuned-adm profile virtual-guest
```

### 扩展开的知识点

#### tuned 命令

| 命令 | 作用 |
|------|------|
| `tuned-adm recommend` | 查看系统推荐的调优方案 |
| `tuned-adm profile NAME` | 设置调优方案 |
| `tuned-adm active` | 查看当前激活的方案 |
| `tuned-adm list` | 列出所有可用方案 |
| `tuned-adm off` | 关闭调优 |

### 验证

```bash
tuned-adm list | grep Current
# Current active profile: virtual-guest
```

---
