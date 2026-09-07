<script setup>
// 侧边栏宠物区（笔记页 + 关于页）：接在 幽灵/立方/幽灵 装饰列下方
// - 像素小恐龙（Uiverse pixel dino，逐帧奔跑）与小狗同列居中
// - 太极已下架
// 固定定位，跟随幽灵列的坐标体系；<960px 隐藏
</script>

<template>
  <div class="side-pets" aria-hidden="true">
    <!-- 小恐龙 -->
    <div class="dino-stage">
      <aside class="loader dino-loader" style="--wh-number: 24;">
        <div class="pixel"></div>
      </aside>
    </div>

    <!-- 小狗（恐龙正下方，同列） -->
    <div class="dog-stage">
      <div class="main dog-main">
        <div class="dog">
          <div class="dog__paws">
            <div class="dog__bl-leg leg">
              <div class="dog__bl-paw paw"></div>
              <div class="dog__bl-top top"></div>
            </div>
            <div class="dog__fl-leg leg">
              <div class="dog__fl-paw paw"></div>
              <div class="dog__fl-top top"></div>
            </div>
            <div class="dog__fr-leg leg">
              <div class="dog__fr-paw paw"></div>
              <div class="dog__fr-top top"></div>
            </div>
          </div>

          <div class="dog__body">
            <div class="dog__tail"></div>
          </div>

          <div class="dog__head">
            <div class="dog__snout">
              <div class="dog__nose"></div>
              <div class="dog__eyes">
                <div class="dog__eye-l"></div>
                <div class="dog__eye-r"></div>
              </div>
            </div>
          </div>

          <div class="dog__head-c">
            <div class="dog__ear-l"></div>
            <div class="dog__ear-r"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ===== 宠物区容器：接在幽灵列（~570px）之下，占满侧边栏宽 ===== */
.side-pets {
  position: fixed;
  left: 0;
  top: 590px;
  width: 272px;
  height: 330px;
  pointer-events: none;
  z-index: 54;
}

/* ===================== 小恐龙 ===================== */
/* flex 居中代替 absolute+translate%（zoom 与百分比位移在不同浏览器解析不一致） */
.dino-stage {
  position: absolute;
  left: 56px;
  top: 6px;
  width: 124px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.loader {
  --zoom: 0.3;
  flex: none; /* 防止 flex 收缩压缩 zoom 后的画布 */
  --wh: calc(var(--wh-number) * 1px);
  --wh-n: calc(var(--wh-number) * -1px);
  width: calc(var(--wh-number) * var(--wh));
  height: calc(var(--wh-number) * var(--wh));
  --color: #fff;
  --blur: 0;
  filter: drop-shadow(var(--wh-n) 0 var(--blur) var(--color))
    drop-shadow(0 var(--wh-n) var(--blur) var(--color))
    drop-shadow(var(--wh) 0 var(--blur) var(--color))
    drop-shadow(0 var(--wh) var(--blur) var(--color));
  image-rendering: pixelated;
  zoom: var(--zoom);
  animation: mover 0.3s linear infinite;
}
.loader .pixel {
  width: var(--wh);
  height: var(--wh);
  box-shadow: var(--shadow);
}

@keyframes mover {
  0%,
  100% {
    --shadow: 0px 0px transparent, 24px 0px transparent, 48px 0px transparent,
      72px 0px transparent, 96px 0px transparent, 120px 0px transparent,
      144px 0px transparent, 168px 0px transparent, 192px 0px transparent,
      216px 0px transparent, 240px 0px transparent, 264px 0px transparent,
      288px 0px transparent, 312px 0px #535353, 336px 0px #535353,
      360px 0px #535353, 384px 0px #535353, 408px 0px #535353, 432px 0px #535353,
      456px 0px #535353, 480px 0px #535353, 504px 0px #535353, 528px 0px #535353,
      552px 0px transparent, 0px 24px transparent, 24px 24px transparent,
      48px 24px transparent, 72px 24px transparent, 96px 24px transparent,
      120px 24px transparent, 144px 24px transparent, 168px 24px transparent,
      192px 24px transparent, 216px 24px transparent, 240px 24px transparent,
      264px 24px transparent, 288px 24px #535353, 312px 24px #535353,
      336px 24px #535353, 360px 24px #535353, 384px 24px #535353,
      408px 24px #535353, 432px 24px #535353, 456px 24px #535353,
      480px 24px #535353, 504px 24px #535353, 528px 24px #535353,
      552px 24px #535353, 0px 48px transparent, 24px 48px transparent,
      48px 48px transparent, 72px 48px transparent, 96px 48px transparent,
      120px 48px transparent, 144px 48px transparent, 168px 48px transparent,
      192px 48px transparent, 216px 48px transparent, 240px 48px transparent,
      264px 48px transparent, 288px 48px #535353, 312px 48px #535353,
      336px 48px transparent, 360px 48px transparent, 384px 48px #535353,
      408px 48px #535353, 432px 48px #535353, 456px 48px #535353,
      480px 48px #535353, 504px 48px #535353, 528px 48px #535353,
      552px 48px #535353, 0px 72px transparent, 24px 72px transparent,
      48px 72px transparent, 72px 72px transparent, 96px 72px transparent,
      120px 72px transparent, 144px 72px transparent, 168px 72px transparent,
      192px 72px transparent, 216px 72px transparent, 240px 72px transparent,
      264px 72px transparent, 288px 72px #535353, 312px 72px #535353,
      336px 72px transparent, 360px 72px transparent, 384px 72px #535353,
      408px 72px #535353, 432px 72px #535353, 456px 72px #535353,
      480px 72px #535353, 504px 72px #535353, 528px 72px #535353,
      552px 72px #535353, 0px 96px transparent, 24px 96px transparent,
      48px 96px transparent, 72px 96px transparent, 96px 96px transparent,
      120px 96px transparent, 144px 96px transparent, 168px 96px transparent,
      192px 96px transparent, 216px 96px transparent, 240px 96px transparent,
      264px 96px transparent, 288px 96px #535353, 312px 96px #535353,
      336px 96px #535353, 360px 96px #535353, 384px 96px #535353,
      408px 96px #535353, 432px 96px #535353, 456px 96px #535353,
      480px 96px #535353, 504px 96px #535353, 528px 96px #535353,
      552px 96px #535353, 0px 120px transparent, 24px 120px transparent,
      48px 120px transparent, 72px 120px transparent, 96px 120px transparent,
      120px 120px transparent, 144px 120px transparent, 168px 120px transparent,
      192px 120px transparent, 216px 120px transparent, 240px 120px transparent,
      264px 120px transparent, 288px 120px #535353, 312px 120px #535353,
      336px 120px #535353, 360px 120px #535353, 384px 120px #535353,
      408px 120px #535353, 432px 120px #535353, 456px 120px #535353,
      480px 120px #535353, 504px 120px #535353, 528px 120px #535353,
      552px 120px #535353, 0px 144px transparent, 24px 144px transparent,
      48px 144px transparent, 72px 144px transparent, 96px 144px transparent,
      120px 144px transparent, 144px 144px transparent, 168px 144px transparent,
      192px 144px transparent, 216px 144px transparent, 240px 144px transparent,
      264px 144px transparent, 288px 144px #535353, 312px 144px #535353,
      336px 144px #535353, 360px 144px #535353, 384px 144px #535353,
      408px 144px #535353, 432px 144px transparent, 456px 144px transparent,
      480px 144px transparent, 504px 144px transparent, 528px 144px transparent,
      552px 144px transparent, 0px 168px transparent, 24px 168px transparent,
      48px 168px transparent, 72px 168px transparent, 96px 168px transparent,
      120px 168px transparent, 144px 168px transparent, 168px 168px transparent,
      192px 168px transparent, 216px 168px transparent, 240px 168px transparent,
      264px 168px transparent, 288px 168px #535353, 312px 168px #535353,
      336px 168px #535353, 360px 168px #535353, 384px 168px #535353,
      408px 168px #535353, 432px 168px transparent, 456px 168px transparent,
      480px 168px transparent, 504px 168px transparent, 528px 168px transparent,
      552px 168px transparent, 0px 192px transparent, 24px 192px transparent,
      48px 192px transparent, 72px 192px transparent, 96px 192px transparent,
      120px 192px transparent, 144px 192px transparent, 168px 192px transparent,
      192px 192px transparent, 216px 192px transparent, 240px 192px transparent,
      264px 192px transparent, 288px 192px #535353, 312px 192px #535353,
      336px 192px #535353, 360px 192px #535353, 384px 192px #535353,
      408px 192px #535353, 432px 192px #535353, 456px 192px #535353,
      480px 192px #535353, 504px 192px #535353, 528px 192px transparent,
      552px 192px transparent, 0px 216px #535353, 24px 216px transparent,
      48px 216px transparent, 72px 216px transparent, 96px 216px transparent,
      120px 216px transparent, 144px 216px transparent, 168px 216px transparent,
      192px 216px transparent, 216px 216px transparent, 240px 216px #535353,
      264px 216px #535353, 288px 216px #535353, 312px 216px #535353,
      336px 216px #535353, 360px 216px #535353, 384px 216px #535353,
      408px 216px transparent, 432px 216px transparent, 456px 216px transparent,
      480px 216px transparent, 504px 216px transparent, 528px 216px transparent,
      552px 216px transparent, 0px 240px #535353, 24px 240px transparent,
      48px 240px transparent, 72px 240px transparent, 96px 240px transparent,
      120px 240px transparent, 144px 240px transparent, 168px 240px transparent,
      192px 240px #535353, 216px 240px #535353, 240px 240px #535353,
      264px 240px #535353, 288px 240px #535353, 312px 240px #535353,
      336px 240px #535353, 360px 240px #535353, 384px 240px #535353,
      408px 240px transparent, 432px 240px transparent, 456px 240px transparent,
      480px 240px transparent, 504px 240px transparent, 528px 240px transparent,
      552px 240px transparent, 0px 264px #535353, 24px 264px #535353,
      48px 264px transparent, 72px 264px transparent, 96px 264px transparent,
      120px 264px transparent, 144px 264px transparent, 168px 264px #535353,
      192px 264px #535353, 216px 264px #535353, 240px 264px #535353,
      264px 264px #535353, 288px 264px #535353, 312px 264px #535353,
      336px 264px #535353, 360px 264px #535353, 384px 264px #535353,
      408px 264px #535353, 432px 264px #535353, 456px 264px transparent,
      480px 264px transparent, 504px 264px transparent, 528px 264px transparent,
      552px 264px transparent, 0px 288px #535353, 24px 288px #535353,
      48px 288px #535353, 72px 288px transparent, 96px 288px transparent,
      120px 288px transparent, 144px 288px #535353, 168px 288px #535353,
      192px 288px #535353, 216px 288px #535353, 240px 288px #535353,
      264px 288px #535353, 288px 288px #535353, 312px 288px #535353,
      336px 288px #535353, 360px 288px #535353, 384px 288px #535353,
      408px 288px transparent, 432px 288px #535353, 456px 288px transparent,
      480px 288px transparent, 504px 288px transparent, 528px 288px transparent,
      552px 288px transparent, 0px 312px #535353, 24px 312px #535353,
      48px 312px #535353, 72px 312px #535353, 96px 312px #535353,
      120px 312px #535353, 144px 312px #535353, 168px 312px #535353,
      192px 312px #535353, 216px 312px #535353, 240px 312px #535353,
      264px 312px #535353, 288px 312px #535353, 312px 312px #535353,
      336px 312px #535353, 360px 312px #535353, 384px 312px #535353,
      408px 312px transparent, 432px 312px transparent, 456px 312px transparent,
      480px 312px transparent, 504px 312px transparent, 528px 312px transparent,
      552px 312px transparent, 0px 336px #535353, 24px 336px #535353,
      48px 336px #535353, 72px 336px #535353, 96px 336px #535353,
      120px 336px #535353, 144px 336px #535353, 168px 336px #535353,
      192px 336px #535353, 216px 336px #535353, 240px 336px #535353,
      264px 336px #535353, 288px 336px #535353, 312px 336px #535353,
      336px 336px #535353, 360px 336px #535353, 384px 336px #535353,
      408px 336px transparent, 432px 336px transparent, 456px 336px transparent,
      480px 336px transparent, 504px 336px transparent, 528px 336px transparent,
      552px 336px transparent, 0px 360px transparent, 24px 360px #535353,
      48px 360px #535353, 72px 360px #535353, 96px 360px #535353,
      120px 360px #535353, 144px 360px #535353, 168px 360px #535353,
      192px 360px #535353, 216px 360px #535353, 240px 360px #535353,
      264px 360px #535353, 288px 360px #535353, 312px 360px #535353,
      336px 360px #535353, 360px 360px #535353, 384px 360px #535353,
      408px 360px transparent, 432px 360px transparent, 456px 360px transparent,
      480px 360px transparent, 504px 360px transparent, 528px 360px transparent,
      552px 360px transparent, 0px 384px transparent, 24px 384px transparent,
      48px 384px #535353, 72px 384px #535353, 96px 384px #535353,
      120px 384px #535353, 144px 384px #535353, 168px 384px #535353,
      192px 384px #535353, 216px 384px #535353, 240px 384px #535353,
      264px 384px #535353, 288px 384px #535353, 312px 384px #535353,
      336px 384px #535353, 360px 384px #535353, 384px 384px transparent,
      408px 384px transparent, 432px 384px transparent, 456px 384px transparent,
      480px 384px transparent, 504px 384px transparent, 528px 384px transparent,
      552px 384px transparent, 0px 408px transparent, 24px 408px transparent,
      48px 408px transparent, 72px 408px #535353, 96px 408px #535353,
      120px 408px #535353, 144px 408px #535353, 168px 408px #535353,
      192px 408px #535353, 216px 408px #535353, 240px 408px #535353,
      264px 408px #535353, 288px 408px #535353, 312px 408px #535353,
      336px 408px transparent, 360px 408px transparent, 384px 408px transparent,
      408px 408px transparent, 432px 408px transparent, 456px 408px transparent,
      480px 408px transparent, 504px 408px transparent, 528px 408px transparent,
      552px 408px transparent, 0px 432px transparent, 24px 432px transparent,
      48px 432px transparent, 72px 432px transparent, 96px 432px #535353,
      120px 432px #535353, 144px 432px #535353, 168px 432px #535353,
      192px 432px #535353, 216px 432px #535353, 240px 432px #535353,
      264px 432px #535353, 288px 432px #535353, 312px 432px #535353,
      336px 432px transparent, 360px 432px transparent, 384px 432px transparent,
      408px 432px transparent, 432px 432px transparent, 456px 432px transparent,
      480px 432px transparent, 504px 432px transparent, 528px 432px transparent,
      552px 432px transparent, 0px 456px transparent, 24px 456px transparent,
      48px 456px transparent, 72px 456px transparent, 96px 456px transparent,
      120px 456px #535353, 144px 456px #535353, 168px 456px #535353,
      192px 456px #535353, 216px 456px #535353, 240px 456px #535353,
      264px 456px #535353, 288px 456px #535353, 312px 456px transparent,
      336px 456px transparent, 360px 456px transparent, 384px 456px transparent,
      408px 456px transparent, 432px 456px transparent, 456px 456px transparent,
      480px 456px transparent, 504px 456px transparent, 528px 456px transparent,
      552px 456px transparent, 0px 480px transparent, 24px 480px transparent,
      48px 480px transparent, 72px 480px transparent, 96px 480px transparent,
      120px 480px transparent, 144px 480px #535353, 168px 480px #535353,
      192px 480px #535353, 216px 480px transparent, 240px 480px transparent,
      264px 480px #535353, 288px 480px #535353, 312px 480px transparent,
      336px 480px transparent, 360px 480px transparent, 384px 480px transparent,
      408px 480px transparent, 432px 480px transparent, 456px 480px transparent,
      480px 480px transparent, 504px 480px transparent, 528px 480px transparent,
      552px 480px transparent, 0px 504px transparent, 24px 504px transparent,
      48px 504px transparent, 72px 504px transparent, 96px 504px transparent,
      120px 504px transparent, 144px 504px #535353, 168px 504px #535353,
      192px 504px transparent, 216px 504px transparent, 240px 504px transparent,
      264px 504px transparent, 288px 504px #535353, 312px 504px transparent,
      336px 504px transparent, 360px 504px transparent, 384px 504px transparent,
      408px 504px transparent, 432px 504px transparent, 456px 504px transparent,
      480px 504px transparent, 504px 504px transparent, 528px 504px transparent,
      552px 504px transparent, 0px 528px transparent, 24px 528px transparent,
      48px 528px transparent, 72px 528px transparent, 96px 528px transparent,
      120px 528px transparent, 144px 528px #535353, 168px 528px transparent,
      192px 528px transparent, 216px 528px transparent, 240px 528px transparent,
      264px 528px transparent, 288px 528px #535353, 312px 528px transparent,
      336px 528px transparent, 360px 528px transparent, 384px 528px transparent,
      408px 528px transparent, 432px 528px transparent, 456px 528px transparent,
      480px 528px transparent, 504px 528px transparent, 528px 528px transparent,
      552px 528px transparent, 0px 552px transparent, 24px 552px transparent,
      48px 552px transparent, 72px 552px transparent, 96px 552px transparent,
      120px 552px transparent, 144px 552px #535353, 168px 552px #535353,
      192px 552px transparent, 216px 552px transparent, 240px 552px transparent,
      264px 552px transparent, 288px 552px #535353, 312px 552px #535353,
      336px 552px transparent, 360px 552px transparent, 384px 552px transparent,
      408px 552px transparent, 432px 552px transparent, 456px 552px transparent,
      480px 552px transparent, 504px 552px transparent, 528px 552px transparent,
      552px 552px transparent;
  }
  33% {
    --shadow: 0px 0px transparent, 24px 0px transparent, 48px 0px transparent,
      72px 0px transparent, 96px 0px transparent, 120px 0px transparent,
      144px 0px transparent, 168px 0px transparent, 192px 0px transparent,
      216px 0px transparent, 240px 0px transparent, 264px 0px transparent,
      288px 0px transparent, 312px 0px #535353, 336px 0px #535353,
      360px 0px #535353, 384px 0px #535353, 408px 0px #535353, 432px 0px #535353,
      456px 0px #535353, 480px 0px #535353, 504px 0px #535353, 528px 0px #535353,
      552px 0px transparent, 0px 24px transparent, 24px 24px transparent,
      48px 24px transparent, 72px 24px transparent, 96px 24px transparent,
      120px 24px transparent, 144px 24px transparent, 168px 24px transparent,
      192px 24px transparent, 216px 24px transparent, 240px 24px transparent,
      264px 24px transparent, 288px 24px #535353, 312px 24px #535353,
      336px 24px #535353, 360px 24px #535353, 384px 24px #535353,
      408px 24px #535353, 432px 24px #535353, 456px 24px #535353,
      480px 24px #535353, 504px 24px #535353, 528px 24px #535353,
      552px 24px #535353, 0px 48px transparent, 24px 48px transparent,
      48px 48px transparent, 72px 48px transparent, 96px 48px transparent,
      120px 48px transparent, 144px 48px transparent, 168px 48px transparent,
      192px 48px transparent, 216px 48px transparent, 240px 48px transparent,
      264px 48px transparent, 288px 48px #535353, 312px 48px #535353,
      336px 48px transparent, 360px 48px transparent, 384px 48px #535353,
      408px 48px #535353, 432px 48px #535353, 456px 48px #535353,
      480px 48px #535353, 504px 48px #535353, 528px 48px #535353,
      552px 48px #535353, 0px 72px transparent, 24px 72px transparent,
      48px 72px transparent, 72px 72px transparent, 96px 72px transparent,
      120px 72px transparent, 144px 72px transparent, 168px 72px transparent,
      192px 72px transparent, 216px 72px transparent, 240px 72px transparent,
      264px 72px transparent, 288px 72px #535353, 312px 72px #535353,
      336px 72px transparent, 360px 72px transparent, 384px 72px #535353,
      408px 72px #535353, 432px 72px #535353, 456px 72px #535353,
      480px 72px #535353, 504px 72px #535353, 528px 72px #535353,
      552px 72px #535353, 0px 96px transparent, 24px 96px transparent,
      48px 96px transparent, 72px 96px transparent, 96px 96px transparent,
      120px 96px transparent, 144px 96px transparent, 168px 96px transparent,
      192px 96px transparent, 216px 96px transparent, 240px 96px transparent,
      264px 96px transparent, 288px 96px #535353, 312px 96px #535353,
      336px 96px #535353, 360px 96px #535353, 384px 96px #535353,
      408px 96px #535353, 432px 96px #535353, 456px 96px #535353,
      480px 96px #535353, 504px 96px #535353, 528px 96px #535353,
      552px 96px #535353, 0px 120px transparent, 24px 120px transparent,
      48px 120px transparent, 72px 120px transparent, 96px 120px transparent,
      120px 120px transparent, 144px 120px transparent, 168px 120px transparent,
      192px 120px transparent, 216px 120px transparent, 240px 120px transparent,
      264px 120px transparent, 288px 120px #535353, 312px 120px #535353,
      336px 120px #535353, 360px 120px #535353, 384px 120px #535353,
      408px 120px #535353, 432px 120px #535353, 456px 120px #535353,
      480px 120px #535353, 504px 120px #535353, 528px 120px #535353,
      552px 120px #535353, 0px 144px transparent, 24px 144px transparent,
      48px 144px transparent, 72px 144px transparent, 96px 144px transparent,
      120px 144px transparent, 144px 144px transparent, 168px 144px transparent,
      192px 144px transparent, 216px 144px transparent, 240px 144px transparent,
      264px 144px transparent, 288px 144px #535353, 312px 144px #535353,
      336px 144px #535353, 360px 144px #535353, 384px 144px #535353,
      408px 144px #535353, 432px 144px transparent, 456px 144px transparent,
      480px 144px transparent, 504px 144px transparent, 528px 144px transparent,
      552px 144px transparent, 0px 168px transparent, 24px 168px transparent,
      48px 168px transparent, 72px 168px transparent, 96px 168px transparent,
      120px 168px transparent, 144px 168px transparent, 168px 168px transparent,
      192px 168px transparent, 216px 168px transparent, 240px 168px transparent,
      264px 168px transparent, 288px 168px #535353, 312px 168px #535353,
      336px 168px #535353, 360px 168px #535353, 384px 168px #535353,
      408px 168px #535353, 432px 168px transparent, 456px 168px transparent,
      480px 168px transparent, 504px 168px transparent, 528px 168px transparent,
      552px 168px transparent, 0px 192px transparent, 24px 192px transparent,
      48px 192px transparent, 72px 192px transparent, 96px 192px transparent,
      120px 192px transparent, 144px 192px transparent, 168px 192px transparent,
      192px 192px transparent, 216px 192px transparent, 240px 192px transparent,
      264px 192px transparent, 288px 192px #535353, 312px 192px #535353,
      336px 192px #535353, 360px 192px #535353, 384px 192px #535353,
      408px 192px #535353, 432px 192px #535353, 456px 192px #535353,
      480px 192px #535353, 504px 192px #535353, 528px 192px transparent,
      552px 192px transparent, 0px 216px #535353, 24px 216px transparent,
      48px 216px transparent, 72px 216px transparent, 96px 216px transparent,
      120px 216px transparent, 144px 216px transparent, 168px 216px transparent,
      192px 216px transparent, 216px 216px transparent, 240px 216px #535353,
      264px 216px #535353, 288px 216px #535353, 312px 216px #535353,
      336px 216px #535353, 360px 216px #535353, 384px 216px #535353,
      408px 216px transparent, 432px 216px transparent, 456px 216px transparent,
      480px 216px transparent, 504px 216px transparent, 528px 216px transparent,
      552px 216px transparent, 0px 240px #535353, 24px 240px transparent,
      48px 240px transparent, 72px 240px transparent, 96px 240px transparent,
      120px 240px transparent, 144px 240px transparent, 168px 240px transparent,
      192px 240px #535353, 216px 240px #535353, 240px 240px #535353,
      264px 240px #535353, 288px 240px #535353, 312px 240px #535353,
      336px 240px #535353, 360px 240px #535353, 384px 240px #535353,
      408px 240px transparent, 432px 240px transparent, 456px 240px transparent,
      480px 240px transparent, 504px 240px transparent, 528px 240px transparent,
      552px 240px transparent, 0px 264px #535353, 24px 264px #535353,
      48px 264px transparent, 72px 264px transparent, 96px 264px transparent,
      120px 264px transparent, 144px 264px transparent, 168px 264px #535353,
      192px 264px #535353, 216px 264px #535353, 240px 264px #535353,
      264px 264px #535353, 288px 264px #535353, 312px 264px #535353,
      336px 264px #535353, 360px 264px #535353, 384px 264px #535353,
      408px 264px #535353, 432px 264px #535353, 456px 264px transparent,
      480px 264px transparent, 504px 264px transparent, 528px 264px transparent,
      552px 264px transparent, 0px 288px #535353, 24px 288px #535353,
      48px 288px #535353, 72px 288px transparent, 96px 288px transparent,
      120px 288px transparent, 144px 288px #535353, 168px 288px #535353,
      192px 288px #535353, 216px 288px #535353, 240px 288px #535353,
      264px 288px #535353, 288px 288px #535353, 312px 288px #535353,
      336px 288px #535353, 360px 288px #535353, 384px 288px #535353,
      408px 288px transparent, 432px 288px #535353, 456px 288px transparent,
      480px 288px transparent, 504px 288px transparent, 528px 288px transparent,
      552px 288px transparent, 0px 312px #535353, 24px 312px #535353,
      48px 312px #535353, 72px 312px #535353, 96px 312px #535353,
      120px 312px #535353, 144px 312px #535353, 168px 312px #535353,
      192px 312px #535353, 216px 312px #535353, 240px 312px #535353,
      264px 312px #535353, 288px 312px #535353, 312px 312px #535353,
      336px 312px #535353, 360px 312px #535353, 384px 312px #535353,
      408px 312px transparent, 432px 312px transparent, 456px 312px transparent,
      480px 312px transparent, 504px 312px transparent, 528px 312px transparent,
      552px 312px transparent, 0px 336px #535353, 24px 336px #535353,
      48px 336px #535353, 72px 336px #535353, 96px 336px #535353,
      120px 336px #535353, 144px 336px #535353, 168px 336px #535353,
      192px 336px #535353, 216px 336px #535353, 240px 336px #535353,
      264px 336px #535353, 288px 336px #535353, 312px 336px #535353,
      336px 336px #535353, 360px 336px #535353, 384px 336px #535353,
      408px 336px transparent, 432px 336px transparent, 456px 336px transparent,
      480px 336px transparent, 504px 336px transparent, 528px 336px transparent,
      552px 336px transparent, 0px 360px transparent, 24px 360px #535353,
      48px 360px #535353, 72px 360px #535353, 96px 360px #535353,
      120px 360px #535353, 144px 360px #535353, 168px 360px #535353,
      192px 360px #535353, 216px 360px #535353, 240px 360px #535353,
      264px 360px #535353, 288px 360px #535353, 312px 360px #535353,
      336px 360px #535353, 360px 360px #535353, 384px 360px #535353,
      408px 360px transparent, 432px 360px transparent, 456px 360px transparent,
      480px 360px transparent, 504px 360px transparent, 528px 360px transparent,
      552px 360px transparent, 0px 384px transparent, 24px 384px transparent,
      48px 384px #535353, 72px 384px #535353, 96px 384px #535353,
      120px 384px #535353, 144px 384px #535353, 168px 384px #535353,
      192px 384px #535353, 216px 384px #535353, 240px 384px #535353,
      264px 384px #535353, 288px 384px #535353, 312px 384px #535353,
      336px 384px #535353, 360px 384px #535353, 384px 384px transparent,
      408px 384px transparent, 432px 384px transparent, 456px 384px transparent,
      480px 384px transparent, 504px 384px transparent, 528px 384px transparent,
      552px 384px transparent, 0px 408px transparent, 24px 408px transparent,
      48px 408px transparent, 72px 408px #535353, 96px 408px #535353,
      120px 408px #535353, 144px 408px #535353, 168px 408px #535353,
      192px 408px #535353, 216px 408px #535353, 240px 408px #535353,
      264px 408px #535353, 288px 408px #535353, 312px 408px #535353,
      336px 408px transparent, 360px 408px transparent, 384px 408px transparent,
      408px 408px transparent, 432px 408px transparent, 456px 408px transparent,
      480px 408px transparent, 504px 408px transparent, 528px 408px transparent,
      552px 408px transparent, 0px 432px transparent, 24px 432px transparent,
      48px 432px transparent, 72px 432px transparent, 96px 432px #535353,
      120px 432px #535353, 144px 432px #535353, 168px 432px #535353,
      192px 432px #535353, 216px 432px #535353, 240px 432px #535353,
      264px 432px #535353, 288px 432px #535353, 312px 432px #535353,
      336px 432px transparent, 360px 432px transparent, 384px 432px transparent,
      408px 432px transparent, 432px 432px transparent, 456px 432px transparent,
      480px 432px transparent, 504px 432px transparent, 528px 432px transparent,
      552px 432px transparent, 0px 456px transparent, 24px 456px transparent,
      48px 456px transparent, 72px 456px transparent, 96px 456px transparent,
      120px 456px #535353, 144px 456px #535353, 168px 456px #535353,
      192px 456px #535353, 216px 456px #535353, 240px 456px #535353,
      264px 456px #535353, 288px 456px #535353, 312px 456px transparent,
      336px 456px transparent, 360px 456px transparent, 384px 456px transparent,
      408px 456px transparent, 432px 456px transparent, 456px 456px transparent,
      480px 456px transparent, 504px 456px transparent, 528px 456px transparent,
      552px 456px transparent, 0px 480px transparent, 24px 480px transparent,
      48px 480px transparent, 72px 480px transparent, 96px 480px transparent,
      120px 480px transparent, 144px 480px #535353, 168px 480px #535353,
      192px 480px #535353, 216px 480px transparent, 240px 480px transparent,
      264px 480px #535353, 288px 480px #535353, 312px 480px transparent,
      336px 480px transparent, 360px 480px transparent, 384px 480px transparent,
      408px 480px transparent, 432px 480px transparent, 456px 480px transparent,
      480px 480px transparent, 504px 480px transparent, 528px 480px transparent,
      552px 480px transparent, 0px 504px transparent, 24px 504px transparent,
      48px 504px transparent, 72px 504px transparent, 96px 504px transparent,
      120px 504px transparent, 144px 504px #535353, 168px 504px #535353,
      192px 504px transparent, 216px 504px transparent, 240px 504px transparent,
      264px 504px transparent, 288px 504px transparent, 312px 504px transparent,
      336px 504px transparent, 360px 504px transparent, 384px 504px transparent,
      408px 504px transparent, 432px 504px transparent, 456px 504px transparent,
      480px 504px transparent, 504px 504px transparent, 528px 504px transparent,
      552px 504px transparent, 0px 528px transparent, 24px 528px transparent,
      48px 528px transparent, 72px 528px transparent, 96px 528px transparent,
      120px 528px transparent, 144px 528px #535353, 168px 528px transparent,
      192px 528px transparent, 216px 528px transparent, 240px 528px transparent,
      264px 528px transparent, 288px 528px transparent, 312px 528px transparent,
      336px 528px transparent, 360px 528px transparent, 384px 528px transparent,
      408px 528px transparent, 432px 528px transparent, 456px 528px transparent,
      480px 528px transparent, 504px 528px transparent, 528px 528px transparent,
      552px 528px transparent, 0px 552px transparent, 24px 552px transparent,
      48px 552px transparent, 72px 552px transparent, 96px 552px transparent,
      120px 552px transparent, 144px 552px #535353, 168px 552px #535353,
      192px 552px transparent, 216px 552px transparent, 240px 552px transparent,
      264px 552px transparent, 288px 552px transparent, 312px 552px transparent,
      336px 552px transparent, 360px 552px transparent, 384px 552px transparent,
      408px 552px transparent, 432px 552px transparent, 456px 552px transparent,
      480px 552px transparent, 504px 552px transparent, 528px 552px transparent,
      552px 552px transparent;
  }
  66% {
    --shadow: 0px 0px transparent, 24px 0px transparent, 48px 0px transparent,
      72px 0px transparent, 96px 0px transparent, 120px 0px transparent,
      144px 0px transparent, 168px 0px transparent, 192px 0px transparent,
      216px 0px transparent, 240px 0px transparent, 264px 0px transparent,
      288px 0px transparent, 312px 0px #535353, 336px 0px #535353,
      360px 0px #535353, 384px 0px #535353, 408px 0px #535353, 432px 0px #535353,
      456px 0px #535353, 480px 0px #535353, 504px 0px #535353, 528px 0px #535353,
      552px 0px transparent, 0px 24px transparent, 24px 24px transparent,
      48px 24px transparent, 72px 24px transparent, 96px 24px transparent,
      120px 24px transparent, 144px 24px transparent, 168px 24px transparent,
      192px 24px transparent, 216px 24px transparent, 240px 24px transparent,
      264px 24px transparent, 288px 24px #535353, 312px 24px #535353,
      336px 24px #535353, 360px 24px #535353, 384px 24px #535353,
      408px 24px #535353, 432px 24px #535353, 456px 24px #535353,
      480px 24px #535353, 504px 24px #535353, 528px 24px #535353,
      552px 24px #535353, 0px 48px transparent, 24px 48px transparent,
      48px 48px transparent, 72px 48px transparent, 96px 48px transparent,
      120px 48px transparent, 144px 48px transparent, 168px 48px transparent,
      192px 48px transparent, 216px 48px transparent, 240px 48px transparent,
      264px 48px transparent, 288px 48px #535353, 312px 48px #535353,
      336px 48px transparent, 360px 48px transparent, 384px 48px #535353,
      408px 48px #535353, 432px 48px #535353, 456px 48px #535353,
      480px 48px #535353, 504px 48px #535353, 528px 48px #535353,
      552px 48px #535353, 0px 72px transparent, 24px 72px transparent,
      48px 72px transparent, 72px 72px transparent, 96px 72px transparent,
      120px 72px transparent, 144px 72px transparent, 168px 72px transparent,
      192px 72px transparent, 216px 72px transparent, 240px 72px transparent,
      264px 72px transparent, 288px 72px #535353, 312px 72px #535353,
      336px 72px transparent, 360px 72px transparent, 384px 72px #535353,
      408px 72px #535353, 432px 72px #535353, 456px 72px #535353,
      480px 72px #535353, 504px 72px #535353, 528px 72px #535353,
      552px 72px #535353, 0px 96px transparent, 24px 96px transparent,
      48px 96px transparent, 72px 96px transparent, 96px 96px transparent,
      120px 96px transparent, 144px 96px transparent, 168px 96px transparent,
      192px 96px transparent, 216px 96px transparent, 240px 96px transparent,
      264px 96px transparent, 288px 96px #535353, 312px 96px #535353,
      336px 96px #535353, 360px 96px #535353, 384px 96px #535353,
      408px 96px #535353, 432px 96px #535353, 456px 96px #535353,
      480px 96px #535353, 504px 96px #535353, 528px 96px #535353,
      552px 96px #535353, 0px 120px transparent, 24px 120px transparent,
      48px 120px transparent, 72px 120px transparent, 96px 120px transparent,
      120px 120px transparent, 144px 120px transparent, 168px 120px transparent,
      192px 120px transparent, 216px 120px transparent, 240px 120px transparent,
      264px 120px transparent, 288px 120px #535353, 312px 120px #535353,
      336px 120px #535353, 360px 120px #535353, 384px 120px #535353,
      408px 120px #535353, 432px 120px #535353, 456px 120px #535353,
      480px 120px #535353, 504px 120px #535353, 528px 120px #535353,
      552px 120px #535353, 0px 144px transparent, 24px 144px transparent,
      48px 144px transparent, 72px 144px transparent, 96px 144px transparent,
      120px 144px transparent, 144px 144px transparent, 168px 144px transparent,
      192px 144px transparent, 216px 144px transparent, 240px 144px transparent,
      264px 144px transparent, 288px 144px #535353, 312px 144px #535353,
      336px 144px #535353, 360px 144px #535353, 384px 144px #535353,
      408px 144px #535353, 432px 144px transparent, 456px 144px transparent,
      480px 144px transparent, 504px 144px transparent, 528px 144px transparent,
      552px 144px transparent, 0px 168px transparent, 24px 168px transparent,
      48px 168px transparent, 72px 168px transparent, 96px 168px transparent,
      120px 168px transparent, 144px 168px transparent, 168px 168px transparent,
      192px 168px transparent, 216px 168px transparent, 240px 168px transparent,
      264px 168px transparent, 288px 168px #535353, 312px 168px #535353,
      336px 168px #535353, 360px 168px #535353, 384px 168px #535353,
      408px 168px #535353, 432px 168px transparent, 456px 168px transparent,
      480px 168px transparent, 504px 168px transparent, 528px 168px transparent,
      552px 168px transparent, 0px 192px transparent, 24px 192px transparent,
      48px 192px transparent, 72px 192px transparent, 96px 192px transparent,
      120px 192px transparent, 144px 192px transparent, 168px 192px transparent,
      192px 192px transparent, 216px 192px transparent, 240px 192px transparent,
      264px 192px transparent, 288px 192px #535353, 312px 192px #535353,
      336px 192px #535353, 360px 192px #535353, 384px 192px #535353,
      408px 192px #535353, 432px 192px #535353, 456px 192px #535353,
      480px 192px #535353, 504px 192px #535353, 528px 192px transparent,
      552px 192px transparent, 0px 216px #535353, 24px 216px transparent,
      48px 216px transparent, 72px 216px transparent, 96px 216px transparent,
      120px 216px transparent, 144px 216px transparent, 168px 216px transparent,
      192px 216px transparent, 216px 216px transparent, 240px 216px #535353,
      264px 216px #535353, 288px 216px #535353, 312px 216px #535353,
      336px 216px #535353, 360px 216px #535353, 384px 216px #535353,
      408px 216px transparent, 432px 216px transparent, 456px 216px transparent,
      480px 216px transparent, 504px 216px transparent, 528px 216px transparent,
      552px 216px transparent, 0px 240px #535353, 24px 240px transparent,
      48px 240px transparent, 72px 240px transparent, 96px 240px transparent,
      120px 240px transparent, 144px 240px transparent, 168px 240px transparent,
      192px 240px #535353, 216px 240px #535353, 240px 240px #535353,
      264px 240px #535353, 288px 240px #535353, 312px 240px #535353,
      336px 240px #535353, 360px 240px #535353, 384px 240px #535353,
      408px 240px transparent, 432px 240px transparent, 456px 240px transparent,
      480px 240px transparent, 504px 240px transparent, 528px 240px transparent,
      552px 240px transparent, 0px 264px #535353, 24px 264px #535353,
      48px 264px transparent, 72px 264px transparent, 96px 264px transparent,
      120px 264px transparent, 144px 264px transparent, 168px 264px #535353,
      192px 264px #535353, 216px 264px #535353, 240px 264px #535353,
      264px 264px #535353, 288px 264px #535353, 312px 264px #535353,
      336px 264px #535353, 360px 264px #535353, 384px 264px #535353,
      408px 264px #535353, 432px 264px #535353, 456px 264px transparent,
      480px 264px transparent, 504px 264px transparent, 528px 264px transparent,
      552px 264px transparent, 0px 288px #535353, 24px 288px #535353,
      48px 288px #535353, 72px 288px transparent, 96px 288px transparent,
      120px 288px transparent, 144px 288px #535353, 168px 288px #535353,
      192px 288px #535353, 216px 288px #535353, 240px 288px #535353,
      264px 288px #535353, 288px 288px #535353, 312px 288px #535353,
      336px 288px #535353, 360px 288px #535353, 384px 288px #535353,
      408px 288px transparent, 432px 288px #535353, 456px 288px transparent,
      480px 288px transparent, 504px 288px transparent, 528px 288px transparent,
      552px 288px transparent, 0px 312px #535353, 24px 312px #535353,
      48px 312px #535353, 72px 312px #535353, 96px 312px #535353,
      120px 312px #535353, 144px 312px #535353, 168px 312px #535353,
      192px 312px #535353, 216px 312px #535353, 240px 312px #535353,
      264px 312px #535353, 288px 312px #535353, 312px 312px #535353,
      336px 312px #535353, 360px 312px #535353, 384px 312px #535353,
      408px 312px transparent, 432px 312px transparent, 456px 312px transparent,
      480px 312px transparent, 504px 312px transparent, 528px 312px transparent,
      552px 312px transparent, 0px 336px #535353, 24px 336px #535353,
      48px 336px #535353, 72px 336px #535353, 96px 336px #535353,
      120px 336px #535353, 144px 336px #535353, 168px 336px #535353,
      192px 336px #535353, 216px 336px #535353, 240px 336px #535353,
      264px 336px #535353, 288px 336px #535353, 312px 336px #535353,
      336px 336px #535353, 360px 336px #535353, 384px 336px #535353,
      408px 336px transparent, 432px 336px transparent, 456px 336px transparent,
      480px 336px transparent, 504px 336px transparent, 528px 336px transparent,
      552px 336px transparent, 0px 360px transparent, 24px 360px #535353,
      48px 360px #535353, 72px 360px #535353, 96px 360px #535353,
      120px 360px #535353, 144px 360px #535353, 168px 360px #535353,
      192px 360px #535353, 216px 360px #535353, 240px 360px #535353,
      264px 360px #535353, 288px 360px #535353, 312px 360px #535353,
      336px 360px #535353, 360px 360px #535353, 384px 360px #535353,
      408px 360px transparent, 432px 360px transparent, 456px 360px transparent,
      480px 360px transparent, 504px 360px transparent, 528px 360px transparent,
      552px 360px transparent, 0px 384px transparent, 24px 384px transparent,
      48px 384px #535353, 72px 384px #535353, 96px 384px #535353,
      120px 384px #535353, 144px 384px #535353, 168px 384px #535353,
      192px 384px #535353, 216px 384px #535353, 240px 384px #535353,
      264px 384px #535353, 288px 384px #535353, 312px 384px #535353,
      336px 384px #535353, 360px 384px #535353, 384px 384px transparent,
      408px 384px transparent, 432px 384px transparent, 456px 384px transparent,
      480px 384px transparent, 504px 384px transparent, 528px 384px transparent,
      552px 384px transparent, 0px 408px transparent, 24px 408px transparent,
      48px 408px transparent, 72px 408px #535353, 96px 408px #535353,
      120px 408px #535353, 144px 408px #535353, 168px 408px #535353,
      192px 408px #535353, 216px 408px #535353, 240px 408px #535353,
      264px 408px #535353, 288px 408px #535353, 312px 408px #535353,
      336px 408px transparent, 360px 408px transparent, 384px 408px transparent,
      408px 408px transparent, 432px 408px transparent, 456px 408px transparent,
      480px 408px transparent, 504px 408px transparent, 528px 408px transparent,
      552px 408px transparent, 0px 432px transparent, 24px 432px transparent,
      48px 432px transparent, 72px 432px transparent, 96px 432px #535353,
      120px 432px #535353, 144px 432px #535353, 168px 432px #535353,
      192px 432px #535353, 216px 432px #535353, 240px 432px #535353,
      264px 432px #535353, 288px 432px #535353, 312px 432px #535353,
      336px 432px transparent, 360px 432px transparent, 384px 432px transparent,
      408px 432px transparent, 432px 432px transparent, 456px 432px transparent,
      480px 432px transparent, 504px 432px transparent, 528px 432px transparent,
      552px 432px transparent, 0px 456px transparent, 24px 456px transparent,
      48px 456px transparent, 72px 456px transparent, 96px 456px transparent,
      120px 456px #535353, 144px 456px #535353, 168px 456px #535353,
      192px 456px #535353, 216px 456px #535353, 240px 456px #535353,
      264px 456px #535353, 288px 456px #535353, 312px 456px transparent,
      336px 456px transparent, 360px 456px transparent, 384px 456px transparent,
      408px 456px transparent, 432px 456px transparent, 456px 456px transparent,
      480px 456px transparent, 504px 456px transparent, 528px 456px transparent,
      552px 456px transparent, 0px 480px transparent, 24px 480px transparent,
      48px 480px transparent, 72px 480px transparent, 96px 480px transparent,
      120px 480px transparent, 144px 480px #535353, 168px 480px #535353,
      192px 480px #535353, 216px 480px transparent, 240px 480px transparent,
      264px 480px #535353, 288px 480px #535353, 312px 480px transparent,
      336px 480px transparent, 360px 480px transparent, 384px 480px transparent,
      408px 480px transparent, 432px 480px transparent, 456px 480px transparent,
      480px 480px transparent, 504px 480px transparent, 528px 480px transparent,
      552px 480px transparent, 0px 504px transparent, 24px 504px transparent,
      48px 504px transparent, 72px 504px transparent, 96px 504px transparent,
      120px 504px transparent, 144px 504px transparent, 168px 504px #535353,
      192px 504px #535353, 216px 504px #535353, 240px 504px transparent,
      264px 504px transparent, 288px 504px #535353, 312px 504px transparent,
      336px 504px transparent, 360px 504px transparent, 384px 504px transparent,
      408px 504px transparent, 432px 504px transparent, 456px 504px transparent,
      480px 504px transparent, 504px 504px transparent, 528px 504px transparent,
      552px 504px transparent, 0px 528px transparent, 24px 528px transparent,
      48px 528px transparent, 72px 528px transparent, 96px 528px transparent,
      120px 528px transparent, 144px 528px transparent, 168px 528px transparent,
      192px 528px transparent, 216px 528px transparent, 240px 528px transparent,
      264px 528px transparent, 288px 528px #535353, 312px 528px transparent,
      336px 528px transparent, 360px 528px transparent, 384px 528px transparent,
      408px 528px transparent, 432px 528px transparent, 456px 528px transparent,
      480px 528px transparent, 504px 528px transparent, 528px 528px transparent,
      552px 528px transparent, 0px 552px transparent, 24px 552px transparent,
      48px 552px transparent, 72px 552px transparent, 96px 552px transparent,
      120px 552px transparent, 144px 552px transparent, 168px 552px transparent,
      192px 552px transparent, 216px 552px transparent, 240px 552px transparent,
      264px 552px transparent, 288px 552px #535353, 312px 552px #535353,
      336px 552px transparent, 360px 552px transparent, 384px 552px transparent,
      408px 552px transparent, 432px 552px transparent, 456px 552px transparent,
      480px 552px transparent, 504px 552px transparent, 528px 552px transparent,
      552px 552px transparent;
  }
}

/* ===================== 太极已下架 ===================== */

/* ===================== 小狗（下，居中） ===================== */
.dog-stage {
  position: absolute;
  left: 0;
  width: 236px;
  bottom: 0;
  height: 130px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}
.dog-main {
  position: relative;
  width: 23.5vmax;
  height: 23.5vmax;
  display: flex;
  justify-content: center;
  align-items: center;
  transform: scale(0.42);
  transform-origin: center bottom;
}

.leg {
  position: absolute;
  bottom: 0;
  width: 2vmax;
  height: 2.125vmax;
}
.paw {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 1.95vmax;
  height: 1.875vmax;
  overflow: hidden;
}
.paw::before {
  content: "";
  position: absolute;
  width: 3.75vmax;
  height: 3.75vmax;
  border-radius: 50%;
}
.top {
  position: absolute;
  bottom: 0;
  left: 0.75vmax;
  height: 4.5vmax;
  width: 2.625vmax;
  border-top-left-radius: 1.425vmax;
  border-top-right-radius: 1.425vmax;
  transform-origin: bottom right;
  transform: rotateZ(90deg) translateX(-0.1vmax) translateY(1.5vmax);
  z-index: -1;
  background-image: linear-gradient(70deg, transparent 20%, #ff8b56 20%);
}
.dog {
  position: relative;
  width: 22.5vmax;
  height: 8.25vmax;
}
.dog::before {
  content: "";
  position: absolute;
  bottom: -0.75vmax;
  right: -0.15vmax;
  width: 100%;
  height: 1.5vmax;
  background-color: rgba(28, 49, 48, 0.1);
  border-radius: 50%;
  z-index: -1000;
  animation: shadow 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__head {
  position: absolute;
  left: 4.5vmax;
  bottom: 0;
  width: 9.75vmax;
  height: 8.25vmax;
  border-top-left-radius: 4.05vmax;
  border-top-right-radius: 4.05vmax;
  border-bottom-right-radius: 3.3vmax;
  border-bottom-left-radius: 3.3vmax;
  background-color: #ff8147;
  animation: head 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__head-c {
  position: absolute;
  left: 1.5vmax;
  bottom: 0;
  width: 9.75vmax;
  height: 8.25vmax;
  animation: head 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
  z-index: -1;
}
.dog__snout {
  position: absolute;
  left: -1.5vmax;
  bottom: 0;
  width: 7.5vmax;
  height: 3.75vmax;
  border-top-right-radius: 3vmax;
  border-bottom-right-radius: 3vmax;
  border-bottom-left-radius: 4.5vmax;
  background-color: #d7dbd2;
  animation: snout 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__snout::before {
  content: "";
  position: absolute;
  left: -0.1125vmax;
  top: -0.15vmax;
  width: 1.875vmax;
  height: 1.125vmax;
  border-top-right-radius: 3vmax;
  border-bottom-right-radius: 3vmax;
  border-bottom-left-radius: 4.5vmax;
  background-color: #1c3130;
  animation: snout-b 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__nose {
  position: absolute;
  top: -1.95vmax;
  left: 40%;
  width: 0.75vmax;
  height: 2.4vmax;
  border-radius: 0.525vmax;
  transform-origin: bottom;
  transform: rotateZ(10deg);
  background-color: #d7dbd2;
}
.dog__eye-l,
.dog__eye-r {
  position: absolute;
  top: -0.9vmax;
  width: 0.675vmax;
  height: 0.375vmax;
  border-radius: 50%;
  background-color: #1c3130;
  animation: eye 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__eye-l { left: 27%; }
.dog__eye-r { left: 65%; }
.dog__ear-l,
.dog__ear-r {
  position: absolute;
  width: 10.5vmax;
  height: 3.375vmax;
  border-top-left-radius: 0vmax;
  border-top-right-radius: 0vmax;
  border-bottom-right-radius: 3.3vmax;
  border-bottom-left-radius: 3.3vmax;
  background-color: #e26538;
}
.dog__ear-l {
  top: 1.5vmax;
  left: 6vmax;
  transform-origin: bottom left;
  transform: rotateZ(-50deg);
  z-index: -1;
  animation: ear-l 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__ear-r {
  top: 1.5vmax;
  right: 3vmax;
  transform-origin: bottom right;
  transform: rotateZ(20deg);
  z-index: -2;
  animation: ear-r 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__body {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  position: absolute;
  bottom: 0.3vmax;
  left: 3.75vmax;
  width: 18.75vmax;
  height: 7.2vmax;
  border-top-left-radius: 3vmax;
  border-top-right-radius: 6vmax;
  border-bottom-right-radius: 1.5vmax;
  border-bottom-left-radius: 6vmax;
  background-color: #ff702e;
  z-index: -2;
  animation: body 10s cubic-bezier(0.3, 0.41, 0.18, 1.01) infinite;
}
.dog__tail {
  position: absolute;
  right: -3vmax;
  height: 1.5vmax;
  width: 4.5vmax;
  background-color: #e96839;
  border-radius: 1.5vmax;
}
.dog__paws {
  position: absolute;
  bottom: 0;
  left: 7.5vmax;
  width: 12vmax;
  height: 3vmax;
}
.dog__bl-leg { left: -3vmax; z-index: -10; }
.dog__bl-paw::before { background-color: #bec4b6; }
.dog__bl-top { background-image: linear-gradient(80deg, transparent 20%, #e96839 20%); }
.dog__fl-leg { z-index: 10; left: 0; }
.dog__fl-paw::before { background-color: #d7dbd2; }
.dog__fr-leg { right: 0; }
.dog__fr-paw::before { background-color: #d7dbd2; }

@keyframes head {
  0%, 10%, 20%, 26%, 28%, 90%, 100% {
    height: 8.25vmax;
    bottom: 0;
    transform-origin: bottom right;
    transform: rotateZ(0);
  }
  5%, 15%, 22%, 24%, 30% { height: 8.1vmax; }
  32%, 50% { height: 8.25vmax; }
  55%, 60% {
    bottom: 0.75vmax;
    transform-origin: bottom right;
    transform: rotateZ(0);
  }
  70%, 80% {
    bottom: 0.75vmax;
    transform-origin: bottom right;
    transform: rotateZ(10deg);
  }
}
@keyframes body {
  0%, 10%, 20%, 26%, 28%, 32%, 100% { height: 7.2vmax; }
  5%, 15%, 22%, 24%, 30% { height: 7.05vmax; }
}
@keyframes ear-l {
  0%, 10%, 20%, 26%, 28%, 82%, 100% { transform: rotateZ(-50deg); }
  5%, 15%, 22%, 24% { transform: rotateZ(-48deg); }
  30%, 31% { transform: rotateZ(-30deg); }
  32%, 80% { transform: rotateZ(-60deg); }
}
@keyframes ear-r {
  0%, 10%, 20%, 26%, 28% { transform: rotateZ(20deg); }
  5%, 15%, 22%, 24% { transform: rotateZ(18deg); }
  30%, 31% { transform: rotateZ(10deg); }
  32% { transform: rotateZ(25deg); }
}
@keyframes snout {
  0%, 10%, 20%, 26%, 28%, 82%, 100% { height: 3.75vmax; }
  5%, 15%, 22%, 24% { height: 3.45vmax; }
}
@keyframes snout-b {
  0%, 10%, 20%, 26%, 28%, 98%, 100% { width: 1.875vmax; }
  5%, 15%, 22%, 24% { width: 1.8vmax; }
  34%, 98% { width: 1.275vmax; }
}
@keyframes shadow {
  0%, 10%, 20%, 26%, 28%, 30%, 84%, 100% { width: 99%; }
  5%, 15%, 22%, 24% { width: 101%; }
  34%, 81% { width: 96%; }
}
@keyframes eye {
  0%, 30% { width: 0.675vmax; height: 0.3vmax; }
  32%, 59%, 90%, 100% {
    width: 0.525vmax;
    height: 0.525vmax;
    transform: translateY(0);
  }
  60%, 75% { transform: translateY(-0.3vmax); }
  80%, 85% { transform: translateY(0.15vmax); }
}

/* ===================== 响应式 / 无障碍 ===================== */
@media (max-width: 959px) {
  .side-pets { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .loader, .yy, .dot,
  .dog::before, .dog__head, .dog__head-c, .dog__snout, .dog__snout::before,
  .dog__eye-l, .dog__eye-r, .dog__ear-l, .dog__ear-r, .dog__body {
    animation: none;
  }
}
</style>
