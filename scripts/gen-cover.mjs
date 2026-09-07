import { chromium } from 'playwright'
const browser = await chromium.launch({ args: ['--no-sandbox'] })
const page = await (await browser.newContext({ viewport: { width: 96, height: 96 } })).newPage()
await page.setContent(`<body style="margin:0"><div style="width:96px;height:96px;position:relative;overflow:hidden;background:
  conic-gradient(from 210deg at 60% 40%, #f472b6, #a855f7, #3b82f6, #22d3ee, #f472b6)">
  <div style="position:absolute;inset:0;background:radial-gradient(circle at 32% 30%, rgba(255,255,255,.85) 0%, transparent 28%)"></div>
  <div style="position:absolute;left:50%;top:50%;width:46px;height:46px;border-radius:50%;transform:translate(-50%,-50%);
    background:#0b0b12;display:flex;align-items:center;justify-content:center">
    <div style="width:10px;height:10px;border-radius:50%;background:#f472b6"></div>
  </div>
  <div style="position:absolute;bottom:5px;left:0;right:0;text-align:center;color:#fff;font:700 11px/1 sans-serif;letter-spacing:2px">BBBEN</div>
</div></body>`)
await page.screenshot({ path: '/srv/knowledge-web/docs/public/cover.png' })
await browser.close()
console.log('cover.png 生成 ✓ (96x96，换成自己的封面图即可)')
