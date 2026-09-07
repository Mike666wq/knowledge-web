<script setup>
// 玻璃三卡片图标组：Github / Code / Earn
// 放在页面 hero / 目录区上方作为社交跳转卡片，全部跳转用户 GitHub
const cards = [
  { text: 'Github', r: -15, url: 'https://github.com/Mike666wq', icon: 'M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z' },
  { text: 'Code', r: 5, url: 'https://github.com/Mike666wq', icon: 'M392.8 1.2c-17-4.9-34.7 5-39.6 22l-128 448c-4.9 17 5 34.7 22 39.6s34.7-5 39.6-22l128-448c4.9-17-5-34.7-22-39.6zm80.6 120.1c-12.5 12.5-12.5 32.8 0 45.3L562.7 256l-89.4 89.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l112-112c12.5-12.5 12.5-32.8 0-45.3l-112-112c-12.5-12.5-32.8-12.5-45.3 0zm-306.7 0c-12.5-12.5-32.8-12.5-45.3 0l-112 112c-12.5 12.5-12.5 32.8 0 45.3l112 112c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256l89.4-89.4c12.5-12.5 12.5-32.8 0-45.3z' },
  { text: 'Earn', r: 25, url: 'https://github.com/Mike666wq', icon: 'M64 64C28.7 64 0 92.7 0 128V384c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V128c0-35.3-28.7-64-64-64H64zm64 320H64V320c35.3 0 64 28.7 64 64zM64 192V128h64c0 35.3-28.7 64-64 64zM448 384c0-35.3 28.7-64 64-64v64H448zm64-192c-35.3 0-64-28.7-64-64h64v64zM288 160a96 96 0 1 1 0 192 96 96 0 1 1 0-192z' }
]
</script>

<template>
  <div class="glass-cards-container">
    <div class="container">
      <a
        v-for="card in cards"
        :key="card.text"
        class="glass"
        :data-text="card.text"
        :style="{ '--r': card.r }"
        :href="card.url"
        target="_blank"
        rel="noopener"
      >
        <svg viewBox="0 0 576 512" height="1em" xmlns="http://www.w3.org/2000/svg">
          <path :d="card.icon"></path>
        </svg>
      </a>
    </div>
  </div>
</template>

<style scoped>
.glass-cards-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 0 1rem;
}

.container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.container .glass {
  position: relative;
  width: 110px;
  height: 130px;
  background: linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.08));
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: 0.5s;
  border-radius: 14px;
  margin: 0 -22px;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  transform: rotate(calc(var(--r) * 1deg));
  text-decoration: none;
  cursor: pointer;
  overflow: hidden;
}

.container:hover .glass {
  transform: rotate(0deg) translateY(-10px);
  margin: 0 10px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.25);
}

/* 悬停的卡片再放大 / 图标变色 */
.container:hover .glass:hover {
  transform: rotate(0deg) translateY(-14px) scale(1.06);
  background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.2));
  border-color: var(--vp-c-brand-1);
}

.container:hover .glass:hover svg {
  fill: var(--vp-c-brand-1);
}

.container .glass::before {
  content: attr(data-text);
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 32px;
  background: rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--vp-c-text-1);
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}

.container .glass svg {
  font-size: 2.6em;
  fill: var(--vp-c-text-2);
}
</style>