<script setup>
// 3D 旋转立方体（改造自 Uiverse cube loader）
// 放在服务器插画下方，组成左列装饰组合；纯装饰不挡点击
</script>

<template>
  <div class="cube-strip" aria-hidden="true">
    <div class="loader-container">
      <div class="loader-cube">
        <div class="loader-side front"></div>
        <div class="loader-side back"></div>
        <div class="loader-side left"></div>
        <div class="loader-side right"></div>
        <div class="loader-side top"></div>
        <div class="loader-side bottom"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 文档流中居中显示（曾是固定在侧栏的小转轮，现搬到页面里） */
.cube-strip {
  display: flex;
  justify-content: center;
  margin: 0 auto;
  width: 128px;
  pointer-events: none;
}

.loader-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 10em;
  perspective: 800px;
}

.loader-cube {
  position: relative;
  width: 5em;
  height: 5em;
  transform-style: preserve-3d;
  animation: cube-rotate 2s infinite linear;
}

.loader-side {
  position: absolute;
  width: 5em;
  height: 5em;
  background: #333;
  border: 0.1em solid #fff;
}

.front { transform: translateZ(2.5em); }
.back { transform: rotateY(180deg) translateZ(2.5em); }
.right { transform: rotateY(90deg) translateZ(2.5em); }
.left { transform: rotateY(-90deg) translateZ(2.5em); }
.top { transform: rotateX(90deg) translateZ(2.5em); }
.bottom { transform: rotateX(-90deg) translateZ(2.5em); }

@keyframes cube-rotate {
  from { transform: rotateX(0deg) rotateY(0deg); }
  to { transform: rotateX(360deg) rotateY(360deg); }
}

.loader-side:hover {
  background: #555;
}

/* 暗色模式：立方体稍微提亮 */
html.dark .loader-side {
  background: #3d3d47;
  border-color: rgba(255, 255, 255, 0.85);
}
html.dark .loader-side:hover { background: #4d4d5a; }

@media (max-width: 959px) {
  .cube-strip { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .loader-cube { animation: none; }
}
</style>