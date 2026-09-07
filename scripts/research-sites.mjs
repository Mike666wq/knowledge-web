// 抓取 3 个 UI 参考网站的真实设计
import { chromium } from 'playwright'
import { writeFileSync } from 'node:fs'

const browser = await chromium.launch({ args: ['--no-sandbox'] })
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
})
const page = await ctx.newPage()

const results = []

async function inspectSite(url, name, key) {
  console.log(`\n========== ${name} ==========`)
  console.log(`URL: ${url}`)

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 })
  } catch (e) {
    console.log(`⚠ goto error: ${e.message.slice(0, 100)}`)
  }

  // 等渲染
  await page.waitForTimeout(3000)

  // 1. 截图首页
  await page.screenshot({ path: `/srv/knowledge-web/research-${key}.png`, fullPage: false })
  console.log(`📸 截图已保存 research-${key}.png`)

  // 2. 抓基础样式
  const baseStyles = await page.evaluate(() => {
    const root = document.documentElement
    const cs = getComputedStyle(document.body)
    return {
      bodyFont: cs.fontFamily,
      bodyFontSize: cs.fontSize,
      bodyLineHeight: cs.lineHeight,
      bodyBg: cs.backgroundColor,
      bodyColor: cs.color,
      docHeight: document.documentElement.scrollHeight,
      docWidth: document.documentElement.scrollWidth
    }
  })
  console.log(`字体: ${baseStyles.bodyFont}`)
  console.log(`字号: ${baseStyles.bodyFontSize}, 行高: ${baseStyles.bodyLineHeight}`)
  console.log(`背景: ${baseStyles.bodyBg}, 文字: ${baseStyles.bodyColor}`)

  // 3. 抓 CSS 变量
  const cssVars = await page.evaluate(() => {
    const root = document.documentElement
    const cs = getComputedStyle(root)
    const vars = {}
    const important = ['--bg-primary','--bg-secondary','--text-primary','--text-secondary','--accent','--accent-secondary','--border','--card-bg','--card-shadow','--radius','--font-sans','--font-mono','--font-display']
    for (const v of important) {
      const val = cs.getPropertyValue(v).trim()
      if (val) vars[v] = val
    }
    // 遍历所有 CSS 自定义属性（取前 40 个）
    const allProps = []
    for (const sheet of document.styleSheets) {
      try {
        for (const rule of sheet.cssRules) {
          if (rule.style) {
            for (const prop of rule.style) {
              if (prop.startsWith('--')) allProps.push(`${prop}: ${rule.style.getPropertyValue(prop).trim()}`)
            }
          }
        }
      } catch (e) { /* CORS */ }
    }
    return { named: vars, all: [...new Set(allProps)].slice(0, 50) }
  })
  console.log(`CSS 变量（关键）: ${JSON.stringify(cssVars.named)}`)

  // 4. 抓所有可能的代码块 / pre / card / button 元素的实际样式
  const elements = await page.evaluate(() => {
    const out = {}
    const selectors = ['pre', 'code', 'article', 'main', '[class*="card"]', '[class*="Card"]', '[class*="button"]', '[class*="Button"]', 'h1', 'h2', 'h3', 'p', 'a']
    for (const sel of selectors) {
      try {
        const els = document.querySelectorAll(sel)
        if (els.length === 0) continue
        const sample = els[0]
        const cs = getComputedStyle(sample)
        out[sel] = {
          count: els.length,
          fontSize: cs.fontSize,
          fontWeight: cs.fontWeight,
          fontFamily: cs.fontFamily.slice(0, 80),
          color: cs.color,
          background: cs.backgroundColor,
          padding: cs.padding,
          borderRadius: cs.borderRadius,
          border: cs.border,
          boxShadow: cs.boxShadow.slice(0, 100)
        }
      } catch (e) {}
    }
    return out
  })
  console.log(`元素样式:`, JSON.stringify(elements, null, 2))

  // 5. 抓整个页面的 HTML（前 3000 字符）
  const html = await page.content()
  writeFileSync(`/srv/knowledge-web/research-${key}.html`, html)
  console.log(`HTML 已保存 research-${key}.html (${html.length} 字符)`)

  results.push({ name, url, baseStyles, cssVars, elements })
  return results[results.length - 1]
}

// ===== 1. reactbits.dev =====
await inspectSite('https://www.reactbits.dev/get-started/index', 'reactbits.dev', 'reactbits')

// ===== 2. uiverse.io =====
await inspectSite('https://uiverse.io/', 'uiverse.io', 'uiverse')

// ===== 3. showreel.design =====
await inspectSite('https://showreel.design/', 'showreel.design', 'showreel')

// 保存完整报告
writeFileSync('/srv/knowledge-web/research-data.json', JSON.stringify(results, null, 2))
console.log('\n✅ 全部完成，结果已保存到 research-data.json')

await browser.close()