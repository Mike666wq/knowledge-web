<script setup>
// 霓虹绿卡（Uiverse viper 风格）：呼吸光晕 + 滚动文字 + 六边形 logo + hover 3D 翻转
</script>

<template>
  <div class="viper-card">
    <div class="v-bg">
      <div class="v-hex">
        <div class="v-logo-spin"></div>
        <div class="v-logo-inside">
          <div class="v-fmark"></div>
          <div class="v-fmark"></div>
        </div>
      </div>
      <div class="v-blur-area"></div>
      <div class="v-marquee">
        <div class="v-marquee-inner" aria-hidden="true">
          <span class="v-viper-text">viper viper viper viper</span>
          <span class="v-viper-text">viper viper viper viper</span>
          <span class="v-viper-text">viper viper viper viper</span>
        </div>
      </div>
    </div>
    <div class="v-mist-wrap">
      <div class="v-mist"></div>
    </div>
    <strong class="v-text-ext">Lorem ipsum</strong>
    <strong class="v-text-border">Lorem ipsum</strong>
  </div>
</template>

<style scoped>
.viper-card {
  z-index: 0;
  position: relative;
  padding: 1rem;
  width: 300px;
  height: 350px;
  margin: 0 auto;
  box-sizing: border-box;
  background: transparent;
  backdrop-filter: blur(40px);
  border-radius: 0 2rem;
  background-image: radial-gradient(rgba(33,33,33,0.54), rgba(33,33,33,0.8)), linear-gradient(35deg, #124926 62%, #57ff94 100%);
  background-origin: border-box;
  background-clip: content-box, border-box;
  box-shadow: 1px 1px 3rem #57ff95;
  animation: pulse 3s infinite;
  transition: transform 0.5s;
}
.viper-card:hover { transform: rotateY(20deg); }

.v-bg {
  position: relative;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 0 0.8rem;
  background: linear-gradient(346.80deg, #124926 30%, #165c30 30%, rgba(255,70,84,0) 30%, rgba(255,70,84,0) 32%, #124926 32%, #124926 35%, transparent 35%);
}

.v-hex {
  display: flex;
  position: absolute;
  width: 3.5rem;
  height: 3em;
  top: 1rem;
  left: 1rem;
  align-items: center;
  justify-content: center;
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}
.v-logo-spin {
  position: absolute;
  width: 200%;
  height: 200%;
  background: conic-gradient(#228647 0%, #fff 10%, #7bffac 25%, #0d381c 50%, #1ccc5d 70%, #69b384 90%);
  animation: spin 5s linear infinite;
}
.v-logo-inside {
  display: flex;
  width: 85%;
  height: 85%;
  align-items: center;
  justify-content: center;
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
  background-color: #212121;
}
.v-fmark {
  position: absolute;
  width: 30px;
  height: 30px;
  background-color: #57ff95;
}
.v-fmark:nth-child(1) { clip-path: polygon(0 10%, 70% 90%, 35% 90%, 0 50%); }
.v-fmark:nth-child(2) { clip-path: polygon(100% 10%, 100% 50%, 88% 65%, 55% 65%); }

.v-blur-area {
  display: block;
  position: absolute;
  z-index: -1;
  inset: 0;
  border-radius: 0 1rem;
  backdrop-filter: blur(3px);
  background: linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.27) 100%);
}

.v-marquee {
  top: 0;
  z-index: -5;
  width: 100%;
  height: 100%;
  position: absolute;
  overflow: hidden;
  --offset: 2rem;
  --move-initial: calc(-20% + var(--offset));
  --move-final: calc(-85% + var(--offset));
  border-radius: 0 1rem;
  filter: opacity(0.3);
}
.v-marquee-inner {
  width: fit-content;
  display: flex;
  position: relative;
  transform: translate3d(var(--move-initial), 0, 0);
  animation: slide 60s linear infinite;
  border-radius: 0 1rem;
}
.v-viper-text {
  display: flex;
  text-transform: uppercase;
  font-family: 'Open Sans Pro', sans-serif;
  font-size: 8rem;
  font-weight: 900;
  align-items: center;
  line-height: 0.9em;
  color: transparent;
  -webkit-text-stroke-width: 2px;
  -webkit-text-stroke-color: rgb(255, 255, 255);
  padding-right: 0.2em;
}

.v-mist-wrap {
  position: absolute;
  width: 450px;
  height: 150px;
  overflow: hidden;
  filter: blur(1rem);
  top: 60%;
  left: 0;
}
.v-mist {
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(131,255,158,0.63) 10%, rgba(255,255,255,0) 50%);
  animation: mist 10s infinite both;
}

.v-text-ext {
  z-index: -1;
  display: flex;
  position: absolute;
  inset: 1rem;
  -webkit-text-stroke-width: 1px;
  -webkit-text-stroke-color: #ffffff;
  background: linear-gradient(346.80deg, rgb(255,255,255) 30%, #fff 30%, #fff 30%, #fff 32%, #fff 32%, #fff 35%);
  background-size: cover;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  padding: 9rem 0 0 0.5rem;
  font-size: 1.6rem;
  font-weight: 900;
  align-items: center;
  text-transform: uppercase;
  letter-spacing: 0.5rem;
  font-family: 'Open Sans Pro', sans-serif;
}
.v-text-border {
  position: absolute;
  top: 15.35rem;
  left: 1.5rem;
  width: 100%;
  height: fit-content;
  color: transparent;
  -webkit-text-stroke-width: 1px;
  -webkit-text-stroke-color: rgb(255, 255, 255);
  background: linear-gradient(90deg, transparent 100%, #ffffff 65%);
  background-size: cover;
  background-clip: text;
  -webkit-background-clip: text;
  font-size: 1.6rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.5rem;
  font-family: 'Open Sans Pro', sans-serif;
  display: flex;
  align-items: center;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes mist {
  0%   { transform: translateX(-50%) translateY(0%) scaleY(0.7) rotate(0deg); opacity: 0.3; }
  50%  { transform: translateX(0%)   translateY(50%) scaleY(-10.3) rotate(20deg); opacity: 0.5; }
  100% { transform: translateX(-50%) translateY(0%) scaleY(0.7) rotate(-20deg); opacity: 0.3; }
}
@keyframes pulse {
  0%   { box-shadow: 0 0 1rem #57ff95; }
  70%  { box-shadow: 0 0 2rem #57ff95; }
  100% { box-shadow: 0 0 1rem #57ff95; }
}
@keyframes slide {
  0%   { transform: translate3d(var(--move-initial), 0, 0); }
  100% { transform: translate3d(var(--move-final), 0, 0); }
}
</style>
