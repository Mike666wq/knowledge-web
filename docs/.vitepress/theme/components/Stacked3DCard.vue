<script setup>
// 3D 卡堆（改造自 Uiverse stacked cards）—— 可交互版本
// - 点击某层 → 跳转到对应位置（内部走 router，外链新标签）
// - 键盘：Tab 聚焦整卡，↑/↓ 切层，Enter 跳转当前层
// - 悬停某层 → 右侧浮现该层标签
import { ref, computed } from 'vue'
import { useRouter } from 'vitepress'

const router = useRouter()

const layers = [
  { text: '全部笔记', href: '/' },
  { text: 'Ctrl+K 搜索', action: 'search' },
  { text: 'Linux 笔记', href: '/notes/Linux/' },
  { text: '安全笔记', href: '/notes/安全/' },
  { text: 'AI-agent', href: '/notes/AI-agent/' },
  { text: '终端工具', action: 'terminal' },
  { text: 'GitHub 主页', href: 'https://github.com/Mike666wq', external: true },
  { text: '关于本站', href: '/about.html' },
]

const active = ref(0)
const activeLayer = computed(() => layers[active.value] || layers[0])

function open(l) {
  if (!l) return
  if (l.action === 'search') {
    document.querySelector('#local-search .DocSearch-Button')?.click()
    return
  }
  if (l.action === 'terminal') {
    window.dispatchEvent(new CustomEvent('open-terminal'))
    return
  }
  if (!l.href) return
  if (l.external) {
    window.open(l.href, '_blank', 'noopener')
  } else {
    router.go(l.href)
  }
}

function onKeydown(e) {
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
    e.preventDefault()
    active.value = (active.value + 1) % layers.length
  } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
    e.preventDefault()
    active.value = (active.value - 1 + layers.length) % layers.length
  } else if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    open(activeLayer.value)
  }
}
</script>

<template>
  <div
    class="stack-card"
    tabindex="0"
    role="navigation"
    aria-label="探索本站：3D 卡堆导航"
    @keydown="onKeydown"
  >
    <component
      :is="l.href && !l.external ? 'a' : 'div'"
      v-for="(l, i) in layers"
      :key="i"
      class="layer"
      :class="{ active: active === i }"
      :style="{ '--i': i, '--label': `'${l.text}'` }"
      :href="l.href && !l.external ? l.href : undefined"
      :target="l.external ? '_blank' : undefined"
      :rel="l.external ? 'noopener' : undefined"
      @click="open(l)"
      @mouseenter="active = i"
    ></component>
  </div>
</template>

<style scoped>
.stack-card {
  /* base sizing */
  --w: 250px;
  --h: 300px;
  --step: 18px;
  --offset: 10px;
  --hover-mult: 2;
  --active-mult: 5.5;

  position: relative;
  width: var(--w);
  height: var(--h);
  border-radius: 1rem;
  font-family: 'Montserrat', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: rgba(50, 50, 50, 0.6);
  transform: rotateX(-15deg) rotateY(-35deg);
  perspective: 600px;
  box-shadow:
    rgba(0, 0, 0, 0.2) 4px -4px 18px,
    0rem 5rem 25px 10px rgba(0, 0, 0, 0.25);
  border: dashed 2px rgba(100, 100, 100, 0.4);
  transition: 0.6s ease-in-out;
  user-select: none;
  cursor: pointer;
  outline: none;
}
/* 键盘聚焦：可见描边 */
.stack-card:focus-visible {
  box-shadow:
    0 0 0 3px #38bdf8,
    0 0 0 6px rgba(56, 189, 248, 0.35),
    rgba(0, 0, 0, 0.2) 4px -4px 18px,
    0rem 5rem 25px 10px rgba(0, 0, 0, 0.25);
}

.stack-card:hover {
  transform: translateY(-15px) translateX(15px) rotateX(-15deg) rotateY(-35deg);
  background: rgba(70, 70, 70, 0.6);
  border: dashed 2px rgba(150, 150, 150, 0.3);
  box-shadow:
    rgba(0, 0, 0, 0.2) 4px -4px 18px,
    -1rem 5rem 25px 20px rgba(0, 0, 0, 0.2);
}

.stack-card:active {
  cursor: grabbing;
  height: 250px;
  transition: 0.6s ease-in-out;
  transition-delay: 0.1s;
  box-shadow:
    rgba(0, 0, 0, 0.3) 4px -4px 18px,
    -1rem 7rem 25px 40px rgba(0, 0, 0, 0.2);
  border: dashed 2px rgba(120, 120, 120, 0.5);
}

/* === Layers === */
.layer {
  width: calc(var(--w) - (var(--i) * var(--step)));
  height: calc(var(--h) - (var(--i) * var(--step)));
  transform: translateY(calc(var(--i) * var(--offset)))
    translateX(calc(var(--i) * var(--offset) * -1));
  position: absolute;
  top: 0;
  left: 0;
  border-radius: 1rem;
  box-shadow: rgba(0, 0, 0, 0.3) 4px -4px 12px;
  border: solid 1px rgba(120, 120, 120, 0.4);
  background: rgba(30, 30, 30, calc(0.7 - (var(--i) * 0.05)));
  transition: 0.4s cubic-bezier(0.87, 0, 0.13, 1);
  transition-delay: 0.05s;
  cursor: pointer;
  display: block;
  text-decoration: none;
}

.stack-card:hover .layer {
  background: rgba(30, 30, 30, calc(0.65 - (var(--i) * 0.05)));
  transform: translateY(calc(var(--i) * var(--offset) * var(--hover-mult)))
    translateX(calc(var(--i) * var(--offset) * var(--hover-mult) * -1));
}

.stack-card:active .layer {
  transform: translateY(calc(var(--i) * var(--offset) * var(--active-mult)))
    translateX(calc(var(--i) * var(--offset) * var(--active-mult) * -1));
}

.stack-card:active .layer[style*='--i: 0'] {
  transform: translateY(10px) translateX(-10px);
}

/* 当前激活层：高亮描边 */
.layer.active {
  border: solid 1.5px #38bdf8;
  box-shadow:
    rgba(0, 0, 0, 0.3) 4px -4px 12px,
    0 0 10px rgba(56, 189, 248, 0.35);
}

/* === 标签：悬停/激活时浮现 === */
.layer::after {
  content: var(--label);
  position: absolute;
  left: calc(100% + 10px);
  top: 50%;
  transform: translateY(-50%) scale(1);
  transform-origin: left center;
  color: #ccc;
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition:
    color 0.3s,
    text-shadow 0.3s,
    transform 0.3s,
    opacity 0.3s;
}

.layer:hover::after,
.layer.active::after {
  opacity: 1;
  color: #fff;
  text-shadow: 0 0 5px #fff;
  transform: translateY(-50%) scale(1.3);
}

@media (prefers-reduced-motion: reduce) {
  .stack-card,
  .layer,
  .layer::after { transition: none; }
  .stack-card:hover .layer { transform: translateY(calc(var(--i) * var(--offset))) translateX(calc(var(--i) * var(--offset) * -1)); }
}
</style>