<script setup>
// 3D 翻书卡片（改造自 Uiverse 悬浮开书组件）
// 用法：<FlipBook cover="标题">内部内容（默认插槽）</FlipBook>
// - 桌面：悬停翻开；触屏/键盘：点击或回车切换（.open 常开）
// - 原版代码问题已修：transform:preserve-3d 无效写法、rotateY(70deg) 与
//   rotateY(-70deg) 互相覆盖、-webkit 前缀透视不一致、写死浅色配色
// - v2 装修：靛蓝皮革封面 + 米色烫金框 + 纸张内页（横线 + 装订红线）
import { ref } from 'vue'

defineProps({
  cover: { type: String, default: 'Hover Me' },
  hint: { type: String, default: '悬停 / 点击打开' },
})

const open = ref(false)

function toggle() {
  open.value = !open.value
}
</script>

<template>
  <div class="book-wrap">
    <div
      class="book"
      :class="{ open }"
      role="button"
      tabindex="0"
      :aria-expanded="open"
      @click="toggle"
      @keydown.enter.prevent="toggle"
      @keydown.space.prevent="toggle"
    >
      <!-- 书内页（默认插槽） -->
      <div class="inner">
        <div class="inner-content">
          <slot />
        </div>
      </div>
      <!-- 封面 -->
      <div class="cover">
        <div class="cover-frame"></div>
        <div class="cover-content">
          <span class="cover-monogram">~/bbben</span>
          <p class="text">{{ cover }}</p>
          <span class="ornament">── ✦ ──</span>
          <span class="cover-author">bbben · 编</span>
        </div>
        <span class="hint">{{ hint }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-wrap {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0.5rem 0 1rem;
}

.book {
  --book-bg: #ffffff;
  --book-shadow: rgba(0, 0, 0, 0.3);
  --book-paper: #fbf7ec;
  --book-line: rgba(0, 0, 0, 0.07);
  --book-margin-line: rgba(224, 108, 92, 0.4);
  --book-ink: #4a4438;
  --cover-cream: #f7f1e1;
  position: relative;
  border-radius: 10px;
  width: 240px;
  height: 320px;
  background-color: var(--book-bg);
  box-shadow: 2px 2px 10px var(--book-shadow);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--vp-c-text-1);
  transform-style: preserve-3d;
  perspective: 900px;
  cursor: pointer;
  transition: transform 0.5s ease;
}

.dark .book {
  --book-bg: #26262b;
  --book-shadow: rgba(0, 0, 0, 0.6);
  --book-paper: #2b2b31;
  --book-line: rgba(255, 255, 255, 0.07);
  --book-margin-line: rgba(224, 108, 92, 0.45);
  --book-ink: #d8d2c4;
}

.cover,
.inner {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border-radius: 10px;
  transform-origin: left center;
  transition: all 0.5s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ---- 靛蓝皮革封面 ---- */
.cover {
  background:
    radial-gradient(120% 90% at 20% 0%, rgba(255, 255, 255, 0.14), transparent 55%),
    linear-gradient(160deg, #35418f 0%, #27306e 55%, #1d2452 100%);
  box-shadow: 1px 1px 6px var(--book-shadow), inset 0 0 24px rgba(0, 0, 0, 0.35);
  z-index: 2;
  flex-direction: column;
}

/* 烫金内框 */
.cover-frame {
  position: absolute;
  inset: 10px;
  border: 1.5px solid rgba(247, 241, 225, 0.55);
  border-radius: 6px;
  pointer-events: none;
}
.cover-frame::after {
  content: "";
  position: absolute;
  inset: 4px;
  border: 1px solid rgba(247, 241, 225, 0.25);
  border-radius: 4px;
}

/* 书脊暗部 */
.cover::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 12px;
  border-radius: 10px 0 0 10px;
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.35), transparent);
  pointer-events: none;
}

/* 右缘书页叠层 */
.cover::after {
  content: "";
  position: absolute;
  right: 5px;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 2px;
  background: repeating-linear-gradient(
    0deg,
    rgba(247, 241, 225, 0.5) 0 2px,
    transparent 2px 5px
  );
  pointer-events: none;
}

.inner {
  background-color: var(--book-paper);
  box-shadow: 1px 1px 6px var(--book-shadow);
}

/* ---- 封面排版 ---- */
.cover-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.cover-monogram {
  font-size: 10px;
  letter-spacing: 0.12em;
  color: var(--cover-cream);
  border: 1px solid rgba(247, 241, 225, 0.6);
  border-radius: 999px;
  padding: 3px 10px;
  font-family: 'Courier New', monospace;
}

.text {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.35em;
  text-indent: 0.35em; /* 抵消末字间距，保持视觉居中 */
  color: var(--cover-cream);
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.4);
}

.ornament {
  font-size: 10px;
  color: rgba(247, 241, 225, 0.75);
  letter-spacing: 0.2em;
}

.cover-author {
  font-size: 11px;
  color: rgba(247, 241, 225, 0.72);
  letter-spacing: 0.25em;
}

.hint {
  position: absolute;
  bottom: 18px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 10px;
  color: rgba(247, 241, 225, 0.6);
  letter-spacing: 0.08em;
}

/* ---- 纸张内页：横线 + 装订红线 ---- */
.inner::before {
  content: "";
  position: absolute;
  inset: 14px 12px;
  border-radius: 4px;
  background: repeating-linear-gradient(
    0deg,
    transparent 0 25px,
    var(--book-line) 25px 26px
  );
  pointer-events: none;
}

.inner::after {
  content: "";
  position: absolute;
  top: 10px;
  bottom: 10px;
  left: 26px;
  width: 1.5px;
  background: var(--book-margin-line);
  pointer-events: none;
}

.inner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 78%;
  transform: translateX(14px); /* 视觉居中补偿（装订线侧留白） */
}

.inner-content :deep(ul) {
  margin: 0;
  padding-left: 0;
  list-style: none;
  font-size: 12.5px;
  line-height: 2.1;
  text-align: left;
  color: var(--book-ink);
}

.inner-content :deep(li) {
  position: relative;
  padding-left: 16px;
}

.inner-content :deep(li)::before {
  content: "";
  position: absolute;
  left: 2px;
  top: 0.75em;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--vp-c-brand-1);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--vp-c-brand-1) 25%, transparent);
}

/* ---- 翻开（悬停 或 点击常开）---- */
.book:hover,
.book.open {
  transform: rotateZ(-10deg);
}

.book:hover .cover,
.book.open .cover {
  transform: rotateY(-70deg);
  box-shadow: 1px 1px 8px var(--book-shadow);
}

.book:hover .inner,
.book.open .inner {
  transform: rotateZ(10deg) rotateX(-3deg) rotateY(-10deg) translateX(170px);
  box-shadow: 1px 1px 20px var(--book-shadow);
  z-index: 1;
}

.book:focus-visible {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: 4px;
}

@media (prefers-reduced-motion: reduce) {
  .book,
  .cover,
  .inner {
    transition: none;
  }
}
</style>
