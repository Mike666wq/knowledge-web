// 扫描所有 md 里的图片/资源引用，找出目标文件不存在的「断链」
import { readFileSync, readdirSync, statSync, existsSync } from 'fs'
import { join, dirname, resolve } from 'path'

const ROOT = '/srv/knowledge-web/docs'
function walkMd(dir, out = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.isDirectory()) {
      if (e.name !== 'node_modules' && e.name !== '.vitepress' && e.name !== 'public') walkMd(p, out)
    } else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

const mdFiles = walkMd(ROOT)
const broken = []

for (const md of mdFiles) {
  const src = readFileSync(md, 'utf8')
  const dir = dirname(md)
  const re = /(?:!\[[^\]]*\]\(|<img[^>]*src=")([^")\s]+)(?:\)|")/g
  let m
  while ((m = re.exec(src))) {
    const ref = m[1]
    if (/^(https?:|\/\/|data:)/.test(ref)) continue
    const abs = resolve(dir, decodeURIComponent(ref))
    if (!existsSync(abs)) {
      broken.push(`${relative(ROOT, md)} → ${ref}`)
    }
  }
}

console.log(broken.length ? broken.join('\n') : 'no broken refs ✓')
console.log(`\n共 ${broken.length} 处断链`)
