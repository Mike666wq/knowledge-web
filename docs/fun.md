---
sidebar: true
aside: false
---

# ~/fun

> 实验区：一些好玩的组件都丢在这里，随便点点 ✨

## 设计现场

<ClientOnly>
  <FigmaFlow />
</ClientOnly>

<p class="fun-caption">正在设计本站的第 108 版草图 🎨（其实已经是最终版了）</p>

## 终端模拟器

<ClientOnly>
  <Terminal />
</ClientOnly>

<p class="fun-caption">试试 <code>help</code> / <code>ls</code> / <code>neofetch</code> / <code>whoami</code>，或者随便输点什么，它都会一本正经地回答你</p>

## 黑胶唱片播放器

<ClientOnly>
  <MusicPlayer />
</ClientOnly>

<p class="fun-caption">和手机里那台用同一份歌单（扫的是 <code>public/music/</code>），轻点中央开始播放 🎵</p>

## 3D 旋转立方

<ClientOnly>
  <CubeGrid />
</ClientOnly>

<p class="fun-caption">像素方块阵 · 鼠标碰到的方块会亮起主题色（跟调色盘走）🎨</p>

## 实时键盘

<ClientOnly>
  <KeyboardView />
</ClientOnly>

<p class="fun-caption">在页面任意位置敲键盘，按什么亮什么 ✨</p>

## 复古电视（错误信息轮播器）

<ClientOnly>
  <RetroTV />
</ClientOnly>

<p class="fun-caption">屏幕里的错误信息 4 秒自动换一条，点电视也能切 📺</p>

## iOS 设置面板

<ClientOnly>
  <IosSettings />
</ClientOnly>

<p class="fun-caption">Wi-Fi / Cellular / Battery / Privacy 点击看状态，Bluetooth / Display / Sounds / Notifications 真能拨 ⚙️</p>

## 卡片扇（hover 展开 7 张快捷方式）

<ClientOnly>
  <CardFan />
</ClientOnly>

<p class="fun-caption">鼠标移过去，七张卡往两边散开（熊猫 / 音乐 / 主题 / 键盘 / 电视 / 太极 / Figma）🃏</p>

## 定价卡 · $24/mo（Starter Pack）

<ClientOnly>
  <PriceCardA />
</ClientOnly>

<p class="fun-caption">Uiverse 暗色套餐卡 · 含 Buy Now 按钮 💳</p>

## 定价卡 · $251/mo（黑色圆角 + 6 条特性）

<ClientOnly>
  <PriceCardB />
</ClientOnly>

<p class="fun-caption">Get started 按钮 hover 反色 · 完整 6 条勾选清单 ✅</p>

## 霓虹绿卡（Viper 风格）

<ClientOnly>
  <ViperCard />
</ClientOnly>

<p class="fun-caption">呼吸绿光 + 滚动 viper 文字 + 六边形 logo · hover 整张卡轻微 3D 旋转 🐍</p>

## 红色卡牌（hover 展开 4 张叠加）

<ClientOnly>
  <RedCardDeck />
</ClientOnly>

<p class="fun-caption">hover 任一张 → 切角打开、显示标题、底部 3 个按钮依次升起 🃏</p>

<style>
.fun-caption {
  text-align: center;
  color: var(--vp-c-text-3);
  font-size: 0.85rem;
  margin: 0.8rem 0 2rem;
}

.planet-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  padding: 0.5rem 0 0.5rem;
}
</style>
