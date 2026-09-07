<script setup>
// 像素小幽灵（改造自 Uiverse pixel ghost，支持红/蓝双色变体）
// - color="red"（默认）红色身体 + 白眼 + 蓝瞳
// - color="blue" 蓝色身体 + 蓝眼 + 浅米瞳 + 像素嘴巴
// 放在目录树左侧的左列装饰位（默认）
// 用 class 透传可换位（.ghost-right 放到右侧列）
const props = defineProps({
  color: { type: String, default: 'red' },
})
</script>

<template>
  <div class="ghost-stage" :class="['g-' + props.color]" aria-hidden="true">
    <div id="ghost">
      <div id="red">
        <div id="pupil"></div>
        <div id="pupil1"></div>
        <div id="eye"></div>
        <div id="eye1"></div>
        <div id="top0"></div>
        <div id="top1"></div>
        <div id="top2"></div>
        <div id="top3"></div>
        <div id="top4"></div>
        <div id="st0"></div>
        <div id="st1"></div>
        <div id="st2"></div>
        <div id="st3"></div>
        <div id="st4"></div>
        <div id="st5"></div>
        <div id="an1"></div>
        <div id="an2"></div>
        <div id="an3"></div>
        <div id="an4"></div>
        <div id="an5"></div>
        <div id="an6"></div>
        <div id="an7"></div>
        <div id="an8"></div>
        <div id="an9"></div>
        <div id="an10"></div>
        <div id="an11"></div>
        <div id="an12"></div>
        <div id="an13"></div>
        <div id="an14"></div>
        <div id="an15"></div>
        <div id="an16"></div>
        <div id="an17"></div>
        <div id="an18"></div>
        <!-- 嘴巴（只在蓝色变体显示） -->
        <div id="mouthstart"></div>
        <div id="mouth1"></div>
        <div id="mouth2"></div>
        <div id="mouth3"></div>
        <div id="mouth4"></div>
        <div id="mouth5"></div>
        <div id="mouthend"></div>
      </div>
      <div id="shadow"></div>
    </div>
  </div>
</template>

<style scoped>
/* 默认位置：左列与目录树首组齐平；用 inline style 可覆盖 top/left/right */
.ghost-stage {
  position: fixed;
  left: 0;
  top: 96px;
  width: 128px;
  height: 150px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  z-index: 55;
  pointer-events: none;
  overflow: visible;
}

#ghost {
  position: relative;
  scale: 0.8;
}

#red {
  animation: ghost-jump 0.5s infinite;
  position: relative;
  width: 140px;
  height: 140px;
  display: grid;
  grid-template-columns: repeat(14, 1fr);
  grid-template-rows: repeat(14, 1fr);
  grid-column-gap: 0;
  grid-row-gap: 0;
  grid-template-areas:
    "a1  a2  a3  a4  a5  top0  top0  top0  top0  a10 a11 a12 a13 a14"
    "b1  b2  b3  top1 top1 top1 top1 top1 top1 top1 top1 b12 b13 b14"
    "c1 c2 top2 top2 top2 top2 top2 top2 top2 top2 top2 top2 c13 c14"
    "d1 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 d14"
    "e1 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 e14"
    "f1 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 top3 f14"
    "top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4"
    "top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4"
    "top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4"
    "top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4"
    "top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4"
    "top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4 top4"
    "st0 st0 an4 st1 an7 st2 an10 an10 st3 an13 st4 an16 st5 st5"
    "an1 an2 an3 an5 an6 an8 an9 an9 an11 an12 an14 an15 an17 an18";
}

/* 像素格 grid-area 分配（红/蓝共用同一网格模板） */
#top0 { grid-area: top0; } #top1 { grid-area: top1; } #top2 { grid-area: top2; }
#top3 { grid-area: top3; } #top4 { grid-area: top4; }
#st0 { grid-area: st0; } #st1 { grid-area: st1; } #st2 { grid-area: st2; }
#st3 { grid-area: st3; } #st4 { grid-area: st4; } #st5 { grid-area: st5; }
#an1 { grid-area: an1; } #an2 { grid-area: an2; } #an3 { grid-area: an3; } #an4 { grid-area: an4; }
#an5 { grid-area: an5; } #an6 { grid-area: an6; } #an7 { grid-area: an7; } #an8 { grid-area: an8; }
#an9 { grid-area: an9; } #an10 { grid-area: an10; } #an11 { grid-area: an11; } #an12 { grid-area: an12; }
#an13 { grid-area: an13; } #an14 { grid-area: an14; } #an15 { grid-area: an15; }
#an16 { grid-area: an16; } #an17 { grid-area: an17; } #an18 { grid-area: an18; }

@keyframes ghost-jump {
  0%, 49% { transform: translateY(0); }
  50%, 100% { transform: translateY(-10px); }
}

/* 默认（红色）身体 + 白眼 + 蓝瞳 */
.g-red #top0, .g-red #top1, .g-red #top2, .g-red #top3, .g-red #top4,
.g-red #st0, .g-red #st1, .g-red #st2, .g-red #st3, .g-red #st4, .g-red #st5 {
  background-color: red;
}
.g-red #eye, .g-red #eye1 { width: 40px; height: 50px; position: absolute; top: 30px; }
.g-red #eye { left: 10px; } .g-red #eye1 { right: 10px; }
.g-red #eye::before, .g-red #eye1::before {
  content: ""; background-color: white; width: 20px; height: 50px;
  transform: translateX(10px); display: block; position: absolute;
}
.g-red #eye::after, .g-red #eye1::after {
  content: ""; background-color: white; width: 40px; height: 30px;
  transform: translateY(10px); display: block; position: absolute;
}
.g-red #pupil, .g-red #pupil1 {
  width: 20px; height: 20px; background-color: blue; position: absolute; top: 50px; z-index: 1;
}
.g-red #pupil { left: 10px; } .g-red #pupil1 { right: 10px; }
.g-red [id^="mouth"] { display: none; }

/* 蓝色变体：蓝身体 + 蓝眼 + 浅米瞳 + 像素嘴巴 */
.g-blue #top0, .g-blue #top1, .g-blue #top2, .g-blue #top3, .g-blue #top4,
.g-blue #st0, .g-blue #st1, .g-blue #st2, .g-blue #st3, .g-blue #st4, .g-blue #st5 {
  background-color: blue;
}
.g-blue #eye, .g-blue #eye1 { width: 40px; height: 50px; position: absolute; top: 30px; }
.g-blue #eye { left: 20px; } .g-blue #eye1 { right: 20px; }
.g-blue #eye::before, .g-blue #eye1::before {
  content: ""; background-color: blue; width: 20px; height: 50px;
  transform: translateX(10px); display: block; position: absolute;
}
.g-blue #eye::after, .g-blue #eye1::after {
  content: ""; background-color: blue; width: 40px; height: 30px;
  transform: translateY(10px); display: block; position: absolute;
}
.g-blue #pupil, .g-blue #pupil1 {
  width: 20px; height: 20px; background-color: #fcc78b; position: absolute; top: 50px; z-index: 1;
}
.g-blue #pupil { left: 30px; } .g-blue #pupil1 { right: 30px; }
.g-blue [id^="mouth"] { display: block; }
.g-blue #mouthstart, .g-blue #mouthend { width: 10px; height: 10px; background-color: #fcc78b; position: absolute; z-index: 1; top: 100px; }
.g-blue #mouthstart { left: 10px; }
.g-blue #mouth1 { width: 20px; height: 10px; background-color: #fcc78b; position: absolute; z-index: 1; top: 90px; left: 20px; }
.g-blue #mouth2 { width: 20px; height: 10px; background-color: #fcc78b; position: absolute; z-index: 1; top: 100px; left: 40px; }
.g-blue #mouth3 { width: 20px; height: 10px; background-color: #fcc78b; position: absolute; z-index: 1; top: 90px; left: 60px; }
.g-blue #mouth4 { width: 20px; height: 10px; background-color: #fcc78b; position: absolute; z-index: 1; top: 100px; left: 80px; }
.g-blue #mouth5 { width: 20px; height: 10px; background-color: #fcc78b; position: absolute; z-index: 1; top: 90px; left: 100px; }
.g-blue #mouthend { left: 120px; }

#shadow {
  background-color: black;
  width: 140px; height: 140px; position: absolute;
  border-radius: 50%;
  transform: rotateX(80deg);
  filter: blur(20px);
  top: 80%;
  animation: shadow-pulse 0.5s infinite;
}
@keyframes shadow-pulse {
  0%, 49% { opacity: 0.5; }
  50%, 100% { opacity: 0.2; }
}

/* 像素闪烁（红色版本的左右对称，蓝色用统一的 flicker-on/off） */
.g-red #an1, .g-red #an18, .g-red #an6, .g-red #an12, .g-red #an7, .g-red #an13, .g-red #an8, .g-red #an11 {
  animation: flicker-on 0.5s infinite;
}
.g-red #an2, .g-red #an3, .g-red #an4, .g-red #an10, .g-red #an9, .g-red #an5, .g-red #an15, .g-red #an16, .g-red #an17 {
  animation: flicker-off 0.5s infinite;
}
.g-blue #an1, .g-blue #an18, .g-blue #an6, .g-blue #an12, .g-blue #an7, .g-blue #an13, .g-blue #an8, .g-blue #an11 {
  animation: flicker-on 0.5s infinite;
}
.g-blue #an2, .g-blue #an3, .g-blue #an4, .g-blue #an10, .g-blue #an9, .g-blue #an5, .g-blue #an15, .g-blue #an16, .g-blue #an17 {
  animation: flicker-off 0.5s infinite;
}
@keyframes flicker-on {
  0%, 49% { background-color: var(--ghost-color, red); }
  50%, 100% { background-color: transparent; }
}
@keyframes flicker-off {
  0%, 49% { background-color: transparent; }
  50%, 100% { background-color: var(--ghost-color, red); }
}
.g-red { --ghost-color: red; }
.g-blue { --ghost-color: blue; }

#pupil, #pupil1 {
  width: 20px; height: 20px; position: absolute; top: 50px; z-index: 1;
  animation: eyes-move 3s infinite;
}
@keyframes eyes-move {
  0%, 49% { transform: translateX(0); }
  50%, 99% { transform: translateX(10px); }
  100% { transform: translateX(0); }
}

@media (max-width: 959px) {
  .ghost-stage { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  #red, #shadow, #pupil, #pupil1 { animation: none; }
}
</style>