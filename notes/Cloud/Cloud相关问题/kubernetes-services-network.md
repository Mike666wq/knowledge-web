---
id: "kb-cloud-kubernetes-services-network"
title: "Kubernetes Service 与网络"
summary: "Job、Namespace、Service、DNS、Pod 网络和四种服务类型。"
category: "云计算"
status: "published"
order: 18
parent: "kb-cloud-containers"
tags: ["kubernetes", "job", "namespace", "service", "dns", "network"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# Kubernetes Service 与网络

## Kubernetes Service 与网络

### 15.7 Service 工作机制与"Myapp Version 1.0"来源

#### 实验现象
```bash
$ kubectl get deploy
myapp-deploy  3/3  3  3  22s

$ kubectl get service
myapp  ClusterIP  10.3.47.41  <none>  80/TCP  23h

$ while true; do curl 10.3.47.41; sleep 1; done
Myapp Version 1.0
Myapp Version 1.0
...
```

#### ① 为啥改 label 就能跟 Service 关联
Service 只通过 **selector 找 Pod**，不管 RS。完整链路：

```
Service (selector: app=myapp)
  ↓ Endpoints Controller watch
Endpoints 对象（自动维护 Pod IP 列表）
  ↓ kube-proxy 持续 watch
配置 iptables / IPVS 规则
  ↓ 访问 ClusterIP
DNAT 到真实 Pod IP
```

**详细步骤**：
1. **Endpoints Controller**（kube-controller-manager 组件）持续 watch Service selector 和 Pod labels
2. 把匹配的 Pod IP 写入 Endpoints（v1.21+ 默认 EndpointSlice）
3. **kube-proxy**（每 Node 跑一个）监听 Endpoints 变化
4. 生成 iptables 规则（轮询负载均衡）
5. 访问 ClusterIP 时 iptables DNAT 到 Pod IP

```bash
$ kubectl describe svc myapp
Selector:          app=myapp          ← Service 在找这个 label
IP:                10.3.47.41
Endpoints:         10.244.1.5:80,10.244.2.3:80,10.244.3.7:80   ← 自动维护的 Pod 列表
```

#### ② Service ClusterIP 是"虚拟 IP"
- ClusterIP（10.3.47.41）**不绑任何网卡**——纯虚拟
- `ping 10.3.47.41` 不通（ICMP 包没匹配 iptables 规则被丢）
- `curl 10.3.47.41` 能通（TCP 包被 iptables 抢在前面 DNAT）
- iptables 在 OUTPUT 阶段拦截（不是 PREROUTING，因为没路由）

#### ③ "Myapp Version 1.0" 是哪来的
**应用代码自己返回的字符串，跟 K8s 完全无关**。

镜像 `aaronxudocker/myapp:v1.0` 里的 Web 应用代码大概类似：
```python
@app.route("/")
def hello():
    return "Myapp Version 1.0"   # 应用代码里硬编码
```

**这就是 K8s 滚动更新的经典演示**：换 `aaronxudocker/myapp:v2.0`，curl 返回 "Myapp Version 2.0"，逐步替换 Pod。

#### ④ "Myapp" 名字到底是哪层的
**4 个独立的"Myapp"，互相之间没关联**：

| 出现位置 | 是什么 | 谁起的 |
|---|---|---|
| 镜像名 `aaronxudocker/myapp:v1.0` | Docker Hub 仓库名 | 镜像作者 |
| Service 名 `myapp` | K8s 资源名 | 你 |
| Pod label `app=myapp` | K8s label 值 | 你 |
| 返回字符串 "Myapp Version 1.0" | 应用代码硬编码 | 镜像作者 |

**K8s 永远不会把 Service 名、label 塞进 HTTP 响应 body**。4 个"Myapp"只是恰好同名让你产生错觉。

#### ⑤ 这套机制的"自愈"特性
Pod IP 是动态的，Service 自动跟上：
```
Pod 重启 → IP 变了 → Endpoints Controller 检测 → 更新 Endpoints
  → kube-proxy 重新生成 iptables → 客户端无感知继续访问
```
这就是 Service 的核心价值：**入口稳定，后端可换**。

#### ⑥ 验证方法
```bash
kubectl get endpoints myapp                # 看自动维护的 Pod IP 列表
kubectl describe svc myapp                 # 看 selector 和 endpoints 详情
kubectl get pod -o wide -l app=myapp       # 看 Pod 实际 IP 和 label

# 直接 curl 某个 Pod IP（不走 Service），验证返回内容一致
curl 10.244.1.5    # 同样返回 "Myapp Version 1.0"
# 说明返回内容确实来自 Pod 内应用，跟 Service 无关
```

---

> 💡 **一句话：** K8s 的整套 Service 机制 = selector 找 Pod → 写 Endpoints → kube-proxy 生成 iptables → DNAT 到真实 Pod。"Myapp Version 1.0" 是**应用代码硬编码字符串**，跟 Service 名、label 名完全无关。

---

### 15.8 K8s Job 完整指南（completions / parallelism / backoffLimit）

#### 场景
配置 `completions=10, parallelism=5, restartPolicy=Never`，镜像随机返回退出码。
现象：Pod 数远超 completions（看到 15 个 Pod），Error/Completed 混杂，COMPLETIONS 卡在 8/10 跑不动。

#### YAML 关键字段
```yaml
spec:
  completions: 10          # 目标成功 Pod 数
  parallelism: 5           # 并行上限
  backoffLimit: 6          # ⚠️ 默认 6，累计失败 Pod ≥6 就 Failed
  activeDeadlineSeconds:  # 整体超时（建议显式设置）
  template:
    metadata:
      name: rand           # ⚠️ 反模式：pod template name 跟 Job 同名，应删掉
    spec:
      restartPolicy: Never # 失败 Pod 不原地重启，由 Job Controller 补新 Pod
```

#### Job Controller 核心循环
```
if .status.successful < completions  且  活跃 Pod < parallelism:
    立即创建新 Pod 填补
```
- 失败的 Pod **也算占过并行槽位**，所以总 Pod 数 > completions
- Completions 只数退出码=0 的 Pod
- Error 之后紧跟 Pending → ContainerCreating 不是延迟，是槽位释放后立即被新 Pod 抢占

#### restartPolicy 对比
| Policy | 行为 | 适用场景 |
|---|---|---|
| **Never** | 失败不重启，Job Controller 创建新 Pod 补 | 跑一次性离线任务 |
| **OnFailure** | ✅ 容器原地重启，不消耗并行名额 | 镜像可能偶发失败，推荐 |
| Always | 不允许（Job 强制只能是 Never 或 OnFailure） | — |

#### backoffLimit vs backoff period（易混两个概念）
| 概念 | 作用 | 默认值 |
|---|---|---|
| `spec.backoffLimit` | 累计失败 Pod 上限，达到就判 Job Failed | **6** |
| **backoff period** | 失败后等多久再创建新 Pod（指数退避） | 初始 10s 翻倍 |

**数法**：每个退出码非 0 的 Pod 直接 +1 到 `.status.failed`，所以 N 个 Error Pod = `.status.failed` = N。
判定：`.status.failed >= backoffLimit` → Job 标 Failed，**不再创建新 Pod**。

**"卡住"的真实原因（两个机制叠加）：**
1. 失败后 backoff period 指数增长（10s → 20s → 40s → 80s...），看起来像卡住
2. backoffLimit 累计达到 → Job 判 Failed → 停止创建 Pod，COMPLETIONS 永远卡在 <10

#### 验证 backoffLimit 是否触发
```bash
# 看 Job 详细状态（Conditions 和 Events）
kubectl describe job rand
# 期望看到:
#   Conditions:
#     Type: Failed
#     Status: True
#     Reason: BackoffLimitExceeded

# 看原始 status 字段
kubectl get job rand -o jsonpath='{.status}' | jq .

# 看 Pod 数量是否稳定（Failed 后不再涨）
kubectl get pods -l job-name=rand --no-headers | wc -l
```

**为什么 `get job` 还显示 8/10 而不是 Failed？**
- Job Controller 是**周期性 reconcile**（默认几秒~十几秒）
- 8/10 那一刻可能是 reconcile 间隙，再等几秒 get 就是 Failed: True
- `kubectl describe` 比 `kubectl get` 更早反映真实状态

#### 改进模板
```yaml
spec:
  backoffLimit: 20              # 提高容错
  activeDeadlineSeconds: 300    # 整体 5 分钟超时防死循环
  template:
    spec:
      restartPolicy: OnFailure  # ✅ 推荐：容器原地重试不消耗并行槽位
      containers:
      - image: <image>
```
⚠️ 删掉 `template.metadata.name`（反模式，Job Controller 会自动生成 `<job-name>-<random>`）

#### 核心要点
- `backoffLimit` 数的是**退出码非 0 的 Failed Pod 数**，跟 `restartPolicy: Never` 直接挂钩
- `Never` 下每个 Failed Pod 必 +1；`OnFailure` 下失败由容器自己重试，不增加 `.status.failed`
- 想"重试到成功" → 用 `OnFailure` + 高 `backoffLimit` + `activeDeadlineSeconds` 三件套

**一句话速记：** `restartPolicy: Never` + 随机退出镜像 → Job 疯狂补 Pod 凑数，但 `backoffLimit: 6` 会让 Job 半路 Failed。推荐 `OnFailure` + 提高 backoffLimit + 加 activeDeadlineSeconds。

---

### 15.9 K8s Namespace 机制

#### 直接答案
`-n` = `--namespace` 缩写，指定查哪个 namespace。K8s 用 namespace 把资源切成逻辑组（类似虚拟集群），做隔离和权限控制。

- 不加 `-n` → 查 `default` namespace
- `-n kube-system` → 查 kube-system namespace  
- `-A` = `--all-namespaces` → 查全部

#### 4 个内置 namespace
| Namespace | 作用 |
|---|---|
| `default` | 默认，用户资源默认落这 |
| `kube-system` | K8s 系统组件（calico、kube-proxy、coredns...） |
| `kube-public` | 公开可读，放集群公共信息 |
| `kube-node-lease` | 节点心跳（1.14+），节点健康检测 |

#### 常用 namespace 命令
```bash
kubectl get ns                          # 列所有 namespace
kubectl get pod -A                      # ✅ 推荐：看所有 namespace 的 Pod
kubectl get ds -A                       # 查所有 namespace 的 DaemonSet

kubectl config set-context --current --namespace=kube-system   # 切换默认 ns
kubectl create ns my-ns                  # 创建 namespace
kubectl apply -f app.yaml -n my-ns        # 指定 ns 部署
```

#### YAML 里指定 namespace
```yaml
metadata:
  name: my-daemonset
  namespace: kube-system    # 不写默认 default
spec:
  ...
```

**一句话速记：** `-n` 指定 namespace，不写默认 `default`；系统组件住 `kube-system`，用户资源默认 `default`；想一次看全用 `-A`。

---

### 15.10 K8s Headless Service 详解（无 VIP，DNS 直接返 Pod IP）

#### Headless vs 普通 Service
| 维度 | 普通 Service | Headless Service |
|---|---|---|
| `clusterIP` | 有（自动分配 VIP） | **None** |
| DNS 解析 | 单条 A 记录 → ClusterIP | 多条 A 记录 → 每个 Pod IP |
| 负载均衡 | K8s 自动（iptables/IPVS） | **客户端自己做** |
| 配套 StatefulSet | ❌ | ✅（标准用法） |

**核心区别**：Headless 不要 VIP，直接把后端 Pod IP 全部暴露，客户端自己挑 Pod。

#### 三种典型用途
1. **StatefulSet 配套**：每个 Pod 要稳定 DNS（如 `mysql-0.mysql`, `mysql-1.mysql`）
2. **客户端自定义负载**：要看到所有后端，自己选（轮询/最少连接/权重）
3. **服务发现**：拿所有 Pod IP 做注册中心、监控、流量调度

#### K8s DNS 域名结构
```
<service-name>.<namespace>.svc.<cluster-domain>
                       ↑          ↑
                    svc 固定    默认 cluster.local
```
例：`service-headliness.default.svc.cluster.local`
拆解：service 名 . default ns . svc . cluster.local

#### Pod 内 /etc/resolv.conf 自动补全
```bash
nameserver 10.0.0.10                            # CoreDNS
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```
- `search` 列表：Pod 里 `ping service-headliness`（短域名）时自动按顺序补全
- `ndots:5`：域名中点数 < 5 才走 search 补全

#### 实际场景：StatefulSet 配 Headless Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  clusterIP: None                # ← Headless 关键配置
  selector:
    app: mysql
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql            # ← 关联 Headless Service
  replicas: 3
```
DNS 解析能力：
- `mysql.default.svc.cluster.local` → 3 个 Pod IP
- `mysql-0.mysql.default.svc.cluster.local` → **单个 Pod 的稳定 IP**（StatefulSet 核心）

#### 验证 Headless
```bash
dig @10.0.0.10 <service-name>.<ns>.svc.cluster.local
# Headless 返回 N 条 A 记录（N = Pod 数）
# 普通 Service 返回 1 条 A 记录（ClusterIP）
```

#### 通俗版讲解（公司打电话比喻）
| 模式 | 比喻 | DNS 解析结果 |
|---|---|---|
| 普通 Service | 公司有总机，K8s 帮你转接 | 1 个总机号（ClusterIP） |
| Headless Service | 没有总机，直接发通讯录 | N 个员工号（所有 Pod IP） |

**三个生活场景：**
1. **外卖平台挑厨师**：顾客想自己选评价最高的 → Headless（系统告诉 3 个厨师，自己选）
2. **StatefulSet 稳定卡号**：Pod 挂了重建名字不能变 → Headless（`mysql-0` 永远是 `mysql-0`）
3. **监控系统数机器**：要看所有后端 IP → Headless（一眼看到所有 Pod）

**一句话速记：** Headless = 关掉自动总机，给你员工名单自己打电话。

---

### 15.11 K8s Service 四种类型 DNS 对照 + ExternalName

#### K8s Service 4 种类型 DNS 对照
| 类型 | dig 返回 | 后端 |
|---|---|---|
| ClusterIP | `A <ClusterIP>` (1 条) | 集群内 Pod，K8s 代理 |
| **Headless** | `A <PodIP1> A <PodIP2> A <PodIP3>` (N 条) | 集群内 Pod，**无代理** |
| **ExternalName** | `CNAME <外部域名>` (链式解析) | 集群外服务，**无代理** |
| NodePort/LoadBalancer | `A <ClusterIP>` (1 条) | 集群内 Pod，K8s 代理 + 端口暴露 |

#### "无 ClusterIP" 的 3 种 Service
| 类型 | ClusterIP | selector | DNS 记录 |
|---|---|---|---|
| **Headless** | None | 有 | 多 A → Pod IP |
| **ExternalName** | 无 | **无** | CNAME → 外部域名 |
| 无 selector Service | 有/无 | 无 | A → 手动建 Endpoints |

#### Headless vs ExternalName 对比
| 维度 | Headless | ExternalName |
|---|---|---|
| 目的 | 暴露**集群内** Pod | 暴露**集群外**外部服务 |
| DNS 记录 | **A 记录**（Pod IP 列表） | **CNAME**（别名到外部域名） |
| 后端来源 | selector 选中的 Pod | externalName 指定的域名 |
| 典型场景 | StatefulSet、稳定标识 | 集群内访问外部 DB |

**共性：都是"无代理" Service**
- 都没 ClusterIP（`<none>`）
- 都不走 iptables/IPVS 代理
- 都是**纯 DNS 层面**的服务发现

#### ExternalName 详解
```yaml
spec:
  type: ExternalName
  externalName: www.baidu.com
```
dig 返回 CNAME 记录（不是 A 记录），链式解析到外部 IP：

```
service-externalname.default.svc.cluster.local
        ↓ CNAME
www.baidu.com
        ↓ CNAME
www.a.shifen.com
        ↓ A 记录
180.101.50.242
180.101.50.188
```

**ExternalName 特点：**
- 不分配 ClusterIP（`EXTERNAL-IP` 列显示外部域名）
- 不需要 selector（没有 Pod 关联）
- DNS 返回 **CNAME 记录**（域名别名）
- **不转发流量**，纯"域名翻译"

#### ExternalName 实战场景
**场景 1：集群内访问外部数据库（最常用）**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-mysql
  namespace: prod
spec:
  type: ExternalName
  externalName: db.prod.example.com
```
Pod 里 `mysql -h external-mysql.prod.svc.cluster.local` → 连 `db.prod.example.com`
**好处**：代码写死集群内域名，外部地址变了只改 Service。

**场景 2：环境切换（测试/生产）**
```yaml
# 测试环境
externalName: mock-db.testing.example.com
# 生产环境（同一份代码）
externalName: real-db.prod.example.com
```

**一句话速记：** Headless 用 A 记录把内网 Pod IP 列表给你；ExternalName 用 CNAME 把外网域名"翻译"给你；两者都跳过了 K8s 的流量代理。

---

### 15.12 Pod 网络基础：Pod IP + containerPort + 共享 netns

#### 核心结论
- **Pod IP** 是 K8s 给 Pod 分配的虚拟 IP（flannel 默认 `10.244.0.0/16`），节点物理网卡上**根本看不到**这个 IP，是 CNI 在节点上撑起的虚拟网络分配的
- **`containerPort` 只是声明性 metadata**，不等于端口映射，不会创建 iptables 规则
- **nginx 监听 `0.0.0.0:80` 天然就在 Pod IP:80 上**，这是物理层面绑在一起的结果，不是 K8s "映射"出来的

#### Pod IP 的实质（以 `10.244.140.106` 为例）
- 任何真实网卡上都看不到这个 IP，它是 CNI 虚拟网络分配的
- 安装 K8s 时声明 Pod 网络 CIDR（flannel 默认 `10.244.0.0/16`，calico 经常 `192.168.0.0/16` 等）
- 节点上会多出虚拟网络设备：`flannel.1`、`cni0`、`veth pair`...
- Pod 内的 eth0 在宿主机上对应一段 veth pair 的另一头
- 节点间通过 VXLAN / IPIP / host-gw 等隧道转发流量
- 集群内 Pod IP 全可达，集群外不可达（私有 IP + 无路由）

#### 为什么 80 端口会"到 Pod IP 上"：pause 容器 + 共享 netns

每个 Pod 启动时 kubelet 都先拉起一个**超小的 pause 容器**（啥也不干、占着一个 netns 不退出），业务容器全部 `--netns=pause` 加入到这个 netns：

```
┌──── Pod: volume-emptydir （共享一个 netns）──────────┐
│                                                          │
│   eth0  ←─── Pod IP 10.244.140.106 绑在这里（pause 持有）│
│   ↑                                                       │
│   │ 同一张网卡 / 同一张路由表 / 同一个 localhost         │
│   ├────────────────────┐                                  │
│   │                                       │                │
│ ┌───────┐                          ┌───────────┐          │
│ │ nginx  │                         │ busybox   │          │
│ │ :80    │ localhost               │ tail -f   │          │
│ │ (eth0) │                         │           │          │
│ └───────┘                          └───────────┘          │
└────────────────────────────────────────────────────────────┘
```

推论：
1. nginx 默认监听 `0.0.0.0:80` → 自动监听在 Pod IP（eth0）:80
2. busybox 因共享 netns，`curl localhost:80` 就能访问 nginx
3. Pod 内所有容器看到的 eth0 = localhost = 路由表 = iptables = Pod 级"网络面板"

#### `containerPort` 本质
```yaml
ports:
- containerPort: 80
```
- 纯声明性 metadata，**不打端口、不做 DNAT、不建 iptables**
- 唯一作用：给 Service / Ingress 等控制器做匹配依据、`kubectl get pod -o yaml` 展示意图、给 port-forward 智能提示参考
- **真正把流量引到 Pod 内的**是 Service / NodePort / Ingress / hostPort 等独立资源，跟 containerPort 是两码事

#### Pod 多种访问方式对照

| 访问方 | 命令 | 通否 | 原理 |
|--------|------|------|------|
| 同 Pod 内其他容器 | `curl localhost:80` | ✅ | 共享 netns |
| 集群内 Pod / 节点 | `curl http://10.244.140.106/` | ✅ | CNI 路由打通 |
| **集群外（笔记本）** | 直接访问 10.244.140.106 | ❌ | 私有 IP + 无外部路由 |

#### 让集群外能访问 nginx 的 4 种方案
```yaml
# 方案 1：Service（集群内 VIP，最基础）
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  selector: { ... }           # 匹配 Pod 的 label
  ports:
  - port: 80                  # Service 自身端口
    targetPort: 80            # 转发到 Pod 的 80

# 方案 2：NodePort（每个节点开 30000-32767 固定口）
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080           # 访问 <NodeIP>:30080 进来

# 方案 3：kubectl port-forward（调试用，不生产）
kubectl port-forward pod/volume-emptydir 8080:80
# 本机访问 http://localhost:8080

# 方案 4：Ingress（七层路由，需要先有 NodePort Service）
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata: { name: nginx-ing }
spec:
  rules:
  - host: nginx.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-svc
            port: { number: 80 }
```

#### Pod 像一台小虚拟机：端口是所有容器的并集
| 类比维度 | Pod | 普通虚拟机 |
|---------|-----|----------|
| IP | Pod IP（绑在 pause eth0 上） | 虚拟机 IP |
| 内部进程 | 多个容器（共享 netns） | 多个进程 |
| 监听端口 | 所有容器监听端口的**并集** | 所有进程监听端口的并集 |
| 端口冲突 | 不允许同端口两个容器（同 netns） | 不允许同端口两个进程 |
| 内部通信 | `localhost:<port>` | `localhost:<port>` |

⚠️ **端口冲突 = Pod 起不来**：共享 netns，同一端口只能被一个容器 listen。两个容器都 listen 80 → Pod 启动报错 `bind: address already in use` → CrashLoopBackOff。

**一句话速记：** Pod IP + 80 端口 = 天然可用，不是映射是共享；containerPort 是声明标签不是真映射；集群外访问必须经 Service / NodePort / Ingress 这层"搬运工"。

---
