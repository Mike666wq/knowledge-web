<script setup>
// 纯 CSS 太阳：径向渐变球面 + 太阳黑子 + 辉光层 + 缓慢自转
// 之前用 base64 素材渲出来一团黑/橙，现在用纯色 + 阴影画出真正的「太阳」感
</script>

<template>
  <div class="sun-stage" aria-hidden="true">
    <div class="sun-glow"></div>
    <div class="sun-body">
      <div class="sun-spots">
        <div class="spot spot-1"></div>
        <div class="spot spot-2"></div>
        <div class="spot spot-3"></div>
        <div class="spot spot-4"></div>
        <div class="spot spot-5"></div>
      </div>
    </div>
    <div class="sun-star sun-star-1"></div>
    <div class="sun-star sun-star-2"></div>
    <div class="sun-star sun-star-3"></div>
    <div class="sun-star sun-star-4"></div>
    <div class="sun-star sun-star-5"></div>
    <div class="sun-star sun-star-6"></div>
    <div class="sun-star sun-star-7"></div>
  </div>
</template>

<style scoped>
.sun-stage {
  position: relative;
  width: 300px;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 太阳本体：径向渐变 + 多层 inset 阴影做出球面层次 + 缓慢自转 */
.sun-body {
  position: relative;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 35% 35%, #fff8c4 0%, #ffd23f 18%, #ff9a3c 45%, #f4741e 72%, #c43e0e 100%);
  box-shadow:
    inset -10px -10px 30px rgba(196, 62, 14, 0.65),
    inset 8px 8px 25px rgba(255, 248, 196, 0.5);
  animation: sun-spin 30s linear infinite;
}

@keyframes sun-spin {
  to { transform: rotate(360deg); }
}

/* 太阳黑子：在本体里转 */
.sun-spots {
  position: absolute;
  inset: 0;
  animation: sun-spin 30s linear infinite;
}
.spot {
  position: absolute;
  background: rgba(160, 50, 10, 0.45);
  border-radius: 50%;
  box-shadow: inset 0 0 3px rgba(0, 0, 0, 0.3);
}
.spot-1 { top: 30%;  left: 20%;  width: 18px; height: 14px; }
.spot-2 { top: 55%;  left: 55%;  width: 12px; height: 10px; }
.spot-3 { top: 40%;  left: 70%;  width: 16px; height: 12px; }
.spot-4 { top: 70%;  left: 35%;  width: 10px; height: 10px; }
.spot-5 { top: 25%;  left: 50%;  width: 8px;  height: 8px;  }

/* 辉光：本体外圈橙色光晕，会呼吸 */
.sun-glow {
  position: absolute;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  background: radial-gradient(circle, transparent 55%, rgba(255, 170, 60, 0.4) 65%, transparent 80%);
  filter: blur(6px);
  animation: sun-pulse 4s ease-in-out infinite;
  pointer-events: none;
}
@keyframes sun-pulse {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.08); opacity: 1; }
}

/* 周围的闪烁小星（用 box-shadow 画十字小光点） */
.sun-star {
  position: absolute;
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  box-shadow:
    0 0 4px white,
    -5px 0 6px -1px white,
    5px 0 6px -1px white,
    0 -5px 6px -1px white,
    0 5px 6px -1px white;
  animation: star-twinkle 2.5s ease-in-out infinite;
}
.sun-star-1 { top: 10px;  left: 40px;  animation-delay: 0s; }
.sun-star-2 { top: 30px;  right: 60px; animation-delay: 0.4s; }
.sun-star-3 { top: 120px; left: 5px;   animation-delay: 0.8s; }
.sun-star-4 { bottom: 30px; right: 20px; animation-delay: 1.2s; }
.sun-star-5 { bottom: 10px; left: 120px; animation-delay: 1.6s; }
.sun-star-6 { top: 80px; right: 5px;   animation-delay: 2.0s; }
.sun-star-7 { bottom: 80px; left: 60px; animation-delay: 2.4s; }
@keyframes star-twinkle {
  0%, 100% { opacity: 0.3; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.2); }
}
</style>
