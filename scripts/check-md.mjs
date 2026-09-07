// 检查笔记里有没有代码块外的 {{ 或 {%，避免 build 时被 Vue 当成插值
import { readdirSync, statSync, readFileSync } from 'node:fs'
import { resolve, join } from 'node:path'

const NOTES_ROOT = resolve(process.cwd(), 'notes')
const SKIP = new Set(['.venv', 'node_modules', '.git', 'dist', 'cache'])

let problems = 0

function walk(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) {
      if (SKIP.has(e.name)) continue
      walk(join(dir, e.name))
    } else if (e.isFile() && e.name.endsWith('.md')) {
      check(join(dir, e.name))
    }
  }
}

function check(path) {
  const content = readFileSync(path, 'utf-8')
  const lines = content.split('\n')
  let inCode = false
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.trim().startsWith('```')) { inCode = !inCode; continue }
    if (!inCode && (line.includes('{{') || line.includes('{%'))) {
      console.error(`❌ ${path}:${i+1}: ${line.trim().slice(0, 80)}`)
      problems++
    }
  }
}

walk(NOTES_ROOT)
if (problems === 0) {
  console.log('✅ 笔记检查通过：没有代码块外的 {{ 或 {%')
} else {
  console.error(`\n发现 ${problems} 处问题。修复方法：把 {{ 替换为 &#123;&#123;，把 {% 替换为 &#123;%`)
  process.exit(1)
}
