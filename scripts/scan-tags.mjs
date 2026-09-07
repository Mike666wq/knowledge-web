// 扫描 notes/ 下所有 md：找出代码围栏外、可能被 Vue 当成 HTML 标签的裸 <xxx>
import { readFileSync, readdirSync, statSync } from 'fs'
import { join, relative } from 'path'

const ROOT = '/srv/knowledge-web/notes'
const ALLOWED = new Set([
  'img', 'a', 'div', 'span', 'br', 'p', 'details', 'summary', 'b', 'i', 'em', 'strong',
  'table', 'thead', 'tbody', 'tr', 'th', 'td', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4',
  'h5', 'h6', 'code', 'pre', 'svg', 'path', 'circle', 'rect', 'line', 'iframe', 'video',
  'audio', 'hr', 'sup', 'sub', 'font', 'center', 'u', 's', 'small', 'big', 'blockquote',
])

function walk(dir, out = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) walk(p, out)
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

const files = walk(ROOT)
const issues = []

for (const file of files) {
  const src = readFileSync(file, 'utf8')
  const lines = src.split('\n')
  let inFence = false
  let fenceMark = ''
  lines.forEach((line, i) => {
    const fence = line.match(/^\s*(`{3,}|~{3,})/)
    if (fence) {
      if (!inFence) { inFence = true; fenceMark = fence[1][0] }
      else if (fence[1][0] === fenceMark) inFence = false
      return
    }
    if (inFence) return
    // 行内代码先摘掉（`xxx` 里的 < > 不算）
    const cleaned = line.replace(/`[^`]*`/g, '``')
    const re = /<([a-zA-Z][a-zA-Z0-9_-]*)(\s|>|\/)/g
    let m
    while ((m = re.exec(cleaned))) {
      const tag = m[1].toLowerCase()
      if (!ALLOWED.has(tag)) {
        issues.push(`${relative(ROOT, file)}:${i + 1}: <${m[1]}> ｜ ${line.trim().slice(0, 80)}`)
      }
    }
  })
}

console.log(issues.length ? issues.join('\n') : 'clean ✓')
console.log(`\n共 ${issues.length} 处`)
