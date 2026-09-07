// 全量预检：把所有「目标文件不存在」的本地图片引用注释掉
// 注释保留原路径，以后补了图片可以恢复
import { readFileSync, writeFileSync, readdirSync, existsSync, statSync } from 'fs'
import { join, dirname, resolve, relative } from 'path'

const ROOT = '/srv/knowledge-web/docs'
function walkMd(dir, out = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name)
    if (e.name === 'node_modules' || e.name === '.vitepress' || e.name === 'public') continue
    if (statSync(p).isDirectory()) walkMd(p, out)  // statSync 跟随符号链接（docs/notes → /notes）
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

const mdFiles = walkMd(ROOT)
let total = 0
const byFile = []

for (const md of mdFiles) {
  const src = readFileSync(md, 'utf8')
  const dir = dirname(md)
  const lines = src.split('\n')
  let inFence = false, fenceMark = ''
  let fileFixed = 0

  const newLines = lines.map((line, idx) => {
    const f = line.match(/^\s*(`{3,}|~{3,})/)
    if (f) {
      if (!inFence) { inFence = true; fenceMark = f[1][0] }
      else if (f[1][0] === fenceMark) inFence = false
      return line
    }
    if (inFence) return line

    // 行内代码先摘出，避免误判
    const codeSpans = []
    const work = line.replace(/`[^`]*`/g, m => { codeSpans.push(m); return '\u0000' + (codeSpans.length - 1) + '\u0000' })

    const fixed = work.replace(/(!\[[^\]]*\]\([^)]+\)|<img[^>]*src="[^"]+"[^>]*>)/g, (img, _1, off, s) => {
      const m = img.match(/\]\(([^)]+)\)/) || img.match(/src="([^"]+)"/)
      if (!m) return img
      let ref = m[1]
      if (/^(https?:|\/\/|data:|#)/.test(ref)) return img
      // md 引用相对当前 md 目录；URL 编码还原后判断
      let p = ref
      try { p = decodeURIComponent(p) } catch {}
      // 去掉可能的锚点
      p = p.split('#')[0]
      if (!p) return img
      const abs = resolve(dir, p)
      if (existsSync(abs)) return img
      total++
      fileFixed++
      return `<!-- ${img} -->`
    })

    return fixed.replace(/\u0000(\d+)\u0000/g, (_, i) => codeSpans[+i])
  })

  if (fileFixed > 0) {
    writeFileSync(md, newLines.join('\n'))
    byFile.push(`${relative(ROOT, md)}: ${fileFixed} 处`)
  }
}

console.log(byFile.join('\n'))
console.log('总计注释:', total)
