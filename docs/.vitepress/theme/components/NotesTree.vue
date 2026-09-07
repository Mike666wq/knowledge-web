<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  tree: { type: Array, required: true }
})

const expandedGroups = ref(new Set())

const stats = computed(() => {
  const result = []
  for (const node of props.tree) {
    if (node.type === 'directory') {
      const counts = countNodes(node)
      result.push({
        name: node.name,
        title: node.title || node.name,
        counts,
        children: node.children || []
      })
    } else if (node.type === 'file') {
      result.push({ type: 'file', title: node.title || node.name, link: node.link })
    }
  }
  return result
})

function countNodes(node) {
  let files = 0, dirs = 0
  function walk(n) {
    if (n.type === 'file') files++
    else if (n.type === 'directory') {
      dirs++
      if (n.children) n.children.forEach(walk)
    }
  }
  walk(node)
  return { files, dirs }
}

function initExpanded() {
  try {
    const saved = localStorage.getItem('notes-tree-expanded')
    if (saved) { expandedGroups.value = new Set(JSON.parse(saved)); return }
  } catch {}
  expandedGroups.value = new Set()
}
initExpanded()

function toggleGroup(name) {
  if (expandedGroups.value.has(name)) expandedGroups.value.delete(name)
  else expandedGroups.value.add(name)
  expandedGroups.value = new Set(expandedGroups.value)
  try { localStorage.setItem('notes-tree-expanded', JSON.stringify([...expandedGroups.value])) } catch {}
}

function isExpanded(name) { return expandedGroups.value.has(name) }

function paletteFor(name) {
  const palettes = [
    { gradient: 'linear-gradient(135deg, #0071e3 0%, #5ac8fa 100%)', color: '#0071e3' },
    { gradient: 'linear-gradient(135deg, #34c759 0%, #30b0c7 100%)', color: '#34c759' },
    { gradient: 'linear-gradient(135deg, #ff375f 0%, #ff9f0a 100%)', color: '#ff375f' },
    { gradient: 'linear-gradient(135deg, #bf5af2 0%, #0071e3 100%)', color: '#bf5af2' },
    { gradient: 'linear-gradient(135deg, #5e5ce6 0%, #bf5af2 100%)', color: '#5e5ce6' },
    { gradient: 'linear-gradient(135deg, #ff9f0a 0%, #ff453a 100%)', color: '#ff9f0a' },
    { gradient: 'linear-gradient(135deg, #64d2ff 0%, #5ac8fa 100%)', color: '#64d2ff' },
    { gradient: 'linear-gradient(135deg, #30b0c7 0%, #34c759 100%)', color: '#30b0c7' }
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) & 0xffffffff
  return palettes[Math.abs(hash) % palettes.length]
}

// hex 转成 "r, g, b" 逗号分隔（给 --color-card CSS 变量用）
function rgbStr(hex) {
  const m = hex.replace('#', '')
  const r = parseInt(m.slice(0, 2), 16)
  const g = parseInt(m.slice(2, 4), 16)
  const b = parseInt(m.slice(4, 6), 16)
  return `${r}, ${g}, ${b}`
}

// 根据标题 hash 选一个多彩色，给 --color-card 用
function colorCard(title) {
  const colors = ['0, 113, 227', '52, 199, 89', '255, 55, 95', '191, 90, 242', '94, 92, 230', '255, 159, 10', '100, 210, 255', '48, 176, 199', '234, 88, 12', '16, 185, 129']
  let hash = 0
  for (let i = 0; i < title.length; i++) hash = (hash * 31 + title.charCodeAt(i)) & 0xffffffff
  return colors[Math.abs(hash) % colors.length]
}

// 当前卡片内联 style 辅助：返回 --color-card 变量绑定对象
function colorStyle(name) {
  return { '--color-card': colorCard(name) }
}

// 文件夹图标主色（跟随分类）
function foldColor(name) {
  const pairs = {
    '安全': '#f59e0b',
    'AI-agent': '#8b5cf6',
    'Linux': '#10b981'
  }
  return pairs[name] || '#f59e0b'
}

// 卡片 hover 扩散色（hex），跟随卡片多彩色
const hoverPalette = ['#0071e3', '#10b981', '#ff375f', '#bf5af2', '#5e5ce6', '#ff9f0a', '#0ea5e9', '#30b0c7']
function cardHoverHex(title) {
  let hash = 0
  for (let i = 0; i < title.length; i++) hash = (hash * 31 + title.charCodeAt(i)) & 0xffffffff
  return hoverPalette[Math.abs(hash) % hoverPalette.length]
}

// 给每篇笔记一个多彩渐变色（按标题 hash，轮换红蓝绿紫）
function cardGradient(title) {
  const grads = [
    'linear-gradient(135deg, #0071e3, #5ac8fa)',   // blue
    'linear-gradient(135deg, #ff375f, #ff9f0a)',   // coral
    'linear-gradient(135deg, #34c759, #30b0c7)',   // green
    'linear-gradient(135deg, #bf5af2, #5e5ce6)',   // purple
    'linear-gradient(135deg, #ff9f0a, #ff453a)',   // orange-red
    'linear-gradient(135deg, #5e5ce6, #bf5af2)',   // indigo-purple
    'linear-gradient(135deg, #64d2ff, #0071e3)',   // cyan-blue
    'linear-gradient(135deg, #ff453a, #ff375f)'    // red-pink
  ]
  let hash = 0
  for (let i = 0; i < title.length; i++) hash = (hash * 31 + title.charCodeAt(i)) & 0xffffffff
  return grads[Math.abs(hash) % grads.length]
}

// 按标题 hash 选一个 white line-icon path（文档/代码/盾牌/数据库/书/终端）
function iconFor(title) {
  const paths = [
    '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>',
    '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
    '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
    '<path d="m4 17 6-6-6-6"/><line x1="12" y1="19" x2="20" y2="19"/>',
    '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
  ]
  let hash = 0
  for (let i = 0; i < title.length; i++) hash = (hash * 31 + title.charCodeAt(i)) & 0xffffffff
  return paths[Math.abs(hash) % paths.length]
}
</script>

<template>
  <div class="notes-tree">
    <div v-for="group in stats" :key="group.name || group.title" class="group-section">
      <template v-if="group.children">
        <div
          class="group-header"
          :class="{ collapsed: !isExpanded(group.name) }"
          :style="{ '--color-card': colorCard(group.name) }"
          role="button"
          tabindex="0"
          @click="toggleGroup(group.name)"
          @keydown.enter="toggleGroup(group.name)"
          @keydown.space.prevent="toggleGroup(group.name)"
        >
          <FolderNode
            :open="isExpanded(group.name)"
            :color="foldColor(group.name)"
            :name="group.title"
            @toggle="toggleGroup(group.name)"
          />
          <h3 class="group-title">{{ group.title }}</h3>
          <span class="group-counts">
            {{ group.counts.files }} 篇
            <template v-if="group.counts.dirs > 0"> · {{ group.counts.dirs }} 子目录</template>
          </span>
        </div>

        <Transition name="collapse">
          <div v-show="isExpanded(group.name)" class="cards-grid">
            <a
              v-for="child in group.children.filter(c => c.type === 'file')"
              :key="child.name"
              :href="child.link"
              class="card file-card"
              :style="{ '--color-card': colorCard(child.title), '--card-hover': cardHoverHex(child.title) }"
            >
              <div class="card-icon" :style="{ background: cardGradient(child.title) }">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <g v-html="iconFor(child.title)"></g>
                </svg>
              </div>
              <div class="card-body">
                <div class="card-title">{{ child.title }}</div>
                <div class="card-meta">点击阅读 →</div>
              </div>
            </a>
            <div
              v-for="sub in group.children.filter(c => c.type === 'directory')"
              :key="sub.name"
              class="card dir-card"
            >
              <div class="card-icon" :style="{ background: paletteFor(sub.name).gradient }">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                </svg>
              </div>
              <div class="card-body">
                <div class="card-title">{{ sub.title || sub.name }}</div>
                <div class="card-meta">{{ sub.children.filter(c => c.type === 'file').length }} 篇笔记</div>
              </div>
            </div>
          </div>
        </Transition>
      </template>

      <template v-else>
        <a :href="group.link" class="card file-card single">
          <div class="card-icon" style="background: linear-gradient(135deg, #0071e3, #7c3aed)">📄</div>
          <div class="card-body">
            <div class="card-title">{{ group.title }}</div>
            <div class="card-meta">点击阅读 →</div>
          </div>
        </a>
      </template>
    </div>
  </div>
</template>

<style scoped>
.notes-tree { margin: 1.5rem 0 2rem; }

.group-section { margin-bottom: 1rem; }
.group-section:last-child { margin-bottom: 0; }

/* ===== 分组头：大胶囊 ===== */
.group-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1.25rem 0.9rem 0.75rem;
  margin-bottom: 0.9rem;
  border-radius: 999px;
  cursor: pointer;
  user-select: none;
  background: #ffffff;
  border: 0.5px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.dark .group-header {
  background: #2c2c2e;
  border: 0.5px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.group-header:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
  border-color: rgba(0, 113, 227, 0.35);
  background: color-mix(in srgb, var(--vp-c-brand-soft, rgba(0,113,227,0.06)) 60%, #fff);
}

.dark .group-header:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  border-color: rgba(41, 151, 255, 0.4);
}

.group-header.collapsed { margin-bottom: 0.9rem; }

.group-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.15rem;
  height: 1.15rem;
  color: var(--vp-c-text-3);
  flex-shrink: 0;
  transition: transform 0.2s, color 0.15s;
}
.group-toggle.expanded { transform: rotate(0deg); }
.group-toggle:not(.expanded) { transform: rotate(-90deg); }
.group-header:hover .group-toggle { color: var(--vp-c-brand-1); }

.group-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 50%;
  font-size: 1.2rem;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  flex-shrink: 0;
}

.group-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  flex: 1;
  letter-spacing: -0.01em;
}

.group-counts {
  font-size: 0.75rem;
  color: var(--vp-c-brand-1);
  background: rgba(0, 113, 227, 0.08);
  padding: 0.3rem 0.85rem;
  border-radius: 999px;
  font-weight: 600;
  flex-shrink: 0;
}

.dark .group-counts {
  background: rgba(41, 151, 255, 0.15);
  color: var(--vp-c-brand-1);
}

/* ===== 卡片网格：胶囊化 + 统一间距 ===== */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.7rem;
}

/* ===== 单张卡片：胶囊 + hover 扩散动画 ===== */
.card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  background: #ffffff;
  border: 0.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 999px;
  padding: 0.55rem 0.9rem 0.55rem 0.55rem;
  text-decoration: none;
  color: inherit;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
}

.dark .card {
  background: #2c2c2e;
  border: 0.5px solid rgba(255, 255, 255, 0.08);
}

/* hover 扩散圆（右上角圆点 scale 放大填满卡片）+ 圆角 */
.card::before {
  content: "";
  position: absolute;
  z-index: 1;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background-color: var(--card-hover, #00838d);
  border-radius: 999px;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.45s cubic-bezier(0, 0, 0.2, 1);
  pointer-events: none;
  opacity: 1;
}

.card:hover::before {
  transform: scaleX(1);
}

/* 内容浮在扩散层上方 */
.card-icon,
.card-body {
  position: relative;
  z-index: 2;
}

/* 图标 hover 时白色底反色（更醒目） */
.card:hover .card-icon {
  background: #fff !important;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease-out;
}
.card:hover .card-icon svg path,
.card:hover .card-icon svg line,
.card:hover .card-icon svg ellipse,
.card:hover .card-icon svg polyline,
.card:hover .card-icon svg rect {
  stroke: var(--card-hover, #00838d);
}

/* hover 时文字变白 */
.card:hover .card-title {
  color: #fff !important;
  transition: all 0.25s ease-out;
}
.card:hover .card-meta {
  color: rgba(255, 255, 255, 0.9) !important;
  transition: all 0.25s ease-out;
}
.card:hover {
  transform: translateY(-3px);
  border-color: transparent;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

/* 图标：圆形渐变底 */
.card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 50%;
  font-size: 1rem;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.card-meta {
  font-size: 0.7rem;
  color: var(--vp-c-text-3);
  margin-top: 0.1rem;
  line-height: 1.3;
}

.dir-card {
  background: #f5f5f7;
  border-style: dashed;
}

.dark .dir-card {
  background: #1c1c1e;
}

.card.single { max-width: 320px; }

.collapse-enter-active, .collapse-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
  overflow: hidden;
}
.collapse-enter-from, .collapse-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>