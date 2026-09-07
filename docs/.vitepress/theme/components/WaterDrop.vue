<script setup>
// 水滴（改造自 Uiverse 卡片液态效果）
// 不规则 border-radius 形成有机形状，两个半透明白色高光做出「水滴」感
// 接受 size prop，可放在页面任何位置
defineProps({
  size: { type: Number, default: 120 },
  hue: { type: String, default: '#a3c4f3' },  // 浅蓝
})
</script>

<template>
  <div
    class="drop"
    :style="{
      width: size + 'px',
      height: size + 'px',
      '--drop-hue': hue,
    }"
  ></div>
</template>

<style scoped>
.drop {
  position: relative;
  background-color: color-mix(in srgb, var(--drop-hue) 55%, white);
  box-shadow:
    inset calc(var(--size, 1)*8px) calc(var(--size, 1)*8px) calc(var(--size, 1)*8px) calc(var(--size, 1)*8px) rgba(0, 0, 0, 0.158),
    calc(var(--size, 1)*8px) calc(var(--size, 1)*8px) calc(var(--size, 1)*15px) rgba(0, 0, 0, 0.466),
    inset calc(var(--size, 1)*-8px) calc(var(--size, 1)*-8px) calc(var(--size, 1)*8px) calc(var(--size, 1)*8px) rgba(255, 255, 255, 0.9);
  border-radius: 51% 49% 62% 38% / 25% 57% 43% 75%;
  --size: v-bind('Math.max(size, 80) / 80');
}

.drop::after {
  content: "";
  position: absolute;
  top: 25%;
  left: 30%;
  width: 7%;
  height: 7%;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 80% 20% 91% 9% / 48% 67% 33% 52%;
}

.drop::before {
  content: "";
  position: absolute;
  top: 20%;
  left: 45%;
  width: 14%;
  height: 14%;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 48% 52% 45% 55% / 48% 67% 33% 52%;
}
</style>
