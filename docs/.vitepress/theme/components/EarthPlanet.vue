<script setup>
// 纯 CSS 地球：圆形裁剪遮罩 + 蓝色海洋 + 绿色大陆（绝对定位） + 白色云带 + 表面水平平移模拟自转
// 之前 base64 出来的暗黑球问题已弃用
</script>

<template>
  <div class="earth-stage" aria-hidden="true">
    <div class="earth-atmosphere"></div>
    <div class="earth-globe">
      <div class="earth-surface">
        <!-- 大陆：绿色/棕色不规则形状，绝对定位 -->
        <div class="continent c1"></div>
        <div class="continent c2"></div>
        <div class="continent c3"></div>
        <div class="continent c4"></div>
        <div class="continent c5"></div>
        <div class="continent c6"></div>
        <!-- 云带：白色半透明 -->
        <div class="cloud cloud-1"></div>
        <div class="cloud cloud-2"></div>
        <div class="cloud cloud-3"></div>
        <!-- 重复一份大陆/云用来循环（首尾相接） -->
        <div class="continent c7"></div>
        <div class="continent c8"></div>
        <div class="continent c9"></div>
        <div class="continent c10"></div>
        <div class="cloud cloud-4"></div>
        <div class="cloud cloud-5"></div>
      </div>
    </div>
    <div class="earth-star earth-star-1"></div>
    <div class="earth-star earth-star-2"></div>
    <div class="earth-star earth-star-3"></div>
    <div class="earth-star earth-star-4"></div>
    <div class="earth-star earth-star-5"></div>
    <div class="earth-star earth-star-6"></div>
    <div class="earth-star earth-star-7"></div>
  </div>
</template>

<style scoped>
.earth-stage {
  position: relative;
  width: 250px;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 外圈大气辉光（蓝色光晕） */
.earth-atmosphere {
  position: absolute;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle, transparent 60%, rgba(120, 200, 255, 0.5) 70%, transparent 85%);
  filter: blur(6px);
  pointer-events: none;
}

/* 地球主体：圆形裁剪窗口 */
.earth-globe {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(180deg, #1e6fb8 0%, #2196d6 30%, #1976c1 60%, #0d4f8b 100%);
  box-shadow:
    inset -15px -10px 30px rgba(0, 0, 0, 0.4),
    inset 10px 8px 25px rgba(255, 255, 255, 0.2),
    0 0 30px rgba(80, 160, 220, 0.3);
}

/* 表面（海陆 + 云）：宽度 2 倍，从右往左平移 50% 模拟自转 */
.earth-surface {
  position: absolute;
  top: 0;
  left: 0;
  width: 200%;
  height: 100%;
  display: block;
  animation: earth-rotate 30s linear infinite;
}
@keyframes earth-rotate {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* 大陆（绿色/棕色形状，扁平点缀） */
.continent {
  position: absolute;
  background: linear-gradient(135deg, #4a8f3a, #2d6b1f);
  border-radius: 60% 40% 50% 50% / 50% 60% 40% 50%;
  box-shadow: inset -2px -2px 4px rgba(0, 0, 0, 0.25);
}
.continent.c1 { top: 22%;  left: 8%;   width: 36px; height: 24px; transform: rotate(-8deg); }
.continent.c2 { top: 50%;  left: 22%;  width: 48px; height: 30px; transform: rotate(12deg); }
.continent.c3 { top: 30%;  left: 38%;  width: 30px; height: 20px; transform: rotate(-4deg); }
.continent.c4 { top: 62%;  left: 14%;  width: 28px; height: 18px; transform: rotate(18deg); }
.continent.c5 { top: 40%;  left: 50%;  width: 22px; height: 16px; transform: rotate(-12deg); }
.continent.c6 { top: 70%;  left: 42%;  width: 26px; height: 18px; transform: rotate(6deg); }

/* 重复副本（衔接循环） */
.continent.c7  { top: 22%;  left: 58%;  width: 36px; height: 24px; transform: rotate(-8deg); }
.continent.c8  { top: 50%;  left: 72%;  width: 48px; height: 30px; transform: rotate(12deg); }
.continent.c9  { top: 30%;  left: 88%;  width: 30px; height: 20px; transform: rotate(-4deg); }
.continent.c10 { top: 62%;  left: 64%;  width: 28px; height: 18px; transform: rotate(18deg); }

/* 云带：白色半透明扁平 */
.cloud {
  position: absolute;
  background: rgba(255, 255, 255, 0.78);
  border-radius: 50%;
  filter: blur(2px);
}
.cloud-1 { top: 18%; left: 12%; width: 40px; height: 8px; }
.cloud-2 { top: 48%; left: 35%; width: 50px; height: 10px; }
.cloud-3 { top: 72%; left: 5%;  width: 35px; height: 7px;  }
.cloud-4 { top: 18%; left: 62%; width: 40px; height: 8px; }
.cloud-5 { top: 48%; left: 85%; width: 50px; height: 10px; }

/* 周围小星 */
.earth-star {
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
  animation: earth-twinkle 2.5s ease-in-out infinite;
}
.earth-star-1 { top: 12px;  left: 30px;  animation-delay: 0s; }
.earth-star-2 { top: 25px;  right: 40px; animation-delay: 0.4s; }
.earth-star-3 { top: 100px; left: 8px;   animation-delay: 0.8s; }
.earth-star-4 { bottom: 30px; right: 18px; animation-delay: 1.2s; }
.earth-star-5 { bottom: 10px; left: 90px; animation-delay: 1.6s; }
.earth-star-6 { top: 70px; right: 8px;   animation-delay: 2.0s; }
.earth-star-7 { bottom: 70px; left: 40px; animation-delay: 2.4s; }
@keyframes earth-twinkle {
  0%, 100% { opacity: 0.3; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.2); }
}
</style>
