// 生成占位资源：壁纸(渐变图) + 测试音频(440Hz 正弦波 WAV)
import { chromium } from 'playwright'
import { writeFileSync } from 'node:fs'

// 1) 壁纸：截一张 360x720 的渐变图
const browser = await chromium.launch({ args: ['--no-sandbox'] })
const page = await (await browser.newContext({ viewport: { width: 360, height: 720 } })).newPage()
await page.setContent(`<body style="margin:0"><div style="width:360px;height:720px;background:
  radial-gradient(circle at 30% 20%, #4c1d95 0%, transparent 50%),
  radial-gradient(circle at 80% 70%, #0e7490 0%, transparent 55%),
  linear-gradient(160deg, #0f172a 0%, #1e1b4b 60%, #020617 100%)"></div></body>`)
await page.screenshot({ path: '/srv/knowledge-web/docs/public/wallpaper.png' })
await browser.close()
console.log('wallpaper.png 生成 ✓')

// 2) 音乐：2 秒 440Hz 正弦波 WAV（占位用，之后换成你自己的 mp3 也行）
const sampleRate = 22050
const seconds = 3
const n = sampleRate * seconds
const data = Buffer.alloc(n * 2)
for (let i = 0; i < n; i++) {
  const t = i / sampleRate
  // 一个简单的双音旋律感：440+660 混合，带淡入淡出
  const env = Math.min(1, i / 2000, (n - i) / 4000)
  const v = Math.sin(2 * Math.PI * 440 * t) * 0.5 + Math.sin(2 * Math.PI * 660 * t) * 0.3
  data.writeInt16LE(Math.round(v * env * 22000), i * 2)
}
const header = Buffer.alloc(44)
header.write('RIFF', 0)
header.writeUInt32LE(36 + data.length, 4)
header.write('WAVE', 8)
header.write('fmt ', 12)
header.writeUInt32LE(16, 16)
header.writeUInt16LE(1, 20)  // PCM
header.writeUInt16LE(1, 22)  // mono
header.writeUInt32LE(sampleRate, 24)
header.writeUInt32LE(sampleRate * 2, 28)
header.writeUInt16LE(2, 32)
header.writeUInt16LE(16, 34)
header.write('data', 36)
header.writeUInt32LE(data.length, 40)
writeFileSync('/srv/knowledge-web/docs/public/music.wav', Buffer.concat([header, data]))
console.log('music.wav 生成 ✓ (3秒 440Hz，替换成自己的 mp3 即可)')
