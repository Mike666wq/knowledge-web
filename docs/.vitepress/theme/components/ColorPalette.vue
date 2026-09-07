<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const open = ref(false)
const colors = [
  { c: '#e11d48' }, { c: '#f472b6' }, { c: '#fb923c' },
  { c: '#facc15' }, { c: '#84cc16' }, { c: '#10b981' },
  { c: '#0ea5e9' }, { c: '#3b82f6' }, { c: '#8b5cf6' }, { c: '#a78bfa' }
]
const current = ref('#3b82f6')

function toggle() { open.value = !open.value }
function close() { open.value = false }

function hexToRgb(hex) {
  const m = hex.replace('#', '')
  const r = parseInt(m.slice(0, 2), 16)
  const g = parseInt(m.slice(2, 4), 16)
  const b = parseInt(m.slice(4, 6), 16)
  return `${r}, ${g}, ${b}`
}

function applyColor(c) {
  current.value = c
  const root = document.documentElement
  const rgb = hexToRgb(c)
  root.style.setProperty('--vp-c-brand-1', c)
  root.style.setProperty('--vp-c-brand-2', c)
  root.style.setProperty('--vp-c-brand-3', c)
  root.style.setProperty('--vp-c-brand-soft', 'rgba(' + rgb + ', 0.16)')
  // 带透明度的场景用 rgba(var(--vp-c-brand-rgb), x)
  root.style.setProperty('--vp-c-brand-rgb', rgb)
  // 浅色背景用淡色调，但不要锁死 --vp-c-bg（避免覆盖暗色模式的深色背景）
  root.style.setProperty('--vp-c-tint', 'rgba(' + rgb + ', 0.06)')
  try { localStorage.setItem('knowledge-accent', c) } catch {}
}

function copyColor(c) {
  applyColor(c)
  try { navigator.clipboard?.writeText(c) } catch {}
}

function onKey(e) { if (e.key === 'Escape') close() }
onMounted(() => {
  window.addEventListener('keydown', onKey)
  try {
    const saved = localStorage.getItem('knowledge-accent')
    if (saved) applyColor(saved)
  } catch {}
})
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <button class="palette-btn" title="主题色" @click="toggle">
    <span class="palette-icon">🎨</span>
  </button>

  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="palette-modal" @click.self="close">
        <div class="comic-panel">
          <div class="container-items">
            <button
              v-for="item in colors"
              :key="item.c"
              class="item-color"
              :class="{ active: item.c === current }"
              :style="{ '--color': item.c }"
              :aria-color="item.c"
              @click="copyColor(item.c)"
            ></button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.palette-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 0.5px solid var(--vp-c-border);
  background: var(--vp-c-default-soft);
  cursor: pointer;
  transition: all 0.2s;
  margin: 0 4px;
}
.palette-btn:hover { background: var(--vp-c-brand-soft); border-color: var(--vp-c-brand-1); }

.palette-modal {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.comic-panel {
  background: #ffffff;
  border: 4px solid #000;
  padding: 1.2rem;
  border-radius: 8px;
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 1);
}

.container-items {
  display: flex;
  transform-style: preserve-3d;
  transform: perspective(1000px);
  flex-wrap: wrap;
  max-width: 300px;
  justify-content: center;
}

.item-color {
  position: relative;
  flex-shrink: 0;
  width: 40px;
  height: 48px;
  border: none;
  outline: none;
  margin: -4px;
  background-color: transparent;
  transition: 300ms ease-out;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.item-color::after {
  position: absolute;
  content: "";
  inset: 0;
  width: 40px;
  height: 40px;
  background-color: var(--color);
  border-radius: 6px;
  border: 3px solid #000;
  box-shadow: 4px 4px 0 0 #000;
  pointer-events: none;
  transition: 300ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.item-color.active::after { outline: 3px solid #000; outline-offset: 2px; }

.item-color::before {
  position: absolute;
  content: attr(aria-color);
  left: 50%;
  bottom: 60px;
  font-size: 16px;
  letter-spacing: 1px;
  line-height: 1;
  padding: 6px 10px;
  background-color: #fef3c7;
  color: #000;
  border: 3px solid #000;
  border-radius: 6px;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  transform-origin: bottom center;
  transition: all 300ms cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 300ms ease-out, visibility 300ms ease-out;
  transform: translateX(-50%) scale(0.5) translateY(10px);
  white-space: nowrap;
}

.item-color:hover { transform: scale(1.5) translateY(-5px); z-index: 99999; }
.item-color:hover::before { opacity: 1; visibility: visible; transform: translateX(-50%) scale(1) translateY(0); }
.item-color:active::after { transform: translate(2px, 2px); box-shadow: 2px 2px 0 0 #000; }
.item-color:hover + * { transform: scale(1.3) translateY(-3px); z-index: 9999; }
.item-color:hover + * + * { transform: scale(1.15); z-index: 999; }
.item-color:has(+ *:hover) { transform: scale(1.3) translateY(-3px); z-index: 9999; }
.item-color:has(+ * + *:hover) { transform: scale(1.15); z-index: 999; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>