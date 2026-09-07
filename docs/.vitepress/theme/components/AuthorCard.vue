<script setup>
// "关于本站" 卡（改造自 Uiverse 3D 倾斜个人卡）
// 效果：默认 3D 倾斜，悬停/聚焦回正 + 阴影抬起 + 底部原子图标放大
// 替换内容：中文版个人信息 + GitHub 按钮
const GITHUB_URL = 'https://github.com/Mike666wq'
</script>

<template>
  <a
    :href="GITHUB_URL"
    target="_blank"
    rel="noopener"
    class="author-card"
    tabindex="0"
    aria-label="访问 GitHub 主页"
  >
    <div class="title">
      <span class="big">bbben</span>
      <p class="sub">个人 Markdown 知识库</p>
    </div>

    <button class="cta" tabindex="-1">
      GitHub 主页
      <svg
        y="0"
        xmlns="http://www.w3.org/2000/svg"
        x="0"
        width="100"
        viewBox="0 0 100 100"
        preserveAspectRatio="xMidYMid meet"
        height="100"
        class="arrow"
      >
        <path
          fill-rule="evenodd"
          d="M22.1,77.9a4,4,0,0,1,4-4H73.9a4,4,0,0,1,0,8H26.1A4,4,0,0,1,22.1,77.9ZM35.2,47.2a4,4,0,0,1,5.7,0L46,52.3V22.1a4,4,0,1,1,8,0V52.3l5.1-5.1a4,4,0,0,1,5.7,0,4,4,0,0,1,0,5.6l-12,12a3.9,3.9,0,0,1-5.6,0l-12-12A4,4,0,0,1,35.2,47.2Z"
        ></path>
      </svg>
    </button>

    <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" class="atom atom-1">
      <path
        stroke-width="5"
        stroke-miterlimit="10"
        d="M 50.4 51 C 40.5 49.1 40 46 40 44 v -1.2 a 18.9 18.9 0 0 0 5.7 -8.8 h 0.1 c 3 0 3.8 -6.3 3.8 -7.3 s 0.1 -4.7 -3 -4.7 C 53 4 30 0 22.3 6 c -5.4 0 -5.9 8 -3.9 16 c -3.1 0 -3 3.8 -3 4.7 s 0.7 7.3 3.8 7.3 c 1 3.6 2.3 6.9 4.7 9 v 1.2 c 0 2 0.5 5 -9.5 6.8 S 2 62 2 62 h 60 a 14.6 14.6 0 0 0 -11.6 -11 z"
      ></path>
    </svg>

    <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" class="atom atom-2">
      <path
        stroke-width="2"
        stroke-miterlimit="10"
        d="M 50.4 51 C 40.5 49.1 40 46 40 44 v -1.2 a 18.9 18.9 0 0 0 5.7 -8.8 h 0.1 c 3 0 3.8 -6.3 3.8 -7.3 s 0.1 -4.7 -3 -4.7 C 53 4 30 0 22.3 6 c -5.4 0 -5.9 8 -3.9 16 c -3.1 0 -3 3.8 -3 4.7 s 0.7 7.3 3.8 7.3 c 1 3.6 2.3 6.9 4.7 9 v 1.2 c 0 2 0.5 5 -9.5 6.8 S 2 62 2 62 h 60 a 14.6 14.6 0 0 0 -11.6 -11 z"
      ></path>
    </svg>
  </a>
</template>

<style scoped>
.author-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  width: 288px;
  height: 208px;
  padding: 20px;
  background: #075985; /* sky-800 */
  border: 4px solid #0c4a6e; /* sky-900 */
  border-radius: 16px;
  overflow: hidden;
  color: #f9fafb; /* gray-50 */
  cursor: pointer;
  text-decoration: none;
  transform: rotate3d(1, -1, 1, 60deg);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease,
    background-color 0.3s ease;
  outline: none;
}
.author-card:hover,
.author-card:focus-visible {
  transform: rotate3d(0, 0, 0, 0deg);
  box-shadow: 0 20px 40px -8px rgba(8, 47, 73, 0.6);
  background: #0369a1; /* sky-700, 略亮 */
}
.author-card:focus-visible {
  box-shadow:
    0 0 0 3px #f9fafb,
    0 0 0 6px #075985,
    0 20px 40px -8px rgba(8, 47, 73, 0.6);
}

.title {
  display: flex;
  flex-direction: column;
}
.big {
  font-weight: 700;
  font-size: 40px;
  line-height: 1;
  letter-spacing: -0.02em;
}
.sub {
  font-size: 12px;
  margin: 4px 0 0;
  opacity: 0.85;
}

.cta {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f9fafb;
  color: #075985;
  border: 2px solid #0c4a6e;
  font-weight: 600;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}
.cta:hover {
  background: #0c4a6e;
  color: #f9fafb;
}
.arrow {
  width: 24px;
  height: 24px;
  fill: currentColor;
}

/* 原子图标：两层叠加形成视差放大效果 */
.atom {
  position: absolute;
  bottom: -2px;
  right: -80px;
  width: 192px;
  height: 192px;
  margin: -8px 0;
  fill: #f9fafb;
  stroke: #0c4a6e;
  z-index: 10;
  transition: transform 0.5s ease;
}
.atom-1 {
  stroke-width: 5;
  transition-duration: 0.5s;
}
.atom-2 {
  stroke-width: 2;
  transition-duration: 0.2s;
}
.author-card:hover .atom-1,
.author-card:focus-visible .atom-1 {
  transform: scale(1.25);
}
.author-card:hover .atom-2,
.author-card:focus-visible .atom-2 {
  transform: scale(1.25);
}

@media (prefers-reduced-motion: reduce) {
  .author-card,
  .atom-1,
  .atom-2 { transition: none; }
  .author-card:hover .atom-1,
  .author-card:hover .atom-2,
  .author-card:focus-visible .atom-1,
  .author-card:focus-visible .atom-2 { transform: none; }
}
</style>