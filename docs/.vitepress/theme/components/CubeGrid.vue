<script setup>
// 像素方块阵（Uiverse cube grid）：3 个 skew 立方体组成的 3D 方块阵
// - hue-rotate 5s 循环变色
// - hover 单个方块变红 + 红色辉光
// 原 Uiverse 片段是 SCSS 嵌套写法，这里已展平为普通 CSS
</script>

<template>
  <div class="cube-grid-stage">
    <div class="cube-container">
      <div class="cube">
        <div style="--x:-1; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
        <div style="--x:0; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
        <div style="--x:1; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
      </div>
      <div class="cube">
        <div style="--x:-1; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
        <div style="--x:0; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
        <div style="--x:1; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
      </div>
      <div class="cube">
        <div style="--x:-1; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
        <div style="--x:0; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
        <div style="--x:1; --y:0;">
          <span style="--i:3;"></span>
          <span style="--i:2;"></span>
          <span style="--i:1;"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 舞台：撑出足够高度容纳整簇方块（含 skew 后的上下延伸），不裁剪 */
.cube-grid-stage {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 460px;
}

.cube-container {
  position: relative;
  left: -25px; /* 视觉居中修正 */
  transform: skewY(-20deg) scale(0.82);
}

.cube {
  position: relative;
  z-index: 2;
}
.cube:nth-child(2) {
  z-index: 1;
  translate: -60px -60px;
}
.cube:nth-child(3) {
  z-index: 3;
  translate: 60px 60px;
}

.cube div {
  position: absolute;
  display: flex;
  flex-direction: column;
  gap: 30px;
  translate: calc(-70px * var(--x)) calc(-60px * var(--y));
}

.cube div span {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 50px;
  background: #dcdcdc;
  z-index: calc(1 * var(--i));
  transition: background 0.4s, filter 0.4s, box-shadow 0.4s;
}

.cube div span:hover {
  transition: 0s;
  background: var(--vp-c-brand-1);
  filter: drop-shadow(0 0 22px var(--vp-c-brand-1));
}
.cube div span:hover::before,
.cube div span:hover::after {
  transition: 0s;
  background: var(--vp-c-brand-1);
}

/* 左侧面 */
.cube div span::before {
  content: "";
  position: absolute;
  left: -40px;
  width: 40px;
  height: 100%;
  background: #fff;
  transform-origin: right;
  transform: skewY(45deg);
  transition: background 0.4s;
}

/* 顶面 */
.cube div span::after {
  content: "";
  position: absolute;
  top: -40px;
  left: 0;
  width: 100%;
  height: 40px;
  background: #f2f2f2;
  transform-origin: bottom;
  transform: skewX(45deg);
  transition: background 0.4s;
}

@media (prefers-reduced-motion: reduce) {
  .cube-container { animation: none; }
}
</style>
