// 建立 ./notes 到 ./docs/notes 的软链，让构建时能直接读到笔记。
// 仅首次或重命名 notes 目录时跑一次。
import { symlinkSync, existsSync, rmSync, lstatSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const target = resolve(__dirname, '../notes')
const link   = resolve(__dirname, '../docs/notes')

function rmIfExists(p) {
  if (!existsSync(p)) return
  const s = lstatSync(p)
  if (s.isSymbolicLink() || s.isFile()) rmSync(p, { force: true })
  else rmSync(p, { recursive: true, force: true })
}

rmIfExists(link)
symlinkSync(target, link, 'dir')
console.log(`✓ symlinked docs/notes -> ../notes`)