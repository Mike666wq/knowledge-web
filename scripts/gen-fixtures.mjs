// 生成 5 篇示例笔记，覆盖 GFM 所有特性 + 图片。
// 跑一次后会覆盖 ./notes/ 下演示用的目录与文件。
import { mkdirSync, writeFileSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = resolve(__dirname, '../notes')

function ensure(dir) { mkdirSync(dir, { recursive: true }) }
function write(p, content) {
  ensure(dirname(p))
  writeFileSync(p, content, 'utf-8')
}

// 1x1 透明 PNG（最小有效 PNG，base64 编码）
const TINY_PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
  'base64'
)
// 极简 SVG 矢量图
const SAMPLE_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <rect width="200" height="100" fill="#3b82f6"/>
  <text x="100" y="55" font-size="20" fill="white" text-anchor="middle" font-family="sans-serif">Shell Diagram</text>
</svg>`

// =======================================================
// 笔记 1：README（笔记目录首页）
// =======================================================
write("/srv/knowledge-web/notes/README.md", `---
title: 笔记总览
---

# 笔记总览

这里汇总了所有笔记的入口。点击左侧目录浏览各分类。

## 分类索引

- **programming**：编程相关（Python、JavaScript 等）
- **linux**：Linux 使用与运维
- **daily**：日常记录

## 示例特性

下面的笔记覆盖了所有 Markdown 特性，请逐个查看：

1. [Python 基础](programming/python/basics) — 含代码块、表格、图片
2. [JavaScript 异步](programming/javascript/async-await) — 含任务列表
3. [Shell 速查](linux/shell-cheatsheet) — 含 SVG 矢量图
4. [晨跑日记](daily/2024-01-15-morning-run) — 含日期前缀文件名 + 图片
`)

// =======================================================
// 笔记 2：programming/python/basics.md（带 front-matter 标题 + 图片 + 表格 + 代码块）
// =======================================================
write("/srv/knowledge-web/notes/programming/python/basics.md", `---
title: Python 基础语法
---

# Python 基础语法

这是一篇示例笔记，用于验证 VitePress 的渲染。

## 标题层级

### 三级标题

#### 四级标题

## 行内元素

普通段落里的 **加粗**、*斜体*、***粗斜体***、~~删除线~~、\`行内代码\` 都应正常显示。

引用块：

> 知识就是力量。
> —— 弗朗西斯·培根

## 列表

### 无序列表

- 苹果
  - 红富士
  - 国光
- 香蕉
- 樱桃

### 有序列表

1. 第一步：准备环境
2. 第二步：写代码
3. 第三步：测试

### 任务列表

- [x] 已完成：搭建脚手架
- [x] 已完成：编写配置
- [ ] 待办：接入评论系统（暂不做）
- [ ] 待办：CDN 加速

## 链接

- 外部链接：[VitePress 官网](https://vitepress.dev/)
- 内部链接：[笔记总览](/notes/README)

## 图片

下面是 basics.md 同级 basics/ 目录里的图片：

![Python Logo](basics/python-logo.png)

## 表格

| 特性       | 支持 | 备注            |
| ---------- | ---- | --------------- |
| GFM 表格   | ✅   | 默认开启        |
| 任务列表   | ✅   | 需 markdown-it 插件 |
| 代码高亮   | ✅   | Shiki 引擎      |
| 数学公式   | ❌   | 暂未启用        |

## 代码块

\`\`\`python
def fib(n: int) -> int:
    """斐波那契数列"""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print([fib(i) for i in range(10)])
\`\`\`

\`\`\`javascript
// Promise 链
fetch('/api/data')
  .then(r => r.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
\`\`\`

## 分隔线

---

以上就是本节内容。
`)

// 给 basics.md 准备一张 PNG 图片
write("/srv/knowledge-web/notes/programming/python/basics/python-logo.png", TINY_PNG)

// =======================================================
// 笔记 3：programming/javascript/async-await.md（任务列表密集）
// =======================================================
write("/srv/knowledge-web/notes/programming/javascript/async-await.md", `# JavaScript 异步编程

## 学习清单

- [x] 理解回调函数
- [x] 掌握 Promise
- [ ] 深入 async/await
- [ ] 了解事件循环

## Promise vs async/await

| 写法       | 可读性 | 错误处理     |
| ---------- | ------ | ------------ |
| 链式 then  | 一般   | .catch()     |
| async/await | 高     | try/catch    |

## 示例代码

\`\`\`javascript
async function loadUser(id) {
  try {
    const res = await fetch(\`/api/users/\${id}\`);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } catch (err) {
    console.error('加载用户失败:', err);
    return null;
  }
}
\`\`\`

> 注意：\`await\` 必须用在 \`async\` 函数内部。
`)

// =======================================================
// 笔记 4：linux/shell-cheatsheet.md（带 SVG 矢量图）
// =======================================================
write("/srv/knowledge-web/notes/linux/shell-cheatsheet.md", `---
title: Shell 常用命令速查
---

# Shell 常用命令速查

## 文件操作

| 命令       | 作用         |
| ---------- | ------------ |
| \`ls -la\` | 详细列表     |
| \`pwd\`    | 当前路径     |
| \`cd ~\`   | 回到家目录   |
| \`cp -r\`  | 递归复制     |
| \`rm -rf\` | 强制递归删除 |

## 进程管理

- \`ps aux\`：查看所有进程
- \`top\`：实时监控
- \`kill -9 <pid>\`：强制结束

## 架构示意

![架构图](shell-cheatsheet/diagram.svg)

## TODO

- [x] 文件操作
- [x] 进程管理
- [ ] 网络诊断（\`netstat\` / \`ss\`）
- [ ] 磁盘分析（\`du\` / \`df\`）
`)

write("/srv/knowledge-web/notes/linux/shell-cheatsheet/diagram.svg", SAMPLE_SVG)

// =======================================================
// 笔记 5：daily/2024-01-15-morning-run.md（日期前缀文件名 + 图片）
// =======================================================
write("/srv/knowledge-web/notes/daily/2024-01-15-morning-run.md", `---
title: 晨跑 5 公里
---

# 晨跑 5 公里

今天早上 6:30 出门，沿河边跑了 5 公里，配速 5'30"/km。

## 路线

![河边路线](2024-01-15-morning-run/route.png)

## 感受

- 空气很好
- 风有点大
- 河边樱花开了

## 数据

| 项目     | 数值      |
| -------- | --------- |
| 距离     | 5.0 km    |
| 用时     | 27'30"    |
| 平均配速 | 5'30"/km  |
| 消耗     | ~320 kcal |

今天的状态：**不错**。
`)

write("/srv/knowledge-web/notes/daily/2024-01-15-morning-run/route.png", TINY_PNG)

// =======================================================
// 笔记 6（最深嵌套）：programming/python/advanced/decorators.md（三层子目录）
// =======================================================
write("/srv/knowledge-web/notes/programming/python/advanced/decorators.md", `---
title: 装饰器深入
---

# 装饰器深入

这是三层子目录的笔记，用于验证递归扫描。

## 基础装饰器

\`\`\`python
def logger(fn):
    def wrapper(*args, **kwargs):
        print(f'call {fn.__name__}')
        return fn(*args, **kwargs)
    return wrapper

@logger
def hello(name):
    return f'Hello, {name}!'
\`\`\`

## 带参数的装饰器

- [x] 实现
- [ ] 测试
- [ ] 文档
`)

console.log('✓ 示例笔记已生成在 ./notes/')