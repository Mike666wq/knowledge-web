// 抓带代码块的页面，提取真实 CSS
import { chromium } from 'playwright'
import { writeFileSync } from 'node:fs'

const browser = await chromium.launch({ args: ['--no-sandbox'] })
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
const page = await ctx.newPage()

// 抓 reactbits 的 installation 页（有代码块）
console.log('=== reactbits.dev 安装页 ===')
await page.goto('https://www.reactbits.dev/get-started/installation', { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3000)
await page.screenshot({ path: '/srv/knowledge-web/research-reactbits-code.png', fullPage: false })

// 抓代码块样式
const reactbitsCode = await page.evaluate(() => {
  const pres = document.querySelectorAll('pre')
  const samples = []
  for (let i = 0; i < Math.min(3, pres.length); i++) {
    const pre = pres[i]
    const cs = getComputedStyle(pre)
    samples.push({
      outerHTML: pre.outerHTML.slice(0, 400),
      background: cs.backgroundColor,
      color: cs.color,
      fontFamily: cs.fontFamily,
      fontSize: cs.fontSize,
      lineHeight: cs.lineHeight,
      padding: cs.padding,
      borderRadius: cs.borderRadius,
      border: cs.border,
      boxShadow: cs.boxShadow
    })
  }
  return samples
})
console.log('reactbits pre blocks:', JSON.stringify(reactbitsCode, null, 2))

// 找有 "code" 类的所有元素
const reactbitsInline = await page.evaluate(() => {
  const codes = document.querySelectorAll('code')
  if (codes.length === 0) return null
  const cs = getComputedStyle(codes[0])
  return {
    outerHTML: codes[0].outerHTML.slice(0, 300),
    background: cs.backgroundColor,
    color: cs.color,
    fontFamily: cs.fontFamily.slice(0, 100),
    fontSize: cs.fontSize,
    padding: cs.padding,
    borderRadius: cs.borderRadius
  }
})
console.log('reactbits inline code:', JSON.stringify(reactbitsInline, null, 2))

// === VitePress 默认代码块样式对比 ===
console.log('\n=== 自家笔记页代码块（对比参考）===')
await page.goto('http://127.0.0.1:4199/notes/Linux/02.Linux基础命令.html', { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(2500)

const ourCode = await page.evaluate(() => {
  const pres = document.querySelectorAll('pre, .shiki, div[class*="language-"]')
  if (pres.length === 0) return null
  const el = pres[0]
  const cs = getComputedStyle(el)
  return {
    tag: el.tagName,
    class: el.className.slice(0, 100),
    background: cs.backgroundColor,
    color: cs.color,
    fontFamily: cs.fontFamily.slice(0, 80),
    fontSize: cs.fontSize,
    padding: cs.padding,
    borderRadius: cs.borderRadius,
    border: cs.border,
    boxShadow: cs.boxShadow,
    width: cs.width,
    height: cs.height
  }
})
console.log('Our code block:', JSON.stringify(ourCode, null, 2))

// === Apple Developer 抓代码块样式（最权威的 Apple 风格）===
console.log('\n=== Apple Developer SwiftUI 代码块 ===')
try {
  await page.goto('https://developer.apple.com/documentation/swiftui/view', { waitUntil: 'domcontentloaded', timeout: 25000 })
  await page.waitForTimeout(2500)
  await page.screenshot({ path: '/srv/knowledge-web/research-apple-code.png', fullPage: false })

  const appleCode = await page.evaluate(() => {
    // Apple 用 figure.code-listing
    const blocks = document.querySelectorAll('pre, code, .code-listing')
    const results = {}
    blocks.forEach((el, i) => {
      if (i > 2) return
      const cs = getComputedStyle(el)
      results[el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ')[0] : '')] = {
        background: cs.backgroundColor,
        color: cs.color,
        fontFamily: cs.fontFamily.slice(0, 80),
        fontSize: cs.fontSize,
        lineHeight: cs.lineHeight,
        padding: cs.padding,
        borderRadius: cs.borderRadius,
        border: cs.border
      }
    })
    return results
  })
  console.log('Apple code:', JSON.stringify(appleCode, null, 2))
} catch (e) {
  console.log('Apple Developer 抓取失败:', e.message)
}

await browser.close()
console.log('\n✅ 完成')