---
id: "kb-linux-nmcli-networking"
title: "Rocky Linux nmcli 网络配置"
summary: "NetworkManager、静态地址与连接排障。"
category: "操作系统"
status: "published"
order: 19
parent: "kb-linux-operations"
tags: ["nmcli", "networkmanager", "rocky-linux"]
updatedAt: "2026-08-26"
source: "Migrated from docs/linux.md"
applicableVersion: "rolling"
---

# Rocky Linux nmcli 网络配置

## 24. Rocky Linux 配置网卡 IP（nmcli / NetworkManager）

来源：2026-07-18 交换区

Rocky Linux（RHEL 系）推荐用 **NetworkManager** 体系，三种方式：`nmcli`（命令行，生产推荐）、`nmtui`（图形菜单）、直接改配置文件。

### 核心概念：device vs connection

- **device（网卡设备）**：物理/虚拟网卡本身，如 `ens160`
- **connection（连接配置）**：网卡的配置档案，可与设备不同名
- `nmcli connection` 操作的是 connection，`nmcli device` 操作的是设备

### 查网卡和连接

```bash
nmcli device status                  # 查看所有网卡设备
nmcli connection show                # 查看所有连接
nmcli connection show "ens160"       # 看 ens160 的现有配置
```

### nmcli 配置静态 IP（推荐）

```bash
# 1. 设置 IP + 子网掩码（CIDR 格式）
nmcli connection modify "ens160" ipv4.addresses 192.168.1.100/24

# 2. 设置网关
nmcli connection modify "ens160" ipv4.gateway 192.168.1.1

# 3. 设置 DNS（多个用空格分隔）
nmcli connection modify "ens160" ipv4.dns "223.5.5.5 8.8.8.8"

# 4. 把 ipv4 改为手动（manual），默认是 auto（DHCP）
nmcli connection modify "ens160" ipv4.method manual

# 5. 关闭 IPv6（可选）
nmcli connection modify "ens160" ipv6.method disabled

# 6. 让配置生效（推荐 up，不是重启网络）
nmcli connection up "ens160"
```

- `modify` 只写入配置文件，不立即生效
- `up` 才真正应用配置
- 改完**不需要** `systemctl restart NetworkManager`

### 重新读取配置（不改变连接状态）

```bash
nmcli connection reload "ens160"
```

### 配置文件位置

`nmcli modify` 会写到下面两个位置之一：

- **新版（Rocky 9+ 默认）**：`/etc/NetworkManager/system-connections/ens160.nmconnection`
- **传统（兼容）**：`/etc/sysconfig/network-scripts/ifcfg-ens160`

#### keyfile 格式示例

```ini
[connection]
id=ens160
type=ethernet
interface-name=ens160

[ipv4]
method=manual
address1=192.168.1.100/24,192.168.1.1
dns=223.5.5.5;8.8.8.8

[ipv6]
method=disable
```

> 也可以直接 `vi` 改这个文件，保存后跑 `nmcli connection reload` + `nmcli connection up "ens160"`。

### nmtui（图形菜单）

```bash
nmtui
```

方向键选 "Edit a connection" → 选 ens160 → 改 IP/网关/DNS → OK → 退出。

适合不熟 `nmcli` 的场景，批量配置还是得用 `nmcli`。

### 临时 IP（重启失效，不写文件）

```bash
ip addr add 192.168.1.200/24 dev ens160
ip route add default via 192.168.1.1
ip link set ens160 up
```

调试/排错时用，**重启就没了**。

### 验证

```bash
ip addr show ens160                       # 看 IP
ip route                                  # 看网关
nmcli -t -f IP4 connection show "ens160"  # 看 NM 里的 IP 配置
ping 192.168.1.1                          # 测网关
ping 223.5.5.5                            # 测外网
cat /etc/resolv.conf                      # 看 DNS
```

---

<!-- KB:INSERT:nmcli-networking-additions -->
