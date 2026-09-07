---
id: "kb-cloud-kubernetes-storage-deployment"
title: "Kubernetes 存储、发布与调度"
summary: "EmptyDir、Sidecar、滚动更新、镜像排障与调度策略。"
category: "云计算"
status: "published"
order: 19
parent: "kb-cloud-containers"
tags: ["kubernetes", "volume", "rollout", "scheduling"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# Kubernetes 存储、发布与调度

## Kubernetes 存储、发布与调度

### 15.13 EmptyDir Volume 与 Sidecar（边车）模式

#### 完整双容器示例
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-emptydir
spec:
  containers:
  - name: nginx
    image: aaronxudocker/myapp:v1.0
    ports:
    - containerPort: 80
    volumeMounts:
    - name: logs-volume
      mountPath: /var/log/nginx      # nginx 挂到日志目录
  - name: busybox
    image: aaronxudocker/tools:busybox
    command: ["/bin/sh","-c","tail -f /logs/access.log"]
    volumeMounts:
    - name: logs-volume
      mountPath: /logs               # busybox 挂到 /logs
  volumes:
  - name: logs-volume
    emptyDir: {}                     # Pod 级声明的空目录卷
```

#### YAML 字段含义对照
| 字段层级 | 写法 | 含义 |
|---------|------|------|
| `apiVersion: v1` | core 组 | 不带 `/v1xxx` 前缀 |
| `kind: Pod` | 资源类型 | 最小调度单位 |
| `metadata.name` | Pod 名字 | 同 namespace 内唯一 |
| `spec.containers[]` | 容器数组 | 本 Pod 含 2 个容器 |
| `spec.containers[].ports` | 端口声明 | `containerPort` 是声明性 |
| `spec.containers[].volumeMounts` | 容器内挂载点 | 挂哪个卷、挂哪里 |
| `spec.volumes` | Pod 级卷定义 | 整个 Pod 共享 |
| `spec.volumes[].emptyDir` | 空目录卷 | Pod 启动创建、删除时清理 |

#### 双容器共享外部目录的核心三步
**第一步：`volumes` 是 Pod 级资源，对所有容器可见**
写在 Pod 身上而非某个容器里，相当于"在 Pod 这个沙盒里申请了一块共享存储"，所有声明了同名 volume 的容器都能看到。

**第二步：每个容器通过 `volumeMounts` 把同一个卷挂到自己内部不同路径**
- nginx 把 `logs-volume` 挂到 `/var/log/nginx`（覆盖 nginx 默认日志目录，写入访问日志）
- busybox 把**同一个 `logs-volume`** 挂到 `/logs`（不同容器内路径）

挂载路径不同，但底层是同一份"块儿"。

**第三步：共享生效 = 同一份文件 = 实时同步**
`/var/log/nginx/access.log`（nginx 视角） == `/logs/access.log`（busybox 视角）

nginx 写一行 → busybox 的 `tail -f` 立刻就能看到这行。

#### 数据流图
```
┌────────────── Pod: volume-emptydir ──────────────┐
│                                                    │
│   ┌── logs-volume (emptyDir 共享存储) ──┐         │
│   │   access.log  ←── nginx 写入          │         │
│   │   error.log                            │         │
│   └─────────────────────────────────────┘         │
│       ▲                              ▲              │
│       │ 挂到 /var/log/nginx          │ 挂到 /logs   │
│   ┌────────┐                    ┌──────────┐         │
│   │ nginx  │   ─── 共享卷 ──→   │ busybox  │         │
│   │ 容器   │   同一份文件       │ tail -f  │         │
│   └────────┘                    └──────────┘         │
└────────────────────────────────────────────────────┘
```

#### 这个模式叫 Sidecar（边车模式）
| 角色 | 容器 | 职责 |
|------|------|------|
| 主容器 | nginx | 处理业务请求、写日志 |
| 边车容器 | busybox | 实时消费/转发日志 |

核心思想：**一个容器产生数据，另一个容器消费/加工/转发，通过共享 volume 解耦**。

生产环境 busybox 通常换成：
- `fluentd` / `filebeat` → 采集日志推 ELK
- `promtail` → 采集日志推 Loki
- 自定义 agent → 上报监控埋点
- `istio-proxy` → Service Mesh 边车代理流量

#### EmptyDir 易踩坑清单
1. **生命周期 = Pod 生命周期**：Pod 一删数据清空；持久化必须用 `hostPath` / `PV` / `PVC`
2. **挂载会"遮蔽"容器原有目录**：nginx 把卷挂到 `/var/log/nginx` 后，原有文件被藏（不是删，umount 后可见）
3. **多容器共享 = 要考虑读写冲突**：两边同时操作同份文件可能锁竞争/读写不一致
4. **不跨节点**：和 `hostPath` 不同，`emptyDir` 严格在 Pod 内共享；跨 Pod 共享得用 PV
5. **默认存在节点本地磁盘**：节点挂了数据丢；可指定 `medium: Memory` 走 tmpfs（飞快但吃内存，不算入容器内存 limit）
6. **必须先在 `volumes` 里定义，容器才能挂**：先有卷声明再有容器挂载
7. **挂载路径建议用绝对路径**：相对路径在不同镜像下行为不一致

---

### 15.14 K8s Pod 启动报错：BusyBox/瘦身镜像找不到 `/bin/bash`

#### 报错信息
```
Error: failed to start container "busybox": ...
OCI runtime create failed: runc create failed: unable to start container process:
error during container init: exec: "/bin/bash": stat /bin/bash: no such file or directory
Back-off restarting failed container busybox
```

#### 根本原因
- **BusyBox / Alpine 镜像默认 shell 是 `ash`**（路径 `/bin/sh`），**镜像内没有 `/bin/bash`**
- Pod spec 里把入口写成了 `/bin/bash`（常见错配，照搬 Debian/Ubuntu/CentOS 习惯）
- runtime 去找 `/bin/bash` → 该文件在 BusyBox 镜像里不存在 → 启动失败
- kubelet 检测到失败 → 指数退避重试（BackOff），典型表现 `x5 over 4m`

#### BusyBox 镜像特点
1. **大小约 1~2 MB**，只保留最常用的 Unix 工具
2. **默认 shell 是 `ash`**，不是 bash，`/bin/sh` 才是入口
3. **不包含** bash、glibc、GNU coreutils，很多 Debian/Ubuntu 脚本直接搬过去会报缺命令
4. **alpine:xxx 镜像**也用 `ash`（基于 busybox + musl libc），同一套坑

#### 解决方案（三种写法任选）
```yaml
# ✅ 写法 1：改用 /bin/sh（最常见）
- name: busybox
  image: aaronxudocker/tools:busybox
  command: ["/bin/sh", "-c", "echo hello > /cache/index.html; sleep 3600"]

# ✅ 写法 2：K8s 1.27+ 用 shell 字段声明
spec:
  containers:
  - name: busybox
    image: aaronxudocker/tools:busybox
    shell: /bin/sh              # 1.27+ 才支持，需检查版本
    command: ["echo hello > /cache/index.html; sleep 3600"]

# ✅ 写法 3：留空入口，让镜像自带 ENTRYPOINT 兜底
- name: busybox
  image: aaronxudocker/tools:busybox
  # 不写 command，让镜像 Dockerfile 的 ENTRYPOINT/CMD 生效
```

#### 镜像家族与 shell 选型对照
| 镜像家族 | 默认 shell | Pod spec 里应该写 |
|---------|-----------|-----------------|
| busybox | ash | `/bin/sh` |
| alpine | ash | `/bin/sh` |
| debian / ubuntu | bash | `/bin/bash` |
| centos / rhel | bash | `/bin/bash` |

#### 排查标准动作
1. **看 events**：`kubectl describe pod <name>` → 找 Failed 行的 `exec: "xxx"` 信息
2. **验证镜像里到底有没有这二进制**：
   ```bash
   docker run --rm --entrypoint ls aaronxudocker/tools:busybox /bin/
   # 或
   docker run --rm aaronxudocker/tools:busybox which sh
   ```
3. **临时进入容器测试**：用 `kubectl run --rm -it --image=busybox test -- sh` 跑一下
4. **改 yaml 重 apply**：`command` 改为 `/bin/sh -c "..."`，或换基础镜像（busybox → alpine / debian-slim）

⚠️ **跟 §3.2.1 的区别**：§3.2.1 讲的是运行中容器用 `docker exec` 进不去（瘦身镜像 exec 失效）；本节讲的是 Pod 启动阶段 runtime exec entrypoint 找不到，是不同场景不同排错思路。

---

### 15.15 Deployment 滚动更新：kubectl patch + annotations 触发 + 替换粒度

#### 命令本身
```bash
kubectl patch deployment hotupdate-deploy \
  --patch '{"spec": {"template": {"metadata": {"annotations": {"version/config": "v1.0" }}}}}'
```

| 部分 | 含义 |
|------|------|
| `kubectl patch` | 补丁式更新，只改指定路径字段 |
| `deployment hotupdate-deploy` | 目标资源 |
| `--patch '{...}'` | 默认 strategic merge patch（智能合并，不删其他字段） |
| JSON 路径 | 4 层嵌套：`spec → template → metadata → annotations → version/config` |

合并后效果（不会删除同级别其他 annotation，比如 `kubectl.kubernetes.io/last-applied-configuration`）：
```yaml
spec:
  template:
    metadata:
      annotations:
        kubectl.kubernetes.io/last-applied-configuration: ...
        version/config: "v1.0"   # 新增
```

#### 为什么改 annotations 能触发滚动更新
核心机制：**Deployment controller 对 `spec.template` 整体计算 hash**，hash 变 → 创建新 ReplicaSet → 滚动更新。

被纳入 hash 的字段：
- `spec.template.spec.containers`（image / env / resources / command ...）
- `spec.template.spec.volumes` / `volumeMounts`
- `spec.template.metadata.labels`
- `spec.template.metadata.annotations` ✅ 是的，annotations 也算
- `spec.template.spec.restartPolicy` ...

改 `spec.template` 下任何字段都会触发 hash 变化 → 触发滚动更新。

#### 「用 annotation 强制触发滚动更新」的实战妙用
**痛点场景**：
- ConfigMap / Secret 配置更新了
- 但 Pod template 里引用方式没变（`envFrom configMapRef name` 写死）
- Deployment controller 算 hash 没变 → **不会自动重建 Pod** → 老 Pod 跑老配置

**解决思路**：在 `spec.template.metadata.annotations` 里维护版本号字段，每次想"刷新"所有 Pod 时手动 bump：
```yaml
metadata:
  annotations:
    version/config: "1.0"   # ConfigMap 改了 bump
    version/secret: "3"     # Secret 改了 bump
```
```bash
# ConfigMap 更新后手动触发：
kubectl patch deployment hotupdate-deploy \
  --patch '{"spec":{"template":{"metadata":{"annotations":{"version/config":"1.1"}}}}}'
```
即使 Deployment 自身配置一字不变，也照滚一遍，让所有 Pod 重新拉取最新 ConfigMap。

#### 滚动更新完整流程
```
kubectl patch
    ↓
Deployment Controller 检测 spec.template hash 变化
    ↓
创建 newRS（初始 replicas=0），保留 oldRS
    ↓
按 maxSurge / maxUnavailable 节奏交替伸缩：
    t1: oldRS=4, newRS=0
    t2: oldRS=3, newRS=1   (maxSurge=1，每轮 newRS +1 / oldRS -1)
    t3: oldRS=2, newRS=2
    t4: oldRS=1, newRS=3
    t5: oldRS=0, newRS=4   （完成）
    ↓
oldRS 缩到 0 但**不删除**，方便回滚（kubectl rollout undo）
```
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%         # 最多比期望多几副本（如 4 副本 → 允许 5）
      maxUnavailable: 25%   # 最多几副本不可用（4 副本 → 允许 1 挂）
```

#### 替换粒度：Pod 级（不是容器级，不是节点级）
**Q：同一个 yaml 里跑的节点，改了一个容器配置，滚动更新能用到所有容器上吗？**

A：80% 对，中间有两个修正点：

✅ **理解对的点**：
- 改 yaml 后 apply，整个 Deployment 下所有 Pod 副本都会换成新版本
- 最终状态 = 全部一致的新 Pod，不是「老的留老的、新的换新的」

❎ **需要修正的点**：
1. **「节点」说法偏差**：Deployment 管的是 Pod 副本（ReplicaSet 下的 N 个 Pod），不是节点。一个节点可以跨多个 Deployment 跑多个 Pod
2. **「只改某个容器」被重新加载**：不能只替换 Pod 里某一个容器。Pod 整体哈希变了 → 整个 Pod 重建，所有容器都跟着重启（哪怕没改那个容器）

| 概念 | 替换粒度 |
|------|---------|
| Deployment 滚动更新 | **Pod 级**（一个 Pod 一个 Pod 换） |
| Pod 内多容器共享资源 | 不能只换单个容器 |
| 副本数滚动 | 按 `spec.replicas` 而不是节点数 |

⚠️ **实战例子**（双容器 Deployment）：
```yaml
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nginx
        image: myapp:v1.0 → v2.0    # 改了
      - name: busybox                # 没改
        image: tools:busybox
```
apply 之后结果：
- ✅ 3 个 Pod 全部重建（nginx 升到 v2.0）
- ✅ busybox 也跟着重启了（Pod 是整体）
- ❎ 不是「只换 nginx、保留 busybox」
- ❎ 不是「只换第 1 个 Pod 保留其他 2 个」

#### 三个改动 vs 替换范围
| 改的东西 | 触发滚动？ | 结果 |
|---------|----------|------|
| image tag v1 → v2 | ✅ 是 | 3 个 Pod 都升到 v2 |
| 加个环境变量 | ✅ 是 | 3 个 Pod 都重启加载新 env |
| 改 annotations 版本号 | ✅ 是 | 3 个 Pod 都重启 |
| **改 ConfigMap 内容（但 Pod template 引用方式没变）** | ❌ 否 | **Pod 不会自动重建！老配置一直跑！** |

最后那条是实战中特别容易踩的坑。

#### kubectl patch 的 3 种策略
| 类型 | 适用场景 | 备注 |
|------|---------|------|
| **strategic merge patch**（默认） | 90% 场景 | 智能合并，保留未指定字段 |
| json merge patch（RFC 7396） | 简单合并 | 嵌套对象会被新值完全替换 |
| json patch（RFC 6902） | 数组级精细操作 | `op: replace/add/remove`，需数组 path |

实战**几乎只用默认的 strategic merge patch**。

#### 易踩坑清单
1. **annotation key 含 `/` 不报错**：K8s annotation key 允许带 `/`，用作命名空间分类（`version/config` 是常见用法）
2. **`kubernetes.io/` 前缀禁止用户使用**：保留前缀，会拒绝创建
3. **同值改两次不触发**：必须 v1.0 → v2.0 这种值变化才会触发 hash 变化
4. **`kubectl rollout status deployment/<name>`** 比观察 Pod 状态更直观，是排查进度标准命令
5. **回滚用 `kubectl rollout undo deployment/<name>`**：回到上一个 Revision，因为旧 ReplicaSet 没被删（K8s 默认保留历史 RS）
6. **滚动过程 Pod 数可能临时超出 replicas**：因为有 maxSurge；批量调度也可能临时不足（maxUnavailable 允许少量挂）
7. **annotation 触发的"虚拟更新"会真的起停一遍 Pod**：哪怕业务逻辑没变，所有 Pod 都会被替换一次（生产环境注意流量抖动）

---

### 15.16 Pod 调度策略：反亲和性 + Node 污点与 Toleration

#### A. Pod 反亲和性 podAntiAffinity

##### 完整 YAML
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-podantiaffinity-required
spec:
  containers:
  - name: nginx
    image: aaronxudocker/myapp:v1.0
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: podenv
            operator: In
            values: ["pro"]
        topologyKey: kubernetes.io/hostname
```

##### 逐字段拆解
| 字段 | 含义 |
|------|------|
| `affinity` | 亲和性总开关 |
| `podAntiAffinity` | 类型：反亲和（vs `podAffinity` 是亲和） |
| `requiredDuringSchedulingIgnoredDuringExecution` | 硬限制（必须满足，否则 Pending） |
| `labelSelector.matchExpressions` | 要避开的 Pod 标签匹配条件 |
| `key / operator / values` | 匹配表达式：label 筛选条件 |
| `topologyKey` | 拓扑域（节点/AZ/region） |

##### 一句话讲透
**调度本 Pod 时，scheduler 去找全集群带 `podenv=pro` 标签的 Pod，本 Pod 不能调度到已经存在这种 Pod 的 node 上。**

##### required vs preferred
| 写法 | 含义 | 失败结果 |
|------|------|---------|
| `requiredDuringSchedulingIgnoredDuringExecution` | 硬限制 | Pod Pending，永远调度不上 |
| `preferredDuringSchedulingIgnoredDuringExecution` | 软限制 | 违反也调度，加权分扣 |

##### `IgnoredDuringExecution` 代表什么
- 「**调度时考虑，运行时不强制**」
- Pod 一旦调度上去，后续反亲和规则变化不会触发驱逐
- 后续调度才遵守新规则

##### topologyKey 决定颗粒度
| topologyKey | 颗粒度 |
|-------------|--------|
| `kubernetes.io/hostname` | 节点（同主机名不贴） |
| `topology.kubernetes.io/zone` | 可用区 |
| `topology.kubernetes.io/region` | 区域 |

##### 调度可视图
```
集群 3 个 node，2 个 podenv=pro Pod：
┌───────────────────────┐
│ node1: [nginx-pro ]    │
│ node2: [nginx-pro ]    │
│ node3: []              │
│                        │
│ 第 3 个 nginx-pro Pod 被强制调度到 node3
└───────────────────────┘
```

##### 反亲和 vs 亲和用途
| 类型 | 效果 | 经典场景 |
|------|------|---------|
| `podAffinity` | 跟带 label 的 Pod 同拓扑域 | DB cache 跟 DB 同 node |
| `podAntiAffinity` | 跟带 label 的 Pod 不同拓扑域 | 主从不同 node / ingress 散布多个 node |

##### 易踩坑
1. **节点数不够会 Pending**：3 个 podenv=pro 分散要 3 个 node，集群只有 2 个 → 第 3 个永远 Pending
   - 诊断：`kubectl describe pod` 看 `0/3 nodes are available: 3 node(s) didn't match pod anti-affinity rules`
2. **不命中的 Pod 不参与计算**：label selector 命不中的 Pod scheduler 不看
3. **影响的是同拓扑域的「别的 Pod」，不是自己**：本 Pod 自己也带 podenv=pro 也行，约束的是避开别的同类 Pod
4. **`IgnoredDuringExecution` 不能省**：跟 required 配对的全名就是这个，缩写不合法
5. **`matchExpressions` 是数组**：多条表达式是 AND 关系
   ```yaml
   matchExpressions:
   - key: podenv
     operator: In
     values: ["pro"]
   - key: app
     operator: In
     values: ["nginx"]
   # 表示：app=nginx AND podenv=pro
   ```
6. **Pod 反亲和是调度阶段控制**：不会让已运行的 Pod 被驱逐
7. **多 namespace 下的 Pod 也起作用**：label selector 跨 namespace 查（指定 namespaces 除外）

---

#### B. Node 污点（Taints）+ Pod Toleration

##### 4 种查看方法
```bash
# ① describe 直眼看 Taints: 行
kubectl describe node node01 | grep -A 5 "Taints:"

# ② YAML 完整信息
kubectl get node node01 -o yaml | grep -A 10 taints

# ③ JSONPath 直接抠字段
kubectl get node node01 -o jsonpath='{.spec.taints}' && echo

# ④ 全部节点 + 自定义列（最常用）
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```
输出示例：
```
NAME     TAINTS
master   [map[effect:NoSchedule key:node-role.kubernetes.io/master timeAdded:...]]
node01   <none>
node02   <none>
```
只要看到 `<none>` 或空数组 = **无污点**，所有 Pod 都能调度。

##### Taint 字段格式
```yaml
spec:
  taints:
  - key: dedicated
    value: gpu
    effect: NoSchedule
    timeAdded: "2026-..."  # 系统自动添加，系统 taint 才有
```
格式：`key=value:effect`（key 可不带 value，如 `node-role.kubernetes.io/master:NoSchedule`）

##### 三种 effect 对比
| effect | 效果 |
|--------|------|
| `NoSchedule` | **禁止新 Pod 调度**，已跑 Pod 不动 |
| `PreferNoSchedule` | 软限制，尽量不调度；没节点也会调 |
| `NoExecute` | **禁止新调度 + 驱逐已在运行的 Pod**（最狠） |

##### 常见系统自带 taint
```bash
node-role.kubernetes.io/master:NoSchedule              # master 节点默认
node.kubernetes.io/unreachable:NoExecute                # node 失联时自动
node.kubernetes.io/not-ready:NoExecute                  # NotReady
node.kubernetes.io/memory-pressure:NoSchedule           # 内存压力
node.kubernetes.io/disk-pressure:NoSchedule             # 磁盘压力
node.kubernetes.io/pid-pressure:NoSchedule              # PID 压力
node.kubernetes.io/network-unavailable:NoSchedule       # 网络未就绪
```

##### 设置 / 去掉 taint
```bash
# 设置
kubectl taint nodes node01 dedicated=gpu:NoSchedule
# 去掉（加后缀 -）
kubectl taint nodes node01 dedicated=gpu:NoSchedule-
```

##### Taint + Toleration 原理（单向门 + 钥匙）
**Node 端**（抹黄油、贴反门）：
```bash
kubectl taint nodes node01 dedicated=gpu:NoSchedule
```
**Pod 端**（带钥匙 → 才让进）：
```yaml
spec:
  tolerations:
  - key: dedicated
    operator: Equal
    value: gpu
    effect: NoSchedule
  # tolerationSeconds: 3600    # NoExecute 才用，最多忍多久驱逐
```
调度逻辑：**Node 的所有 taint 都被 Pod 的 tolerations 完全覆盖，Pod 才被允许调上去**。

实战：GPU 节点打 `gpu=true:NoSchedule`，普通 Pod 没 toleration 自动跳过；只有 ML 任务 Pod 带 toleration 才能用。

##### 易踩坑清单
1. **master 节点有隐性污点**：`kubectl get nodes` 看 master 是 `<none>`，其实**系统默认加了** `node-role.kubernetes.io/master:NoSchedule`，必须 describe 才看全
2. **NoExecute 立刻驱逐**：不加 toleration 直接 NoExecute，在跑 Pod 立马被踢 → 服务中断
3. **tolerationSeconds 只对 NoExecute 有效**：其他两种 effect 忽略这字段
4. **toleration 不能 Partial 匹配**：写 `key=A` 不等于容忍 `key=A,value=B`；要么 `Equal` + value 写全，要么用 `Exists` 只匹配 key
5. **toleration 是「允许」不是「调度」**：带 toleration ≠ 一定被调上去，只是「不会因为这个 taint 拒绝」
6. **`effect` 不写会报错**：系统识别不到这个 taint
7. **NoSchedule 不驱逐老 Pod**：只挡新 Pod；要驱逐用 NoExecute
8. **可以同时加多种 taint**：一个 Node 可多个 taint，调度时 Pod 需对每个 taint 都有对应 toleration

<!-- KB:INSERT:kubernetes-deployment-additions -->
