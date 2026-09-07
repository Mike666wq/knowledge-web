<script setup>
// 悬浮 UFO 装饰（改造自 Uiverse 3D 悬浮方块 + 光束）
// - 加入全站背景层（fixed / z-index:-1 / pointer-events:none），与星空呼应
// - 只在暗色模式渲染（html.dark），浅色模式 display:none 彻底移除
// - 方块自转 4s + 上下浮动 4s；光束由 ::after 白色辉光实现
</script>

<template>
  <div class="ufo" aria-hidden="true">
    <div class="objchild">
      <span class="inn6"></span>
    </div>
  </div>
</template>

<style scoped>
.ufo {
  position: fixed;
  right: 20px;
  top: 72px;
  width: 200px;
  height: 200px;
  z-index: -1;
  pointer-events: none;
  transform: rotateX(-25deg) rotateY(20deg);
  transform-style: preserve-3d;
  transition: transform 0.5s all;
}

.objchild {
  animation: ufo-rotate 4s infinite linear;
  transform-style: preserve-3d;
  position: absolute;
  width: 100%;
  height: 100%;
}

/* 底部光束：暗色=白色辉光，浅色=天蓝辉光 */
.objchild::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 100%;
  filter: blur(20px);
  box-shadow: 0 0 200px 15px white;
  transform: rotateX(90deg) scale(1.1) translateZ(-120px);
}

/* 悬浮方块：上下浮动 + 自转 */
.inn6 {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgb(21, 21, 21);
  transform: rotateX(90deg) translateZ(100px);
  animation: ufo-updown 4s infinite ease-in-out;
  border-radius: 6px;
}

/* ===== 浅色模式配色：银白方块 + 天蓝光束 ===== */
html:not(.dark) .inn6 {
  background: linear-gradient(160deg, #ffffff, #d7e0ea);
  border: 1.5px solid #94a3b8;
  box-shadow: 0 12px 26px rgba(100, 116, 139, 0.35);
}
html:not(.dark) .objchild::after {
  box-shadow: 0 0 200px 15px rgba(56, 189, 248, 0.45);
}

@keyframes ufo-rotate {
  0% { transform: rotate3d(0, 1, 0, 0deg); }
  100% { transform: rotate3d(0, 1, 0, 360deg); }
}

@keyframes ufo-updown {
  0% { transform: translateY(100px) rotateX(90deg) translateZ(100px); }
  50% { transform: translateY(200px); }
  100% { transform: translateY(100px) rotateX(450deg) translateZ(100px); }
}

@media (max-width: 768px) {
  .ufo { display: none !important; }
}

@media (prefers-reduced-motion: reduce) {
  .objchild,
  .inn6 { animation: none; }
}
</style>