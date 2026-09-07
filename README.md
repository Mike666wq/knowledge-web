# knowledge-web

基于 [VitePress](https://vitepress.dev/) 的个人 Markdown 笔记站：把 `notes/` 目录里的 Markdown 笔记编译成纯静态网站，通过 Docker 镜像交付，任意机器 `docker pull` 即用。

![CI](https://github.com/<你的用户名>/knowledge-web/actions/workflows/build-image.yml/badge.svg)

## ✨ 特性

- **Markdown 优先**：笔记放进 `notes/` 目录即成为站点页面，构建时编译为纯 HTML，无后端进程
- **递归侧边栏**：目录即站点结构，自动识别 front-matter `title` 与日期前缀命名（`2024-01-15-xxx.md` → `2024-01-15 · xxx`）
- **暗色 / 亮色主题**：显式切换按钮，跟随记忆
- **本地全文搜索**：内置 LocalSearchProvider，中文友好
- **GFM 全特性**：任务列表、表格、删除线、代码高亮（Shiki）开箱即用
- **40+ 自研动效组件**：主题卡片、粒子星空、翻转书、行星系、终端按钮等趣味元素（见 `docs/.vitepress/theme/components/`）
- **端到端冒烟测试**：`npm run smoke-test`，30 项功能逐项校验
- **Docker 镜像交付**：GitHub Actions 自动构建，多阶段构建最终镜像仅 ~25 MB

## 📦 Docker 使用（推荐）

镜像在每次推送到 `main` 时自动更新：

```bash
docker pull ghcr.io/<你的用户名>/knowledge-web:latest
docker run -d --name knowledge-web -p 8080:80 ghcr.io/<你的用户名>/knowledge-web:latest
```

浏览器打开 `http://localhost:8080` 即可。

或使用 docker-compose：

```yaml
services:
  knowledge-web:
    image: ghcr.io/<你的用户名>/knowledge-web:latest
    container_name: knowledge-web
    ports:
      - "8080:80"
    restart: unless-stopped
```

```bash
docker compose up -d          # 启动
docker compose pull && docker compose up -d   # 更新到最新
```

> 镜像首次发布后默认为 private，如需匿名拉取，请在 GitHub → Packages → knowledge-web → Package settings 中改为 Public。固定版本请使用 `v*` 标签构建的版本镜像（如 `:1.2.0`）。

## 🛠 本地开发

```bash
# 1. 克隆并安装依赖（需要 Node ≥ 18）
git clone https://github.com/<你的用户名>/knowledge-web.git
cd knowledge-web
npm install

# 2. 建立 ./docs/notes 软链（首次或重命名 notes 目录时跑一次）
npm run sync-notes

# 3. 启动开发服务器（实时预览，改笔记自动刷新）
npm run dev          # → http://localhost:5173
```

## ✍️ 写笔记

把 `.md` 文件放到 `notes/` 目录下，任意层级子目录都行：

```
notes/
├── linux/shell-cheatsheet.md
├── linux/shell-cheatsheet/     ← 与笔记同名的图片目录
│   └── diagram.svg
└── daily/2024-01-15-morning-run.md
```

- 图片引用用相对路径：`![说明](diagram.svg)`
- front-matter 可选指定标题：

  ```markdown
  ---
  title: 自定义标题
  ---
  ```

- 每加一篇新笔记，`npm run dev` 实时生效；生产产物重新 `npm run build`（或直接 push 触发 CI）
- ⚠️ 代码块**外**不要写裸 `{{` 或 `{%`——VitePress 会交给 Vue 模板引擎解析导致构建失败。确需展示时转义为 `&#123;&#123;` / `&#123;%`（`npm run check-md` 可提前检查）

## 🏗 从源码构建镜像

```bash
docker build -t knowledge-web:local .
docker run -d -p 8080:80 knowledge-web:local
```

多阶段构建：Stage 1（`node:22-alpine`）安装依赖、执行 `check-md` 门禁与 VitePress 构建；Stage 2（`nginx:1.27-alpine`）只保留静态产物，最终镜像不含 Node、依赖与源码。

## 📜 常用命令

| 命令 | 作用 |
| --- | --- |
| `npm run dev` | 启动开发服务器（实时热更新） |
| `npm run build` | 构建生产产物到 `docs/.vitepress/dist/` |
| `npm run preview` | 本地预览生产产物 |
| `npm run sync-notes` | 重建 `docs/notes` 软链（仅首次） |
| `npm run check-md` | 检查笔记中的危险插值语法（CI 门禁） |
| `npm run smoke-test` | 跑 30 项端到端测试 |
| `npm run clean` | 清理构建缓存与产物 |
| `docker build -t knowledge-web .` | 本地构建 Docker 镜像 |

## 📁 项目结构

```
knowledge-web/
├── docs/                        ← VitePress 源目录
│   ├── .vitepress/
│   │   ├── config.mjs           ← ★ 核心配置：递归侧边栏 + 主题
│   │   └── theme/
│   │       ├── index.js         ← 主题入口 / Layout 覆盖
│   │       ├── custom.css       ← 全局样式
│   │       ├── ShellLayout.vue
│   │       └── components/      ← 40+ 自研动效组件
│   ├── index.md                 ← 首页（hero 风格）
│   ├── about.md                 ← 关于页
│   ├── fun.md                   ← 趣味组件展示页
│   ├── public/                  ← 音乐、壁纸等站点资源
│   └── notes -> ../notes        ← 软链 → 真实笔记根目录
├── notes/                       ← ★ 你的笔记根目录（任意层级）
├── scripts/                     ← 辅助脚本（sync / check / smoke-test …）
├── .github/workflows/           ← CI：自动构建 Docker 镜像并推送 GHCR
├── Dockerfile                   ← 多阶段镜像构建
├── nginx.conf                   ← 容器内 Nginx 配置（gzip / 缓存）
└── 部署计划.md                   ← CI/CD 完整方案与操作手册
```

## ⚙️ 配置

核心配置集中在 `docs/.vitepress/config.mjs`：

| 常量 | 默认值 | 说明 |
| --- | --- | --- |
| `NOTES_ROOT` | `../../notes` | 笔记根目录（相对 config.mjs） |
| `BASE_PREFIX` | `/notes/` | 笔记路由前缀 |
| `SITE_BASE` | `/` | 站点 base；独立域名 / 容器部署保持 `/`，子路径部署时改为 `/<path>/` |
| `SITE_DESC` | — | 站点描述 |

## 🔄 CI/CD

推送到 `main`（或打 `v*` 标签）自动触发 GitHub Actions：

```
push → check-md 门禁 → VitePress 构建 → Docker 多阶段构建 → 推送镜像到 GHCR
```

完整的流水线逐步详解、GitHub 仓库操作指南、失败排查表见 [部署计划.md](./部署计划.md)。

## 🔒 隐私提示

本仓库为**公开**仓库，`notes/` 中的全部笔记内容对所有人可见。请确认笔记无敏感信息后再推送；含私密内容时请改用 Private 仓库（CI 与镜像构建流程完全相同，拉取私有镜像前需 `docker login ghcr.io`）。

## 📄 License

暂未附带开源许可证（默认保留所有权利）。如需以 MIT / Apache-2.0 等方式开源，请在仓库根目录添加对应的 `LICENSE` 文件并更新本节。
