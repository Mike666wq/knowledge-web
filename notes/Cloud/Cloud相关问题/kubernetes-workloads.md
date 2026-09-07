---
id: "kb-cloud-kubernetes-workloads"
title: "Kubernetes 工作负载与健康检查"
summary: "Pod 探针、生命周期、ReplicationController、Service 删除与 Deployment 标签。"
category: "云计算"
status: "published"
order: 17
parent: "kb-cloud-containers"
tags: ["kubernetes", "pod", "deployment", "probe"]
updatedAt: "2026-08-26"
source: "Migrated from docs/cloud.md"
applicableVersion: "rolling"
---

# Kubernetes 工作负载与健康检查

## 15. Kubernetes 核心概念与操作

### 15.1 Pod command 与三大探针（liveness/readiness/startup）

#### Pod command 是什么
严格说叫**入口命令**——容器启动时的执行命令由 `command`（覆盖镜像 ENTRYPOINT）+ `args`（覆盖镜像 CMD）共同决定：

| 写法 | 效果 |
|---|---|
| 只写 `command` | 镜像原 CMD 被丢弃 |
| `command` 和 `args` 都写 | 完全覆盖镜像原值 |
| 都不写 | 用镜像默认 ENTRYPOINT + CMD |

#### 演示 YAML
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-exec-pod
spec:
  containers:
    - name: liveness-exec-container
      image: aaronxudocker/tools:busybox
      imagePullPolicy: IfNotPresent
      command: ["/bin/sh", "-c", "touch /tmp/live; sleep 60; rm -rf /tmp/live; sleep 3600"]
      livenessProbe:
        exec:
          command: ["test", "-e", "/tmp/live"]
        initialDelaySeconds: 1
        periodSeconds: 3
      resources:
        limits:
          memory: "128Mi"
          cpu: "500m"
```

`command` 等价于：
```bash
/bin/sh -c "touch /tmp/live; sleep 60; rm -rf /tmp/live; sleep 3600"
```
1. 创建存活标记 `/tmp/live`
2. 撑 60 秒
3. 删除标记
4. 长睡（进程还在，但标记没了）

#### livenessProbe 行为
- `exec.command` 跑 `test -e /tmp/live`：文件存在返回 0（活），不存在返回非 0（死）
- `initialDelaySeconds: 1`：容器启动 1 秒后才开始探测
- `periodSeconds: 3`：每 3 秒探测一次

**完整循环**：
- 0s：容器启动 → 创建标记 → 探针通过
- 1s 起：每 3s 探测一次
- 60s 后：标记被删 → 探针失败累计到 `failureThreshold`（默认 3）次 → **K8s 重启容器**
- 重启后脚本重新跑，标记又出现，循环往复

这是典型的 **livenessProbe 演示用例**：故意制造"假死"，看 K8s 探针失败触发重启的效果。

#### 探针参数速查
| 字段 | 默认值 | 作用 |
|---|---|---|
| `initialDelaySeconds` | 0 | 容器启动后多久开始第一次探测 |
| `periodSeconds` | 10 | 探测间隔 |
| `timeoutSeconds` | 1 | 单次探测超时 |
| `failureThreshold` | 3 | 连续失败多少次判死 |
| `successThreshold` | 1 | 连续成功多少次判活（liveness 必须是 1） |

生产建议 `periodSeconds` 从 10s 起，演示里 3s 偏激进但合理。

#### 三大探针类型
- **exec**：在容器内执行命令，返回 0 算活
- **httpGet**：访问 HTTP 端点，2xx/3xx 算活
- **tcpSocket**：能建立 TCP 连接算活

---

### 15.2 httpGet 探针 path 的真实解析位置

#### 核心结论
**看 Nginx 配置，不是看 K8s。** `httpGet` 不是文件系统访问，是 HTTP 请求：
- path 拼到 URL 里发给容器 80 端口（`http://<pod-ip>:80/<path>`）
- 路径怎么解析 → **完全由容器内 Nginx 的 `root` / `alias` / `location` 决定**
- K8s 只管发请求，不管对应哪个文件系统位置

#### 演示 YAML
```yaml
readinessProbe:
  httpGet:
    port: 80
    path: /index2.html
    initialDelaySeconds: 1
    periodSeconds: 3
startupProbe:
  httpGet:
    path: /index1.html
    port: 80
    periodSeconds: 10
    failureThreshold: 30
```

`nginx:latest` 默认 `nginx.conf` 里有 `root /usr/share/nginx/html;`，所以：
- `/index2.html` → 访问容器内 `/usr/share/nginx/html/index2.html`
- `/index1.html` → 访问容器内 `/usr/share/nginx/html/index1.html`

只有当 Nginx 配置改成 `root /` 或 `alias /`，才走容器根目录。**默认镜像下结论是 Nginx 的 html 目录**。

#### 这是个"故意失败的演示"
默认 nginx 镜像里只有 `index.html`，**没有 index1.html / index2.html**：
- **startupProbe**：访问 `/index1.html` → 404 → 失败累计到 `failureThreshold: 30`（每 10s 一次 = 5 分钟）→ K8s 认为启动失败 → **重启 Pod**
- **readinessProbe**：访问 `/index2.html` → 404 → 探针失败 → **Pod 不会被加入 Service Endpoints**，收不到流量

目的是让你看 startupProbe 触发重启、readinessProbe 隔离流量的效果。生产里 path 必须写真实存在的文件。

#### 一句话速记
`httpGet.path` = **URL 路径**（不是文件系统路径），由容器内 Web 服务的 root/alias/location 解析为实际文件位置。

#### 探针失败后果对照
- startupProbe 失败 → 重启 Pod
- readinessProbe 失败 → 隔离流量（不重启）
- livenessProbe 失败 → 重启 Pod

---

### 15.3 lifecycle 钩子（postStart / preStop）

#### 钩子是什么
容器生命周期关键时刻的**自定义回调**，类似 Java 的 `init()` / `destroy()`：

| 钩子 | 触发时机 | 类比 |
|---|---|---|
| `postStart` | 容器创建后立即执行（ENTRYPOINT 之后） | 启动回调 |
| `preStop` | 容器被终止之前执行（SIGTERM 之前） | 销毁回调 |

支持 `exec`（容器内跑命令）和 `httpGet`（发 HTTP 请求）两种方式。

#### 演示 YAML
```yaml
lifecycle:
  postStart:
    exec:
      command: ["/bin/sh", "-c", "echo postStart > /usr/share/message"]
  preStop:
    exec:
      command: ["/bin/sh", "-c", "echo preStart > /usr/share/message"]
```

`lifecycle` 下有两个**不同类型的钩子**：`postStart` 1 个 + `preStop` 1 个，互不干扰。

#### postStart 详解
- **触发时机**：容器进程启动后**异步**触发，**不保证**先于 ENTRYPOINT 完成（常见误区）
- **失败后果**：钩子失败 → 容器被杀死并按重启策略重启
- **常见用途**：
  - 注册服务到注册中心
  - 复制配置文件 / 预热缓存
  - 通知外部系统"我起来了"
  - 初始化数据库 schema

#### preStop 详解
- **触发时机**：K8s 决定销毁容器时，先执行 preStop，再发 SIGTERM
- **阻塞**：K8s 等 preStop 跑完才往下走，但**默认宽限期 30 秒**，超时被 SIGKILL 强杀
- **常见用途**：
  - 优雅关闭（关闭数据库连接、刷新内存数据到磁盘）
  - 反注册服务（从负载均衡摘除、注销 Eureka）
  - 保存状态、上报监控

#### 容器终止完整顺序
```
K8s 决定终止 Pod
  → preStop 钩子执行（阻塞）
  → SIGTERM 发给主进程（容器自己处理）
  → 等待 terminationGracePeriodSeconds（默认 30s）
  → 还没死？ → SIGKILL 强杀
```

#### 演示脚本的行为
两个钩子写**同一个文件** `/usr/share/message`，**时序不同 → 值不同**：
- 容器正常运行期间看 → 内容是 `postStart`（preStop 还没跑）
- 容器被销毁前的瞬间 → preStop 覆盖 → 内容变成 `preStart`
- 想同时看到两个值 → 不可能（除非在 preStop 执行后立刻抓快照）

是钩子的经典演示：让你观察钩子到底有没有跑、什么时候跑的。生产里两个钩子的 command 当然不能写同一个文件——典型套路是 postStart 写启动日志、preStop 写清理日志。

---

### 15.4 ReplicationController 与 Pod 模板

#### RC 是什么
K8s **最老一代**的 Pod 副本控制器（现在被 ReplicaSet 取代，ReplicaSet 又被 Deployment 包装，但底层逻辑一样）。

**核心职责**：保证 spec.replicas 指定的副本数始终成立：
- Pod 挂了 → 自动补
- Pod 多出来 → 自动删
- 核心机制：**控制循环（reconciliation loop / 调谐循环）**

```
观察实际状态  vs  对比期望状态 → 不一致 → 执行调谐
```

#### 演示 YAML
```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: rc-demo
spec:
  replicas: 3
  selector:
    app: rc-demo
  template:
    metadata:
      name: rc-demo
      labels:
        app: rc-demo
    spec:
      containers:
      - name: rc-demo-container
        image: aaronxudocker/myapp:v1.0
        ports:
        - containerPort: 80
```

#### Pod 模板（template）怎么理解
template = **Pod 的样板/模具**，告诉控制器"以后要补 Pod 就按这个规格创建"。

类比：模具（template） vs 产品（Pod）；class（template） vs instance（Pod）。

**关键细节**：
1. **template.metadata.labels 必须包含 selector 的全部 label**，否则 K8s 拒绝创建（防止孤儿 Pod）
2. **template.metadata.name 写不写无所谓**：K8s 创建 Pod 时会强制清空，然后生成 `rc-demo-xxxxx`（带随机后缀）。最佳实践是不写
3. template.spec 会被原样复制成 Pod 的 spec

#### metadata 和 spec 为啥平级
这是 K8s API 对象的标准结构，**所有资源都遵循**：

```
apiVersion: v1           # API 版本
kind: <资源类型>
metadata:    # "我是谁" — 身份信息
  name, namespace, labels, annotations, uid
spec:        # "我想要什么" — 期望状态（你写的）
  ...
status:      # "我现在怎样" — 实际状态（控制器自动写，不让你写）
```

**类比**：

| 字段 | 简历类比 | 订单类比 |
|---|---|---|
| metadata | 名字、联系方式（你是谁） | 订单号、买家（谁下的） |
| spec | 期望岗位、期望薪资（你想要啥） | 商品规格、数量（你要买啥） |
| status | 入职后实际岗位、薪资 | 实际发货/收货状态 |

**设计精髓**：声明式 API。用户只管写 spec（期望），控制器持续对比 spec 和 status，不一致就调谐让 status 趋近 spec。用户永远不手动写 status。

#### YAML 的隐藏陷阱
1. `image: aaronxudocker/myapp:v1.0` — 私人镜像需要 `imagePullSecrets`，不然 `ImagePullBackOff`
2. selector 只有 1 个 label — 生产里通常多个 label 区分版本/环境
3. RC 已被淘汰 — K8s 1.18 后官方建议用 Deployment（自带滚动更新、回滚），但学 RC 是为了理解 Deployment 的底层

---

### 15.5 Service 删除命令详解

#### 最常用
```bash
kubectl delete svc <service-name>
```
`svc` = `service` 简写，完全等价。

#### 批量/选择删除
```bash
# 一次删多个
kubectl delete svc nginx-svc redis-svc

# 按 label 选择
kubectl delete svc -l app=nginx

# 删某个 namespace 下所有 svc（危险）
kubectl delete svc --all -n my-namespace

# 跨所有 namespace（超级危险）
kubectl delete svc --all --all-namespaces
```

#### 通过 YAML 文件删
```bash
kubectl delete -f service.yaml
```

#### 需要强制删除吗？
**不需要**。Service 是集群内逻辑对象（不是进程，没有"清理"动作），删除立即生效，没有 grace period 概念。Pod 那种 `-f --grace-period=0 --force` 套路对 Service 不适用。

#### 删除前的"看一眼"
```bash
kubectl get svc                  # 当前 namespace
kubectl get svc -A               # 所有 namespace
kubectl get svc -n kube-system   # 指定 namespace
```

#### 三个关键提醒

##### ① 删除 Service 不会删 Pod
Service 是逻辑对象，**后端 Pod 完全不受影响**——Pod 还活着，只是不再有 Service 把流量转给它了。要彻底清理得手动 `kubectl delete pod` 或 `kubectl delete deployment`。

##### ② selector 自动管理 Endpoints
如果 Service 用了 selector：
```yaml
selector:
  app: nginx
```
Service 会自动维护 Endpoints 对象（Pod IP 列表）。**删 Service 时 Endpoints 自动跟着没**，不用单独处理。

如果是 headless service（clusterIP: None）或手动指定 endpoints，删除时要注意 Endpoints 是否遗留。

##### ③ 别手贱 `--all`
生产里 `kubectl delete svc --all -n <业务ns>` 前必须确认 namespace 里没别人部署的关键服务（比如 kube-system 里那些），不然 cluster DNS、metrics-server 全没，集群能炸半天。

---

### 15.6 Deployment 三层标签结构（metadata.labels vs selector）

#### 核心结论
**Deployment 的 `metadata.labels` ≠ `spec.selector.matchLabels`**，是两码事：

- `metadata.labels` = **这个 Deployment 对象本身的标签**（给人/工具看的）
- `spec.selector.matchLabels` = **我这个 Deployment 管哪些 RS**（找别人的标签）

可以一样也可以不一样，但**最佳实践是保持一致**。

#### 演示 YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: myapp-deploy    # ⚠️ 跟 selector 不一致
  name: myapp-deploy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp          # ✅ 跟 RS 匹配
  template:
    metadata:
      labels:
        app: myapp        # ✅ 创建的 Pod 带这个
    spec:
      containers:
      - name: myapp
        image: aaronxudocker/myapp:v1.0
```

#### 三层标签完整图
```
Deployment
  ├─ metadata.labels:           app=myapp-deploy    ← 对象自己的标识
  ├─ spec.selector.matchLabels: app=myapp           ← 管哪些 RS
  └─ spec.template.metadata.labels: app=myapp       ← 创建的 Pod 带什么 label
       │
       ▼ Deployment 创建 RS
       
ReplicaSet
  ├─ metadata.labels:           app=myapp          ← 被 Deployment selector 匹配
  └─ spec.template.metadata.labels: app=myapp       ← 创建的 Pod 带什么 label
       │
       ▼ RS 创建 Pod
       
Pod
  └─ metadata.labels:           app=myapp          ← 被 Service selector 匹配
```

**每一层 selector 都在找下一层的 label**：
- Deployment selector → 找 RS（用 RS labels）
- RS selector → 找 Pod（用 Pod labels）
- Service selector → 找 Pod（用 Pod labels）

#### 为啥这段 YAML 这样写能工作
- Deployment 拿 `app=myapp` 找 RS → 创建的 RS label 就是 `app=myapp` → 匹配成功
- RS 拿 `app=myapp` 找 Pod → 创建的 Pod label 就是 `app=myapp` → 匹配成功
- Service 拿 `app=myapp` 找 Pod → 匹配成功

**Service 根本不关心 Deployment 的 metadata.labels 是啥**——Service 只认 Pod labels。

#### Deployment 的 metadata.labels 到底是干嘛的
纯粹是给"Deployment 对象本身"贴的标签，用于：
1. 给人查：`kubectl get deploy -l app=myapp-deploy`
2. 给工具引用：Service Mesh（Istio/Linkerd）、监控、CI/CD 识别资源
3. 跨 controller 关联：某些 operator 按 label 找 Deployment

**绝对不会参与 Deployment → RS 的匹配**。这是新手最大误区。

#### YAML 的隐藏陷阱 + 最佳实践
```yaml
metadata:
  labels:
    app: myapp-deploy     # ⚠️ 跟 selector 不一致，容易误导
```
虽然功能没问题，但**非常容易把人搞糊涂**。最佳实践：

```yaml
# ✅ 推荐 1：保持一致，避免歧义
metadata:
  labels:
    app: myapp
spec:
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp

# ✅ 推荐 2：想区分就用不冲突的 label key
metadata:
  labels:
    app: myapp              # 核心标签，跟 selector 一致
    deployment: myapp-deploy  # 额外标识
```

---
