<script setup>
// 设计现场（改造自 Uiverse figma-workflow 动画）
// - Figma 式选择框 + 角点 + 光标移动/点击动画
// - 原版文字为矢量写死的 "UX FIGMA WORKFLOW DESIGN"（且烙有原作者签名），
//   这里改为 <text> 渲染站点关键词，便于配色与内容统一
// - 放在关于页「设计现场」区块
</script>

<template>
  <div class="figma-canvas" aria-hidden="true">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 614 390" class="figma-svg">
      <!-- 文案行 -->
      <text x="40" y="122" class="word">LINUX</text>
      <text x="40" y="212" class="word">NOTES</text>
      <text x="40" y="296" class="word word-site">~/bbben</text>

      <!-- Figma 式选择框 + 角点 -->
      <g id="box">
        <path stroke-width="2" stroke="#2563EB" fill-opacity="0.05" fill="#2563EB" d="M587 20H28V306H587V20Z"></path>
        <path stroke-width="2" stroke="#2563EB" fill="white" d="M33 15H23V25H33V15Z"></path>
        <path stroke-width="2" stroke="#2563EB" fill="white" d="M33 301H23V311H33V301Z"></path>
        <path stroke-width="2" stroke="#2563EB" fill="white" d="M592 301H582V311H592V301Z"></path>
        <path stroke-width="2" stroke="#2563EB" fill="white" d="M592 15H582V25H592V15Z"></path>
      </g>

      <!-- 光标（移动 → 选中 → 点击 → 划走） -->
      <g id="cursor">
        <path stroke-width="2" stroke="white" fill="#2563EB" d="M453.383 343L448 317L471 331L459.745 333.5L453.383 343Z"></path>
        <g id="tip">
          <rect x="469" y="341" width="96" height="34" rx="6" fill="#2563EB"></rect>
          <text x="481" y="363" class="tip-text">~/bbben</text>
        </g>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.figma-canvas {
  max-width: 580px;
  margin: 0 auto;
  border-radius: 14px;
  padding: 18px;
  background: linear-gradient(160deg, #232b41 0%, #171d2e 100%);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25), inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

.figma-svg {
  width: 100%;
  height: auto;
  display: block;
}

.word {
  font-family: 'Courier New', monospace;
  font-size: 78px;
  font-weight: 800;
  fill: #f9f9f9;
  letter-spacing: 2px;
}

.word-site {
  font-size: 68px;
  fill: #7eb1ff;
}

.tip-text {
  font-family: 'Courier New', monospace;
  font-size: 15px;
  font-weight: 700;
  fill: white;
}

#cursor,
#box {
  cursor: pointer;
}

#cursor {
  overflow: visible;
  transform: translate3d(300px, 0, 0) scale(1);
  transform-origin: center center;
  transform-box: fill-box;
  animation: cursor 5s ease infinite alternate;
}

@keyframes cursor {
  0% {
    opacity: 0;
    transform: translate3d(300px, 0, 0) scale(1);
  }
  30% {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
  }
  60% {
    opacity: 1;
    transform: translate3d(-200px, -200px, 0) scale(1);
  }

  /* clique */
  65% {
    opacity: 1;
    transform: translate3d(-200px, -200px, 0) scale(0.95);
  }
  70% {
    opacity: 1;
    transform: translate3d(-200px, -200px, 0) scale(1);
  }

  100% {
    opacity: 1;
    transform: translate3d(-300px, -50px, 0) scale(1);
  }
}

#box {
  opacity: 0;
  animation: box 5s ease infinite alternate;
}

@keyframes box {
  0%,
  60% {
    opacity: 0;
  }
  65%,
  100% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  #cursor, #box { animation: none; opacity: 1; transform: none; }
}
</style>
