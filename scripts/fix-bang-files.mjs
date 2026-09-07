// 处理 xxx.png!thumbnail 这类「带感叹号后缀」的文件：
// 如果同名去掉 !thumbnail 后存在原文件 → 缩略图冗余，直接删除；
// 否则改名为 xxx.thumbnail.png 并更新 md 引用
import { readFileSync, writeFileSync, readdirSync, renameSync, unlinkSync, existsSync } from 'fs'
import { join } from 'path'

const ROOT = '/srv/knowledge-web/notes'
const bad = []
function walk(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) walk(p)
    else if (e.name.includes('!')) bad.push(p)
  }
}
walk(ROOT)

const renames = []
const deletes = []
for (const p of bad) {
  const dir = p.slice(0, p.lastIndexOf('/'))
  const name = p.slice(p.lastIndexOf('/') + 1)
  const bang = name.indexOf('!')
  const base = name.slice(0, bang)                    // R5j17V2j8h153YXZ.png
  const suffix = name.slice(bang + 1)                 // thumbnail
  if (existsSync(join(dir, base))) {
    // 原图已存在，缩略图冗余 → 删除
    unlinkSync(p)
    deletes.push(name)
  } else {
    // 原图不存在，缩略图就是唯一的图 → 改成安全名
    const newName = base.replace(/\.(png|jpe?g|gif|webp)$/i, '') + '-' + suffix.replace(/[^\w]/g, '') + '.png'
    renameSync(p, join(dir, newName))
    renames.push({ old: name, new: newName, dir })
  }
}

// 更新 md 引用（改名的）
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
    if (src.includes(r.old)) { src = src.split(r.old).join(r.new); changed = true; refs++ }
  }
  if (changed) writeFileSync(md, src)
}

console.log(`deleted redundant: ${deletes.length}, renamed: ${renames.length}, refs updated: ${refs}`)
deletes.forEach(d => console.log('  del:', d.slice(0, 60)))
renames.forEach(r => console.log('  ren:', r.old.slice(0, 50), '→', r.new))
