#!/usr/bin/env node
/**
 * 把笔记里（代码围栏外的）HTML <img src="相对路径"> 统一转成 markdown 图片语法：
 *   <img src="目录/图.png" alt="xx" style="zoom:80%;" />
 *     →  ![xx](目录/图.png)
 * 原因：HTML <img> 走 vite transformAssetUrls，中文/编码路径解析不稳定（rollup/SSR 双双翻车）；
 *       markdown 图片由 markdown-it 归一化，全站 998 个引用验证可靠。
 * - 文件缺失 → 注释掉（markdown 注释，构建降级为无图）
 * - 应用目录更名映射（带空格目录 → 安全名）
 * - 保留 alt；丢弃 zoom 样式（导出工具残留）
 */
import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from 'node:fs'
import { resolve, dirname } from 'node:path'

const NOTES = '/srv/knowledge-web/notes'
const DIR_RENAMES = [
  ['08.docker compose单机编排', '08-compose-images']
]

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (name === '.git' || name === 'node_modules') continue
    const p = resolve(dir, name)
    if (statSync(p).isDirectory()) walk(p, out)
    else if (name.endsWith('.md')) out.push(p)
  }
  return out
}
function decodeURI_safe(s) { try { return decodeURIComponent(s) } catch { return s } }

let files = 0, converted = 0, commented = 0, skipped = 0
for (const file of walk(NOTES)) {
  const lines = readFileSync(file, 'utf-8').split('\n')
  let inFence = false, changed = false
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (/^\s*(```|~~~)/.test(line)) { inFence = !inFence; continue }
    if (inFence) continue
    if (!/<img\b/i.test(line)) continue

    const l = line.replace(/<img\b([^>]*)>/gi, (m, attrs) => {
      const srcM = attrs.match(/\bsrc="([^"]+)"/i)
      if (!srcM) { skipped++; return m }
      const src = srcM[1]
      // 绝对路径 / http(s) / data: 不动
      if (/^(\/|[a-z]+:|data:|#)/i.test(src)) { skipped++; return m }
      let p = decodeURI_safe(src)
      for (const [o, n] of DIR_RENAMES) p = p.split(o).join(n)
      const abs = resolve(dirname(file), p)
      const altM = attrs.match(/\balt="([^"]*)"/i)
      const alt = altM ? altM[1] : 'img'
      if (existsSync(abs)) {
        converted++; changed = true
        return `![${alt}](${p})`
      }
      commented++; changed = true
      console.warn(`[warn] 图片缺失，已注释: ${file} → ${p}`)
      return `<!-- 原图缺失: ![${alt}](${p}) -->`
    })
    if (l !== line) lines[i] = l
  }
  if (changed) { writeFileSync(file, lines.join('\n')); files++ }
}
console.log(`\n完成: 转换 ${converted} 个 <img> → markdown, 注释 ${commented} 个缺失, 跳过 ${skipped} 个(绝对/外链), 涉及 ${files} 个文件`)
