<script setup>
// 折纸飞机加载动画（改造自 Uiverse loader 组件）
// 用法：<PlaneLoader :scale="0.6" />
// - 配色跟调色板（--vp-c-brand-1），不再写死红色
// - 典型用途：ClientOnly 的 #placeholder，组件挂载前占位
defineProps({
  scale: { type: Number, default: 1 },
})
</script>

<template>
  <div
    class="loader-wrap"
    :style="{ width: 200 * scale + 'px', height: 200 * scale + 'px' }"
  >
    <div class="loader" :style="{ transform: `scale(${scale})` }">
      <div class="pattern-1">
        <div class="pattern-1-shade"></div>
      </div>
      <div class="pattern-2"></div>
    </div>
  </div>
</template>

<style scoped>
.loader-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 1.5rem auto;
  overflow: visible;
}

.loader {
  position: relative;
  width: 200px;
  height: 200px;
  flex: none;
  transform-origin: center;
}

.loader .pattern-1 {
  position: absolute;
  background-color: var(--vp-c-brand-1);
  width: 200px;
  height: 200px;
  clip-path: polygon(0 10%, 70% 90%, 40% 90%, 0 45%);
  overflow: hidden;
}

.loader .pattern-2 {
  position: absolute;
  background-color: var(--vp-c-brand-1);
  width: 220px;
  height: 190px;
  clip-path: polygon(100% 10%, 100% 45%, 83% 65%, 55% 65%);
  opacity: 0.92;
}

.loader .pattern-1 .pattern-1-shade {
  position: absolute;
  transform: translateX(-20px);
  opacity: 0.7;
  z-index: 10;
  background-color: white;
  width: 20px;
  height: 200px;
  animation: shiny 1s infinite;
}

@keyframes shiny {
  0% { transform: translateX(-20px); }
  100% { transform: translateX(140px); }
}

@media (prefers-reduced-motion: reduce) {
  .loader .pattern-1 .pattern-1-shade {
    animation: none;
    opacity: 0;
  }
}
</style>
