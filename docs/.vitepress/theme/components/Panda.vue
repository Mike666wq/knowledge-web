<script setup>
// 熊猫：黑白配色的眨眼小熊猫（改造自 Uiverse panda）
// 放在首页「外观设置」区块，与明暗主题卡并排——黑白配色呼应日夜切换
// 纯装饰：眨眼 / 耳朵抖动 / 眼珠东张西望 / 微笑
</script>

<template>
  <div class="panda-container" aria-hidden="true">
    <div class="ear ear-left"></div>
    <div class="ear ear-right"></div>
    <div class="panda-head">
      <div class="eye-patch eye-patch-left"></div>
      <div class="eye-patch eye-patch-right"></div>
      <div class="eye eye-left"></div>
      <div class="eye eye-right"></div>
      <div class="pupil pupil-left"></div>
      <div class="pupil pupil-right"></div>
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
  perspective: 1000px;
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
    0 3px 10px rgba(0, 0, 0, 0.1),
    inset 0 -5px 20px rgba(0, 0, 0, 0.05);
}

.ear {
  position: absolute;
  width: 70px;
  height: 70px;
  background: #222;
  border: 4px solid #222;
  border-radius: 50%;
  z-index: 3;
  box-shadow: inset 0 -5px 10px rgba(0, 0, 0, 0.3);
}

.ear-left {
  top: 30px;
  left: 40px;
  transform: rotate(-15deg);
  animation: ear-twitch-left 3s ease-in-out infinite;
}

.ear-right {
  top: 30px;
  left: 190px;
  transform: rotate(15deg);
  animation: ear-twitch-right 3.5s ease-in-out infinite;
}

.eye-patch {
  position: absolute;
  width: 60px;
  height: 70px;
  background: #222;
  border-radius: 50%;
  z-index: 5;
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
  border-radius: 50%;
  z-index: 6;
  animation: blink 4s linear infinite;
}

.eye-left {
  top: 75px;
  left: 45px;
}

.eye-right {
  top: 75px;
  left: 125px;
}

.pupil {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #222;
  border-radius: 50%;
  z-index: 7;
  animation: look-around 8s ease-in-out infinite;
}

.pupil-left {
  top: 82px;
  left: 53px;
}

.pupil-right {
  top: 82px;
  left: 133px;
}

.nose {
  position: absolute;
  width: 30px;
  height: 25px;
  background: #222;
  border-radius: 50%;
  top: 110px;
  left: 85px;
  z-index: 8;
  box-shadow: inset 0 -3px 5px rgba(0, 0, 0, 0.3);
}

.mouth {
  position: absolute;
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 12px solid #222;
  border-radius: 50%;
  top: 135px;
  left: 92px;
  z-index: 7;
  transform: rotate(180deg);
  animation: smile 5s ease-in-out infinite;
}

@keyframes blink {
  0%,
  45%,
  55%,
  100% {
    height: 30px;
  }
  48%,
  52% {
    height: 5px;
  }
}

@keyframes look-around {
  0%,
  100% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(3px, 3px);
  }
  50% {
    transform: translate(0, -3px);
  }
  75% {
    transform: translate(-3px, 2px);
  }
}

@keyframes smile {
  0%,
  100% {
    transform: rotate(180deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.2);
  }
}

@keyframes ear-twitch-left {
  0%,
  100% {
    transform: rotate(-15deg);
  }
  50% {
    transform: rotate(-25deg);
  }
}

@keyframes ear-twitch-right {
  0%,
  100% {
    transform: rotate(15deg);
  }
  50% {
    transform: rotate(25deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .ear-left,
  .ear-right,
  .eye,
  .pupil,
  .mouth {
    animation: none;
  }
}
</style>
