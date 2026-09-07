// 修复 notes/ 里被 Vue 当成标签解析的裸 <占位符>
// 策略：只处理扫描出的 文件:行号；行内反引号代码段不动；<ident> → &lt;ident&gt;
import { readFileSync, writeFileSync } from 'fs'

const ROOT = '/srv/knowledge-web/notes'

// scan-tags.mjs 输出的清单
const targets = String(process.argv[2] ? readFileSync(process.argv[2], 'utf8') : '').split('\n').filter(Boolean)
const byFile = new Map()
for (const t of targets) {
  const m = t.match(/^(.+?):(\d+):/)
  if (!m) continue
  const file = ROOT + '/' + m[1]
  if (!byFile.has(file)) byFile.set(file, new Set())
  byFile.get(file).add(+m[2])
}

let fixed = 0
for (const [file, lineSet] of byFile) {
  const lines = readFileSync(file, 'utf8').split('\n')
  for (const ln of lineSet) {
    const parts = lines[ln - 1].split('`')
    // 偶数段 = 反引号外
    for (let i = 0; i < parts.length; i += 2) {
      const before = parts[i]
      parts[i] = before.replace(/<([a-zA-Z][a-zA-Z0-9_-]*)>/g, '&lt;$1&gt;')
      if (parts[i] !== before) fixed++
    }
    lines[ln - 1] = parts.join('`')
  }
  writeFileSync(file, lines.join('\n'))
  console.log('fixed:', file.replace(ROOT + '/', ''), [...lineSet].join(','))
}
console.log('total lines fixed:', fixed)
