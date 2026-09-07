<script setup>
// 星空背景：三层视差滚动的星星（1px/2px/3px，50s/100s/150s 速度差）
// 用固定种子的伪随机数生成 box-shadow 星点：
//  - SSR 和客户端结果一致（不会 hydration 报错）
//  - 星点随机铺满 2000x2000 画布，::after 复制一份实现无缝循环
//  - 只在暗色模式渲染（html.dark），浅色模式完全移除，零开销
function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

// count 颗星，亮度 0.35 ~ 1 随机，部分带一点蓝调
function makeStars(count, seed) {
  const rand = mulberry32(seed)
  const arr = []
  for (let i = 0; i < count; i++) {
    const x = Math.floor(rand() * 2000)
    const y = Math.floor(rand() * 2000)
    const a = (0.35 + rand() * 0.65).toFixed(2)
    const tint = rand()
    const c = tint > 0.82 ? '173,216,255' : '255,255,255' // 少量蓝星星
    arr.push(`${x}px ${y}px rgba(${c},${a})`)
  }
  return arr.join(',')
}

const layer1 = makeStars(420, 20240601) // 小星星
const layer2 = makeStars(180, 20240602) // 中星星
const layer3 = makeStars(90, 20240603)  // 大星星
</script>

<template>
  <div class="star-field" aria-hidden="true">
    <i class="s1" :style="{ boxShadow: layer1 }"></i>
    <i class="s2" :style="{ boxShadow: layer2 }"></i>
    <i class="s3" :style="{ boxShadow: layer3 }"></i>
  </div>
</template>

<style scoped>
.star-field {
  position: fixed;
  inset: 0;
  z-index: -1;          /* 画布背景(品牌色调)之上、所有内容之下 */
  overflow: hidden;
  pointer-events: none; /* 永不挡点击 */
}
/* 浅色模式彻底不渲染。
   注意：实测全屏尺寸的空透明层也会让 Chromium 把全站文字
   从亚像素抗锯齿切成灰度抗锯齿（文字边缘变糊），
   所以必须 display:none 移除，而不是 opacity:0 隐藏。 */
html:not(.dark) .star-field { display: none; }

.star-field i {
  position: absolute;
  top: 0;
  left: 0;
  width: 1px;
  height: 1px;
  border-radius: 50%;
  background: transparent;
  animation: sf-move 50s linear infinite;
}
/* 复制同一片星空往下接 2000px，滚动到头无缝衔接 */
.star-field i::after {
  content: "";
  position: absolute;
  top: 2000px;
  width: inherit;
  height: inherit;
  border-radius: inherit;
  background: inherit;
  box-shadow: inherit;
}
.star-field .s2 { width: 2px; height: 2px; animation-duration: 100s; opacity: 0.9; }
.star-field .s3 { width: 3px; height: 3px; animation-duration: 150s; opacity: 0.85; }

@keyframes sf-move {
  from { transform: translateY(0); }
  to   { transform: translateY(-2000px); }
}

@media (prefers-reduced-motion: reduce) {
  .star-field i { animation: none; }
}
</style>
