<script setup>
import { ref, computed, onMounted } from 'vue'

// 接收分类树，构建 3D 旋转彩色卡片
const props = defineProps({
  tree: { type: Array, required: true }
})

// 递归统计整棵子树下的笔记总数（分类下还有子分类时也一并计入）
function countFiles(node) {
  if (node.type === 'file') return 1
  if (node.type === 'directory') return (node.children || []).reduce((s, c) => s + countFiles(c), 0)
  return 0
}

// 顶层分类（目录）作为旋转卡片
const categories = computed(() => {
  return props.tree
    .filter(n => n.type === 'directory' && n.children && n.children.length)
    .map(n => ({
      name: n.name,
      link: (n.children.find(c => c.type === 'file') || n.children.find(c => c.type === 'directory')?.children?.find?.(c => c.type === 'file'))?.link || null,
      count: countFiles(n)
    }))
})

// 多彩色卡（同 uiverse 的 --color-card 风格，10 种柔彩）
const COLORS = [
  '142, 249, 252',   // 青
  '142, 252, 204',   // 绿
  '142, 252, 157',   // 绿light
  '215, 252, 142',   // 黄绿
  '252, 252, 142',   // 黄
  '252, 208, 142',   // 橙
  '252, 142, 142',   // 红
  '252, 142, 239',   // 粉
  '204, 142, 252',   // 紫
  '142, 202, 252'    // 蓝
]

// 分类专属图标：已知分类精准映射，未知分类按名称 hash 从备用图标里挑（不再用丑丑的 📁）
const ICON_MAP = {
  'Linux': '🐧', 'Linux基础': '🐧', 'Linux相关问题': '🐧',
  'AI-agent': '🤖',
  'Python': '🐍',
  'Java': '☕',
  'Cloud': '☁️',
  'Certificate': '📜',
  '网络安全': '🛡️',
  '安全': '🛡️',
  '编程': '💻',
}
const FALLBACK_ICONS = ['📚', '🗂️', '💡', '🧩', '🔧', '📖', '🎓', '🛠️']

function iconForName(name) {
  if (ICON_MAP[name]) return ICON_MAP[name]
  let h = 0
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) & 0xffffffff
  return FALLBACK_ICONS[Math.abs(h) % FALLBACK_ICONS.length]
}

// 给每个分类分配颜色和序号
const cards = computed(() => {
  const cats = categories.value
  const n = Math.max(cats.length, 1)
  return cats.map((c, i) => ({
    ...c,
    index: i,
    color: COLORS[i % COLORS.length],
    // 旋转角度：360 / 数量 * index
    angle: (360 / n) * i,
    bigIcon: iconForName(c.name)
  }))
})

const quantity = computed(() => Math.max(categories.value.length, 1))

// 旋转半径按卡片数量自适应：保证相邻卡片永不重叠
// 公式：R = (卡宽/2) / sin(π/N) + 余量；N 越多圆越大
const CARD_HALF_W = 120 // --w 240px 的一半
const radius = computed(() => {
  const n = quantity.value
  const r = Math.ceil(CARD_HALF_W / Math.sin(Math.PI / n)) + 30
  return Math.max(r, 300) // 少量卡片时的最小半径兜底
})
</script>

<template>
  <div class="cards-showcase">
    <div class="rotating-wrapper">
      <div class="rotating-inner" :style="{ '--quantity': quantity, '--radius': radius + 'px' }">
        <a
          v-for="card in cards"
          :key="card.name"
          class="rotating-card"
          :style="{
            '--index': card.index,
            '--color-card': card.color,
            '--rotateY': card.angle
          }"
          :href="card.link"
        >
          <div class="img">
            <span class="card-emoji">{{ card.bigIcon }}</span>
            <span class="card-name">{{ card.name }}</span>
            <span class="card-count">{{ card.count }} 篇</span>
          </div>
        </a>
      </div>
    </div>
    <p class="showcase-hint">点击卡片进入目录 ↓</p>
  </div>
</template>

<style scoped>
.cards-showcase {
  width: 100%;
  padding: 2rem 0;
  text-align: center;
}

/* 旋转容器：不裁剪，悬停放大的卡片可以撑出区块 */
.rotating-wrapper {
  width: 100%;
  height: 560px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 3D 旋转组 */
.rotating-inner {
  --w: 240px;
  --h: 330px;
  --translateZ: var(--radius, 340px);
  --rotateX: -10deg;
  --perspective: 1400px;
  position: relative;
  width: var(--w);
  height: var(--h);
  transform-style: preserve-3d;
  transform: perspective(var(--perspective));
  animation: rotating 30s linear infinite;
}

/* 悬停任何卡片时：暂停旋转，方便看清/点按 */
.rotating-wrapper:hover .rotating-inner {
  animation-play-state: paused;
}

@keyframes rotating {
  from {
    transform: perspective(var(--perspective)) rotateX(var(--rotateX)) rotateY(0);
  }
  to {
    transform: perspective(var(--perspective)) rotateX(var(--rotateX)) rotateY(1turn);
  }
}

/* 单张旋转卡片 */
.rotating-card {
  position: absolute;
  border: 2px solid rgba(var(--color-card));
  border-radius: 16px;
  overflow: hidden;
  inset: 0;
  transform: rotateY(calc((360deg / var(--quantity)) * var(--index)))
    translateZ(var(--translateZ));
  text-decoration: none;
  cursor: pointer;
  transition: transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.45s ease;
}

/* 悬停：放大到约大半个屏幕 + 向观者方向弹出 */
.rotating-card:hover {
  z-index: 50;
  transform: rotateY(calc((360deg / var(--quantity)) * var(--index)))
    translateZ(calc(var(--translateZ) + 150px)) scale(1.7);
  box-shadow: 0 40px 90px rgba(0, 0, 0, 0.35);
}

/* 卡片内容背景（彩色径向渐变） */
.img {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #0000
    radial-gradient(
      circle,
      rgba(var(--color-card), 0.25) 0%,
      rgba(var(--color-card), 0.6) 80%,
      rgba(var(--color-card), 1) 100%
    );
}

.card-emoji {
  font-size: 2.6rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.card-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a1a;
  text-shadow: 0 1px 2px rgba(255,255,255,0.6);
}

.card-count {
  font-size: 0.85rem;
  color: rgba(26,26,26,0.7);
  background: rgba(255,255,255,0.5);
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 600;
}

.showcase-hint {
  margin-top: 1rem;
  color: var(--vp-c-text-3);
  font-size: 0.85rem;
  text-align: center;
}
</style>