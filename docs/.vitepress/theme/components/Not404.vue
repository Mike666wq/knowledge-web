<script setup>
// 404 页面：大号动画面部 + 标题 + 返回首页按钮
</script>

<template>
  <div class="not404-wrap">
    <div class="not404-code">404</div>
    <div class="my-custom-face-container">
      <svg class="face" viewBox="0 0 320 380">
        <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="25">
          <g class="face__eyes" transform="translate(0,112.5)">
            <g transform="translate(15,0)">
              <polyline class="face__eye-lid" points="37,0 0,120 75,120"></polyline>
              <polyline class="face__pupil" points="55,120 55,155" stroke-dasharray="35 35"></polyline>
            </g>
            <g transform="translate(230,0)">
              <polyline class="face__eye-lid" points="37,0 0,120 75,120"></polyline>
              <polyline class="face__pupil" points="55,120 55,155" stroke-dasharray="35 35"></polyline>
            </g>
          </g>
          <rect class="face__nose" x="132.5" y="112.5" width="55" height="155" rx="4" ry="4"></rect>
          <g transform="translate(65,334)" stroke-dasharray="102 102">
            <path class="face__mouth-left" d="M 0 30 C 0 30 40 0 95 0"></path>
            <path class="face__mouth-right" d="M 95 0 C 150 0 190 30 190 30"></path>
          </g>
        </g>
      </svg>
    </div>
    <h1 class="not404-title">页面走丢了</h1>
    <p class="not404-desc">你访问的页面不存在或已被移动。</p>
    <a class="not404-btn" href="/">返回首页</a>
  </div>
</template>

<style scoped>
.not404-wrap {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
}

.not404-code {
  font-size: 6rem;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, var(--vp-c-brand-1), #7c3aed);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: -1rem;
}

/* 表情动画 */
.my-custom-face-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 0;
  color: var(--vp-c-text-2);
}

.my-custom-face-container .face { width: 200px; height: auto; }

.my-custom-face-container .face__eyes,
.my-custom-face-container .face__eye-lid,
.my-custom-face-container .face__mouth-left,
.my-custom-face-container .face__mouth-right,
.my-custom-face-container .face__nose,
.my-custom-face-container .face__pupil {
  animation: eyes 1s 0.3s forwards;
}

.my-custom-face-container .face__eye-lid,
.my-custom-face-container .face__pupil {
  animation-duration: 4s;
  animation-delay: 1.3s;
  animation-iteration-count: infinite;
}

.my-custom-face-container .face__eye-lid { animation-name: eye-lid; }
.my-custom-face-container .face__mouth-left { animation-name: mouth-left; }
.my-custom-face-container .face__mouth-right { animation-name: mouth-right; }
.my-custom-face-container .face__nose { animation-name: nose; }
.my-custom-face-container .face__pupil { animation-name: pupil; }

@keyframes eye-lid {
  0%, 40%, 45%, 100% { transform: translateY(0); }
  42.5% { transform: translateY(17.5px); }
}
@keyframes eyes {
  from { transform: translateY(112.5px); }
  to { transform: translateY(15px); }
}
@keyframes pupil {
  0%, 37.5%, 40%, 45%, 87.5%, 100% { stroke-dashoffset: 0; transform: translate(0, 0); }
  12.5%, 25%, 62.5%, 75% { transform: translate(-35px, 0); }
  42.5% { stroke-dashoffset: 35; transform: translate(0, 17.5px); }
}
@keyframes mouth-left {
  from, 50% { stroke-dashoffset: -102; }
  to { stroke-dashoffset: 0; }
}
@keyframes mouth-right {
  from, 50% { stroke-dashoffset: 102; }
  to { stroke-dashoffset: 0; }
}
@keyframes nose {
  from { transform: translate(0, 0); }
  to { transform: translate(0, 22.5px); }
}

.not404-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  margin-top: 1rem;
}

.not404-desc {
  color: var(--vp-c-text-3);
  margin: 0.5rem 0 1.5rem;
  font-size: 1rem;
}

.not404-btn {
  display: inline-block;
  padding: 0.7rem 2rem;
  border-radius: 999px;
  background: var(--vp-c-brand-1);
  color: #fff;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
.not404-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
</style>