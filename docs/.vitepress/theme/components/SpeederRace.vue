<script setup>
// 双骑手赛车条（改造自 Uiverse speeder loader 黑白/彩色双版本）
// 放在笔记页底部（doc-bottom 插槽）：青色骑手(左,朝右) 与 橙色骑手(右,朝左) 面对面疾驰
// - 背景云从右往左飘、长速度线横掠，营造对冲的速度感
// - 配色：青 vs 橙互补对冲（custom.css 的 --race-* 变量，深色模式自动提亮）
</script>

<template>
  <div class="race-strip" aria-hidden="true">
    <!-- 云层背景 -->
    <div class="clouds">
      <div class="cloud cloud1"></div>
      <div class="cloud cloud2"></div>
      <div class="cloud cloud3"></div>
      <div class="cloud cloud4"></div>
      <div class="cloud cloud5"></div>
    </div>

    <!-- 长速度线（横掠全场） -->
    <div class="longfazers">
      <span></span><span></span><span></span><span></span>
    </div>

    <!-- 左骑手：青色，朝右 -->
    <div class="racer racer-left">
      <div class="loader">
        <span><span></span><span></span><span></span><span></span></span>
        <div class="base">
          <span></span>
          <div class="face"></div>
        </div>
      </div>
    </div>

    <!-- 右骑手：橙色，镜像朝左 -->
    <div class="racer racer-b">
      <div class="loader">
        <span><span></span><span></span><span></span><span></span></span>
        <div class="base">
          <span></span>
          <div class="face"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 赛车道条：全宽出血（撑出 doc 容器） */
.race-strip {
  position: relative;
  left: 50%;
  margin-left: -50vw;
  width: 100vw;
  height: 150px;
  overflow: hidden;
  pointer-events: none;
}

/* ===== 云层 ===== */
.clouds {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
.cloud {
  position: absolute;
  background: #cdd8ea;
  border-radius: 50%;
  opacity: 0.5;
  animation: spd-move-clouds linear infinite;
}
.cloud::before,
.cloud::after {
  content: "";
  position: absolute;
  background: inherit;
  border-radius: 50%;
}
.cloud::before { width: 60%; height: 60%; top: -30%; left: 10%; }
.cloud::after { width: 40%; height: 40%; top: -20%; left: 50%; }

.cloud1 { width: 100px; height: 55px; top: 15%; left: 110vw; animation-duration: 9s; }
.cloud2 { width: 150px; height: 75px; top: 38%; left: 130vw; animation-duration: 12s; }
.cloud3 { width: 80px; height: 45px; top: 22%; left: 160vw; animation-duration: 15s; }
.cloud4 { width: 100px; height: 70px; top: 62%; left: 120vw; animation-duration: 11s; }
.cloud5 { width: 170px; height: 60px; top: 72%; left: 150vw; animation-duration: 8s; }

@keyframes spd-move-clouds {
  0% { transform: translateX(0); }
  100% { transform: translateX(-260vw); }
}

/* ===== 长速度线 ===== */
.longfazers {
  position: absolute;
  inset: 0;
}
.longfazers span {
  position: absolute;
  height: 2px;
  width: 20%;
  background: var(--race-ink, #64748b);
}
.longfazers span:nth-child(1) { top: 20%; animation: spd-lf 0.6s linear infinite; animation-delay: -5s; }
.longfazers span:nth-child(2) { top: 40%; animation: spd-lf 0.8s linear infinite; animation-delay: -1s; }
.longfazers span:nth-child(3) { top: 60%; animation: spd-lf 0.6s linear infinite; }
.longfazers span:nth-child(4) { top: 80%; animation: spd-lf 0.5s linear infinite; animation-delay: -3s; }
@keyframes spd-lf {
  0% { left: 200%; opacity: 1; }
  100% { left: -200%; opacity: 0; }
}
@keyframes spd-lf2 {
  0% { left: 200%; opacity: 1; }
  100% { left: -200%; opacity: 0; }
}
@keyframes spd-lf3 {
  0% { left: 200%; opacity: 1; }
  100% { left: -100%; opacity: 0; }
}
@keyframes spd-lf4 {
  0% { left: 200%; opacity: 1; }
  100% { left: -100%; opacity: 0; }
}

/* ===== 骑手公共几何 ===== */
.racer {
  position: absolute;
  width: 260px;
  height: 80px;
  top: 50%;
}
.racer-left { left: 26%; transform: translateY(-50%); }
.racer-b {
  right: 26%;
  transform: translateY(-50%) scaleX(-1); /* 镜像：面对左骑手 */
}

.loader {
  position: absolute;
  top: 50%;
  left: 50%;
  margin-left: -50px;
  animation: spd-jitter 0.4s linear infinite;
}
.loader > span {
  height: 5px;
  width: 35px;
  position: absolute;
  top: -19px;
  left: 60px;
  border-radius: 2px 10px 1px 0;
}
.base span {
  position: absolute;
  width: 0;
  height: 0;
  /* 原版关键车身：没有 border-right 的宽度/样式就只剩速度线 */
  border-top: 6px solid transparent;
  border-right: 100px solid var(--race-base, #0f172a);
  border-bottom: 6px solid transparent;
}
.base span::before {
  content: "";
  height: 22px; width: 22px;
  border-radius: 50%;
  position: absolute;
  right: -110px; top: -16px;
}
.base span::after {
  content: "";
  position: absolute;
  width: 0; height: 0;
  border-top: 0 solid transparent;
  border-bottom: 16px solid transparent;
  top: -16px; right: -98px;
}
.face {
  position: absolute;
  height: 12px; width: 20px;
  border-radius: 20px 20px 0 0;
  transform: rotate(-40deg);
  right: -125px; top: -15px;
}
.face::after {
  content: "";
  height: 12px; width: 12px;
  right: 4px; top: 7px;
  position: absolute;
  transform: rotate(40deg);
  transform-origin: 50% 50%;
  border-radius: 0 0 0 2px;
}

/* 车尾小速度线 */
.loader > span > span {
  width: 30px; height: 1px;
  position: absolute;
}
.loader > span > span:nth-child(1) { animation: spd-fazer1 0.2s linear infinite; }
.loader > span > span:nth-child(2) { top: 3px; animation: spd-fazer2 0.4s linear infinite; }
.loader > span > span:nth-child(3) { top: 1px; animation: spd-fazer3 0.4s linear infinite; animation-delay: -1s; }
.loader > span > span:nth-child(4) { top: 4px; animation: spd-fazer4 1s linear infinite; animation-delay: -1s; }
@keyframes spd-fazer1 { 0% { left: 0; } 100% { left: -80px; opacity: 0; } }
@keyframes spd-fazer2 { 0% { left: 0; } 100% { left: -100px; opacity: 0; } }
@keyframes spd-fazer3 { 0% { left: 0; } 100% { left: -50px; opacity: 0; } }
@keyframes spd-fazer4 { 0% { left: 0; } 100% { left: -150px; opacity: 0; } }

/* 骑手抖动（原地高速骑行的错觉） */
@keyframes spd-jitter {
  0% { transform: translate(2px, 1px) rotate(0deg); }
  10% { transform: translate(-1px, -3px) rotate(-1deg); }
  20% { transform: translate(-2px, 0) rotate(1deg); }
  30% { transform: translate(1px, 2px) rotate(0deg); }
  40% { transform: translate(1px, -1px) rotate(1deg); }
  50% { transform: translate(-1px, 3px) rotate(-1deg); }
  60% { transform: translate(-1px, 1px) rotate(0deg); }
  70% { transform: translate(3px, 1px) rotate(-1deg); }
  80% { transform: translate(-2px, -1px) rotate(1deg); }
  90% { transform: translate(2px, 1px) rotate(0deg); }
  100% { transform: translate(1px, -2px) rotate(-1deg); }
}

/* ===== 左骑手：青色版（深色自动提亮）===== */
.racer-left .loader > span { background: var(--race-base, #f51313); }
.racer-left .base span { border-right-color: var(--race-base2, #fda4af); }
.racer-left .base span::before { background: var(--race-base2, #fda4af); }
.racer-left .base span::after { border-right-color: var(--race-base2, #fda4af); }
.racer-left .face { background: var(--race-base2, #fda4af); }
.racer-left .face::after { background: var(--race-base, #f51313); }
.racer-left .loader > span > span { background: #fff; }

/* ===== 右骑手：橙色版（深色自动提亮）===== */
.racer-b .loader > span { background: var(--race-ink, #0f172a); }
.racer-b .base span { border-right-color: var(--race-ink, #0f172a); }
.racer-b .base span::before { background: var(--race-ink, #0f172a); }
.racer-b .base span::after { border-right-color: var(--race-ink, #0f172a); }
.racer-b .face { background: var(--race-ink, #0f172a); }
.racer-b .face::after { background: var(--race-accent, #f51313); }
.racer-b .loader > span > span { background: var(--race-line, #64748b); }

html.dark .longfazers span { background: #94a3b8; }
html.dark .cloud { background: rgba(255, 255, 255, 0.22); }

@media (max-width: 959px) {
  .race-strip { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .cloud, .longfazers span, .loader, .loader > span > span { animation: none; }
}
</style>