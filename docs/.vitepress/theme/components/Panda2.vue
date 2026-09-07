<script setup>
// 熊猫二号：眼皮眨眼版（eye-lid 翻转眨眼 / 嘴巴微笑展宽）
// 与一号熊猫（Panda.vue：眼珠转动/耳朵抖动）一左一右夹住「主题模式」卡
</script>

<template>
  <div class="panda-container" aria-hidden="true">
    <div class="ear ear-left"></div>
    <div class="ear ear-right"></div>
    <div class="panda-head">
      <div class="eye-patch eye-patch-left"></div>
      <div class="eye-patch eye-patch-right"></div>
      <div class="eye eye-left">
        <div class="eyelid"></div>
        <div class="pupil"></div>
      </div>
      <div class="eye eye-right">
        <div class="eyelid"></div>
        <div class="pupil"></div>
      </div>
      <div class="nose"></div>
      <div class="mouth"></div>
    </div>
  </div>
</template>

<style scoped>
.panda-container {
  position: relative;
  width: 300px;
  height: 280px;
  pointer-events: none;
}

.panda-head {
  position: absolute;
  width: 200px;
  height: 180px;
  background: white;
  border: 4px solid #222;
  border-radius: 50%;
  top: 50px;
  left: 50px;
  z-index: 4;
  box-shadow:
    0 5px 15px rgba(0, 0, 0, 0.1),
    inset 0 -8px 25px rgba(0, 0, 0, 0.08);
}

.ear {
  position: absolute;
  width: 70px;
  height: 70px;
  background: #222;
  border: 4px solid #222;
  border-radius: 50%;
  z-index: 3;
  box-shadow: inset 0 -8px 15px rgba(0, 0, 0, 0.3);
}

.ear-left {
  top: 30px;
  left: 40px;
  transform: rotate(-15deg);
}

.ear-right {
  top: 30px;
  left: 190px;
  transform: rotate(15deg);
}

.eye-patch {
  position: absolute;
  width: 60px;
  height: 70px;
  background: #222;
  border-radius: 50%;
  z-index: 5;
  box-shadow: inset 0 -5px 10px rgba(0, 0, 0, 0.4);
}

.eye-patch-left {
  top: 60px;
  left: 30px;
}

.eye-patch-right {
  top: 60px;
  left: 110px;
}

.eye {
  position: absolute;
  width: 25px;
  height: 30px;
  background: white;
  border-radius: 60%;
  z-index: 6;
  overflow: hidden;
}

.eye-left {
  top: 75px;
  left: 45px;
}

.eye-right {
  top: 75px;
  left: 125px;
}

.eyelid {
  position: absolute;
  width: 100%;
  height: 100%;
  background: #222;
  border-radius: 80%;
  z-index: 7;
  transform-origin: top;
  animation: blink 4s ease-in-out infinite;
}

.pupil {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #000;
  border-radius: 50%;
  z-index: 6;
  top: 9px;
  left: 6px;
}

.nose {
  position: absolute;
  width: 30px;
  height: 25px;
  background: #222;
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  top: 110px;
  left: 85px;
  z-index: 8;
  box-shadow: inset 0 -3px 8px rgba(0, 0, 0, 0.4);
}

.mouth {
  position: absolute;
  width: 40px;
  height: 20px;
  border-bottom: 3px solid #222;
  border-radius: 0 0 50% 50%;
  top: 135px;
  left: 80px;
  z-index: 7;
  transform-origin: center;
  animation: smile 4s ease-in-out infinite;
}

@keyframes blink {
  0%,
  30% {
    transform: scaleY(1);
  }
  35%,
  65% {
    transform: scaleY(0);
  }
  70%,
  100% {
    transform: scaleY(1);
  }
}

@keyframes smile {
  0%,
  30% {
    width: 40px;
    left: 80px;
  }
  35%,
  65% {
    width: 60px;
    left: 70px;
  }
  70%,
  100% {
    width: 40px;
    left: 80px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .eyelid,
  .mouth {
    animation: none;
  }
}
</style>
