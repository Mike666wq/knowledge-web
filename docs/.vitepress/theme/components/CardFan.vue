<script setup>
// 卡片扇（改造自 Uiverse cards fan）：hover 时 7 张卡向两侧扇形展开
// 放在 /fun 实验室当快捷方式展
const cards = [
  { icon: '🐼', label: '熊猫', color: '#fef3c7' },
  { icon: '🎵', label: '音乐', color: '#fce7f3' },
  { icon: '🎨', label: '主题', color: '#dbeafe' },
  { icon: '⌨️', label: '键盘', color: '#e0e7ff' },
  { icon: '📺', label: '电视', color: '#d1fae5' },
  { icon: '☯️', label: '太极', color: '#fee2e2' },
  { icon: '🎨', label: 'Figma', color: '#ede9fe' },
]
</script>

<template>
  <div class="fan-stage" aria-label="hover 展开 7 张快捷卡">
    <div class="fan-container">
      <div
        v-for="(c, i) in cards"
        :key="i"
        class="fan-card"
        :style="{ background: c.color }"
      >
        <div class="fan-icon">{{ c.icon }}</div>
        <div class="fan-label">{{ c.label }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fan-stage {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem 0;
}

.fan-container {
  position: relative;
  width: 240px;
  height: 220px;
}

.fan-card {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 132px;
  height: 196px;
  margin-top: -98px;
  margin-left: -66px;
  background: #ebebeb;
  border: 5px solid #fff;
  border-bottom-width: 40px;
  border-radius: 8%;
  box-shadow: #c7c7c7 -2px 2px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #1f2937;
  transform: rotate(0deg) translate(0, -8px);
  transform-origin: bottom left;
  transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

/* 默认堆在中央，鼠标进入时每张旋转 +54° 到 -54°（步进 18°） */
.fan-container .fan-card:nth-child(1) { transform: rotate(  0deg) translate(0, -8px); }
.fan-container .fan-card:nth-child(2) { transform: rotate(  0deg) translate(0, -8px); }
.fan-container .fan-card:nth-child(3) { transform: rotate(  0deg) translate(0, -8px); }
.fan-container .fan-card:nth-child(4) { transform: rotate(  0deg) translate(0, -8px); }
.fan-container .fan-card:nth-child(5) { transform: rotate(  0deg) translate(0, -8px); }
.fan-container .fan-card:nth-child(6) { transform: rotate(  0deg) translate(0, -8px); }
.fan-container .fan-card:nth-child(7) { transform: rotate(  0deg) translate(0, -8px); }

.fan-container:hover .fan-card:nth-child(1) { transform: rotate(-54deg) translate(0, -8px); }
.fan-container:hover .fan-card:nth-child(2) { transform: rotate(-36deg) translate(0, -8px); }
.fan-container:hover .fan-card:nth-child(3) { transform: rotate(-18deg) translate(0, -8px); }
.fan-container:hover .fan-card:nth-child(4) { transform: rotate(  0deg) translate(0, -8px); }
.fan-container:hover .fan-card:nth-child(5) { transform: rotate( 18deg) translate(0, -8px); }
.fan-container:hover .fan-card:nth-child(6) { transform: rotate( 36deg) translate(0, -8px); }
.fan-container:hover .fan-card:nth-child(7) { transform: rotate( 54deg) translate(0, -8px); }

.fan-card:hover {
  /* 单卡悬停：略放大让它浮出 */
  z-index: 5;
  box-shadow: #a3a3a3 -4px 6px 12px;
}

.fan-icon {
  font-size: 2rem;
  line-height: 1;
  margin-bottom: 6px;
}
.fan-label {
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #1f2937;
}
</style>
