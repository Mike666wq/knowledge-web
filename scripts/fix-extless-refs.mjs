// 找出 md 里引用的、但文件本身没有图片扩展名的资源 → 补 .png 后缀并更新引用
import { readFileSync, readdirSync, statSync, renameSync, existsSync, writeFileSync } from 'fs'
import { join, relative } from 'path'

const ROOT = '/srv/knowledge-web/notes'
const IMG_EXT = /\.(png|jpe?g|gif|webp|svg|bmp|avif)$/i

function walkMd(dir, out = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) walkMd(p, out)
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

const mdFiles = walkMd(ROOT)
const fixes = [] // { mdPath, ref, absPath }

for (const md of mdFiles) {
  const src = readFileSync(md, 'utf8')
  const dir = md.slice(0, md.lastIndexOf('/'))
  const re = /(?:!\[[^\]]*\]\(|<img[^>]*src=")([^")\s]+)(?:\)|")/g
  let m
  while ((m = re.exec(src))) {
    const ref = m[1]
    if (/^(https?:|\/\/|data:)/.test(ref)) continue
    if (IMG_EXT.test(ref)) continue
    const abs = join(dir, ref)
    if (existsSync(abs) && statSync(abs).isFile()) {
      fixes.push({ md, ref, abs })
    }
  }
}

console.log('引用了无扩展名文件的 md 引用数:', fixes.length)

// 逐个补 .png 后缀
let n = 1
for (const f of fixes) {
  let name = f.abs.slice(f.abs.lastIndexOf('/') + 1)
  // 已有其它扩展名（如 .tar.gz）的跳过
  if (name.includes('.')) {
    console.log('  跳过（本身有扩展名）:', name)
    continue
  }
  const newName = name + '.png'
  const newAbs = f.abs + '.png'
  if (!existsSync(newAbs)) {
    renameSync(f.abs, newAbs)
  }
  // 更新该 md 里的引用（所有此 md 中的同名引用）
  let src = readFileSync(f.md, 'utf8')
  src = src.split('(' + f.ref + ')').join('(' + newName + ')')
  src = src.split('src="' + f.ref + '"').join('src="' + newName + '"')
  writeFileSync(f.md, src)
  console.log('  fixed:', name, '→', newName)
  n++
}
