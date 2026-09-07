// 一次性把 notes/ 里文件名含危险字符的图片重命名为安全名，并更新 md 引用
// 危险字符：! & ? = , # % { } ' " + ; @ `（这些会让 Vite/Markdown 解析炸掉）
import { readFileSync, writeFileSync, readdirSync, renameSync } from 'fs'
import { join } from 'path'

const ROOT = '/srv/knowledge-web/notes'
const IMG_EXT = /\.(png|jpe?g|gif|webp|svg|bmp|avif)$/i
const BAD = /[!&?=,#%{}'"`+;@\[\]<>]/

// 1) 收集危险文件名
const bad = []
function walkCollect(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) walkCollect(p)
    else if (IMG_EXT.test(e.name) && BAD.test(e.name)) bad.push(p)
  }
}
walkCollect(ROOT)

// 2) 重命名为 img-safe-N.ext
const renames = []
let n = 1
for (const from of bad) {
  const dir = from.slice(0, from.lastIndexOf('/'))
  const ext = (from.match(IMG_EXT) || ['.png'])[0].toLowerCase()
  let name = `img-safe-${n}${ext}`
  let to = join(dir, name)
  while (readdirSync(dir).includes(name)) { n++; name = `img-safe-${n}${ext}`; to = join(dir, name) }
  renameSync(from, to)
  renames.push({ oldName: from.slice(from.lastIndexOf('/') + 1), newName: name })
  n++
}

// 3) 更新所有 md 引用（按旧文件名精确匹配）
const mdFiles = []
function walkMd(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) walkMd(p)
    else if (e.name.endsWith('.md')) mdFiles.push(p)
  }
}
walkMd(ROOT)

let refs = 0
for (const md of mdFiles) {
  let src = readFileSync(md, 'utf8')
  let changed = false
  for (const r of renames) {
    if (src.includes(r.oldName)) {
      src = src.split(r.oldName).join(r.newName)
      changed = true
      refs++
    }
  }
  if (changed) writeFileSync(md, src)
}

console.log(`renamed: ${renames.length}, md refs updated: ${refs}`)
renames.forEach(r => console.log('  ', r.oldName.slice(0, 60), '→', r.newName))
