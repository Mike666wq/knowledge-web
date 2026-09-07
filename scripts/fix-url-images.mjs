// 把「图床 URL 当文件名」的图片重命名为安全短名，并同步更新 md 引用
// URL 里的 & ? = , 会让 Vite 把文件当 JS 模块解析，直接炸构建
import { readFileSync, readdirSync, renameSync, writeFileSync } from 'fs'
import { join } from 'path'

const ROOT = '/srv/knowledge-web/notes'
const bad = []
const renames = [] // { from, to }

function walk(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) walk(p)
    else if (/&|\?|=|,/.test(e.name)) bad.push(p)
  }
}
walk(ROOT)

let n = 1
for (const from of bad) {
  const dir = from.slice(0, from.lastIndexOf('/'))
  const ext = from.slice(from.lastIndexOf('.'))
  let to = join(dir, `img-ref-${n}${ext}`)
  // 避免和已有文件撞名
  try {
    while (readdirSync(dir).includes(to.slice(to.lastIndexOf('/') + 1))) {
      n++
      to = join(dir, `img-ref-${n}${ext}`)
    }
  } catch {}
  renameSync(from, to)
  renames.push({ from, to })
  n++
}

// 同步更新所有 md 引用（按文件名精确替换）
const mdFiles = []
function walkMd(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) walkMd(p)
    else if (e.name.endsWith('.md')) mdFiles.push(p)
  }
}
walkMd(ROOT)

let refCount = 0
for (const md of mdFiles) {
  let src = readFileSync(md, 'utf8')
  let changed = false
  for (const r of renames) {
    const name = r.from.slice(r.from.lastIndexOf('/') + 1)
    if (src.includes(name)) {
      src = src.split(name).join(r.to.slice(r.to.lastIndexOf('/') + 1))
      changed = true
      refCount++
    }
  }
  if (changed) writeFileSync(md, src)
}

console.log(`renamed ${renames.length} files, updated refs in md: ${refCount}`)
renames.forEach(r => console.log('  ', r.from.slice(r.from.lastIndexOf('/') + 1).slice(0, 50), '→', r.to.slice(r.to.lastIndexOf('/') + 1)))
