---
sidebar: true
aside: false
---

# 关于 ~/bbben

<ClientOnly>
  <div class="author-stage">
    <AuthorCard />
  </div>
</ClientOnly>

一个喜欢折腾 Linux 的学习者。这里记录我在运维、编程与安全方向的学习笔记，
算是一份公开的「学习存档」——写下来，才算真的学会。

## 项目简介

**~/bbben** 是一个纯静态的个人知识库：所有内容都住在 `notes/` 目录里，Markdown 写完即发布，没有后端、没有数据库、没有追踪脚本。

- 📚 **自动目录树** —— 按目录结构生成导航，中文文件名友好
- 🔍 **本地全文搜索** —— 构建时建索引，搜索不走任何外部服务
- 🌗 **明暗双主题** —— 跟随系统或手动固定，还有两只熊猫看着你切
- 📝 **GFM 全特性** —— 表格 / 任务列表 / 代码块 / 删除线开箱即用
- 🚀 **纯静态部署** —— 产物只是 HTML/CSS/静态资源，任意静态服务器皆可托管

## 技术栈

只列方向和级别，不细到版本与项目细节 😎

**🛠️ 本站构建**

<div class="chips">
  <span class="chip">VitePress</span>
  <span class="chip">Vue 3</span>
  <span class="chip">Markdown / GFM</span>
  <span class="chip">纯静态部署</span>
</div>

**🐧 在学方向**（对应左侧笔记分类）

<div class="chips">
  <span class="chip">Linux 基础与运维</span>
  <span class="chip">Shell 脚本</span>
  <span class="chip">网络基础</span>
  <span class="chip">信息安全</span>
  <span class="chip">Python</span>
  <span class="chip">AI 工具链</span>
</div>

**🧰 常用工具**

<div class="chips">
  <span class="chip">Git</span>
  <span class="chip">VS Code / Vim</span>
  <span class="chip">Docker（入门）</span>
  <span class="chip">Nginx（入门）</span>
</div>

## 联系方式

- GitHub：<https://github.com/Mike666wq>

> 只此一个公开渠道，其余暂不公开 —— 欢迎在 Issues 里交流。

## 站点维护速查

<details>
<summary>📖 目录约定 · 新增笔记 · 本地预览 · 部署（点开展开）</summary>

### 目录约定

```
notes/
├── README.md
├── programming/
│   ├── python/
│   │   ├── basics.md
│   │   └── basics/      ← 与 basics.md 同名同级的图片目录
│   │       └── screenshot.png
│   └── ...
└── daily/
    ├── 2024-01-15-foo.md
    └── 2024-01-15-foo/
        └── photo.jpg
```

- 任意层级子目录、任意文件名（中文/空格/特殊字符）都支持
- 文件名形如 `2024-01-15-foo.md` 的，侧栏显示为「2024-01-15 · foo」
- front-matter `title:` 可自定义标题

### 新增笔记

1. 在 `notes/` 下任意位置创建 `.md`
2. （可选）建同名目录存图片
3. `npm run build` 重新发布

### 本地预览

```bash
npm run dev          # → http://localhost:5173
```

### 部署

```bash
npm run build        # 产物在 docs/.vitepress/dist/
```

把 `dist/` 整目录上传到任意静态服务器即可。

</details>

<style>
.author-stage {
  display: flex;
  justify-content: center;
  padding: 1.5rem 0 2rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin: 0.4rem 0 1.1rem;
}

.chip {
  padding: 0.32rem 0.85rem;
  border-radius: 999px;
  font-size: 0.85rem;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  transition: all 0.25s ease;
}

.chip:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

details summary {
  cursor: pointer;
  font-weight: 600;
  color: var(--vp-c-brand-1);
}
</style>
