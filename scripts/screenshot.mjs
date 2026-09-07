// 用 playwright 实际渲染首页并截图
import { chromium } from 'playwright'
import { createServer } from 'node:http'
import { readFileSync, existsSync, statSync } from 'node:fs'
import { resolve, join, extname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { dirname } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const DIST = resolve(__dirname, '../docs/.vitepress/dist')
const PORT = 4200

if (!existsSync(DIST)) {
  console.error('dist 不存在，请先 npm run build')
  process.exit(1)
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.svg':  'image/svg+xml',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif'
}

const server = createServer((req, res) => {
  let url = decodeURIComponent(req.url.split('?')[0])
  if (url.endsWith('/')) url += 'index.html'
  for (const p of [join(DIST, url), join(DIST, url + '.html'), join(DIST, url, 'index.html')]) {
    if (existsSync(p) && statSync(p).isFile()) {
      const ext = extname(p).toLowerCase()
      res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' })
      res.end(readFileSync(p))
      return
    }
  }
  res.writeHead(404).end('not found')
})

await new Promise(r => server.listen(PORT, r))
console.log(`server on http://127.0.0.1:${PORT}/`)

const browser = await chromium.launch({
  args: ['--no-sandbox', '--disable-setuid-sandbox']
})
const ctx = await browser.newContext({ viewport: { width: 1407, height: 842 } })
const page = await ctx.newPage()

// 抓 console 和 page error
page.on('console', msg => console.log(`[browser console ${msg.type()}]`, msg.text().slice(0, 200)))
page.on('pageerror', err => console.log(`[page error]`, err.message))

await page.goto(`http://127.0.0.1:4200/`, { waitUntil: 'domcontentloaded' })

// 等 3 秒让 NotesTree 渲染
await page.waitForTimeout(2000)

// 清 localStorage 让主题回到默认（浅色）
await page.evaluate(() => {
  try { localStorage.removeItem('vitepress-theme-appearance') } catch {}
})
await page.goto(`http://127.0.0.1:4200/`, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(2000)

// 截图 1：浅色首页
await page.screenshot({ path: resolve(__dirname, '../test-screenshot.png'), fullPage: false })
console.log('截图1（首页 - 浅色）已保存到 test-screenshot.png')

// 点击安全分组标题展开
const groupHeader = page.locator('.group-header').first()
if (await groupHeader.count() > 0) {
  await groupHeader.click()
  await page.waitForTimeout(400)
  await page.screenshot({ path: resolve(__dirname, '../test-expanded.png'), fullPage: false })
  console.log('截图2（首页展开）已保存到 test-expanded.png')
}

// 切到暗色主题（点击暗色主题按钮）
const darkBtn = page.locator('button.VPSwitchAppearance')
if (await darkBtn.count() > 0) {
  await darkBtn.first().click()
  await page.waitForTimeout(500)
  await page.screenshot({ path: resolve(__dirname, '../test-dark.png'), fullPage: false })
  console.log('截图3（暗色）已保存到 test-dark.png')

  // 直接 goto 笔记页（手动清 localStorage 让默认折叠状态不干扰）
  await darkBtn.first().click() // 切回浅色
  await page.waitForTimeout(300)
  await page.goto(`http://127.0.0.1:4200/notes/Linux/02.Linux基础命令.html`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(2000)
  await page.screenshot({ path: resolve(__dirname, '../test-note.png'), fullPage: false })
  console.log('截图4（笔记页+代码块）已保存到 test-note.png')
}

// 检查 NotesTree 是否真的渲染了
const treeInfo = await page.evaluate(() => {
  // 找 "全部笔记" 区域
  const h2s = [...document.querySelectorAll('h2')]
  const allNotesH2 = h2s.find(h => h.textContent.includes('全部笔记'))
  if (!allNotesH2) return { error: '找不到"全部笔记"标题' }

  // 找它后面的兄弟节点
  const next = allNotesH2.nextElementSibling
  return {
    h2Found: true,
    h2NextTag: next ? next.tagName : 'none',
    h2NextClass: next ? next.className : '',
    h2NextInnerHTML: next ? next.innerHTML.slice(0, 500) : '',
    h2NextText: next ? next.textContent.slice(0, 200) : '',
    h2NextChildren: next ? next.children.length : 0
  }
})
console.log('\n=== NotesTree 渲染检查 ===')
console.log(JSON.stringify(treeInfo, null, 2))

// 检查图标
const iconInfo = await page.evaluate(() => {
  const sun = document.querySelector('.vpi-sun')
  const gh = document.querySelector('.vpi-social-github')
  return {
    sun: sun ? {
      w: sun.offsetWidth, h: sun.offsetHeight,
      bg: getComputedStyle(sun).backgroundColor,
      mask: getComputedStyle(sun).mask || getComputedStyle(sun).webkitMask,
      iconVar: getComputedStyle(sun).getPropertyValue('--icon').slice(0, 50)
    } : 'not found',
    github: gh ? {
      w: gh.offsetWidth, h: gh.offsetHeight,
      bg: getComputedStyle(gh).backgroundColor,
      mask: getComputedStyle(gh).mask || getComputedStyle(gh).webkitMask,
      iconVar: getComputedStyle(gh).getPropertyValue('--icon').slice(0, 50)
    } : 'not found'
  }
})
console.log('\n=== 图标渲染检查 ===')
console.log(JSON.stringify(iconInfo, null, 2))

await browser.close()
server.close()
console.log('done')