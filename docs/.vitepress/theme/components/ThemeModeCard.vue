<script setup>
// 主题模式选择卡（改造自 Uiverse "Choose One" 单选卡片）
// - 跟随系统 / 浅色 / 深色 三选一，接 VitePress 官方 appearance 存储
// - 与右上角手绘开关共用 localStorage['vitepress-theme-appearance']，互相同步
// - 选中色走 --vp-c-brand-1 / --vp-c-brand-rgb，跟随调色板变色
import { ref, onMounted, onBeforeUnmount } from 'vue'

const STORAGE_KEY = 'vitepress-theme-appearance'
const mode = ref('auto') // 'auto' | 'light' | 'dark'
let mq = null

function applyMode(m) {
  const root = document.documentElement
  const dark = m === 'dark' || (m === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  root.classList.toggle('dark', dark)
}

function setMode(m, dispatch = true) {
  mode.value = m
  applyMode(m)
  try { localStorage.setItem(STORAGE_KEY, m) } catch {}
  // 通知其他主题控件（如手绘开关）同步视觉状态
  if (dispatch) window.dispatchEvent(new CustomEvent('theme-mode-changed', { detail: m }))
}

// 接收手绘开关的变更（不转发，避免事件循环）
function onExternalChange(e) {
  const m = e.detail
  if (['auto', 'light', 'dark'].includes(m) && m !== mode.value) setMode(m, false)
}

function onSystemChange() {
  if (mode.value === 'auto') applyMode('auto')
}

onMounted(() => {
  let saved = null
  try { saved = localStorage.getItem(STORAGE_KEY) } catch {}
  mode.value = ['light', 'dark', 'auto'].includes(saved) ? saved : 'auto'
  applyMode(mode.value)
  mq = window.matchMedia('(prefers-color-scheme: dark)')
  mq.addEventListener('change', onSystemChange)
  window.addEventListener('theme-mode-changed', onExternalChange)
})

onBeforeUnmount(() => {
  if (mq) mq.removeEventListener('change', onSystemChange)
  window.removeEventListener('theme-mode-changed', onExternalChange)
})
</script>

<template>
  <div class="mode-card" role="radiogroup" aria-label="主题模式">
    <div class="card-title">主题模式</div>

    <label class="mode-item">
      <span class="mode-icon">
        <!-- 显示器 -->
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" clip-rule="evenodd"
            d="M4 3h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-6v2h3.5a1 1 0 0 1 0 2h-11a1 1 0 0 1 0-2H10v-2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm0 2v9h16V5H4Z" />
        </svg>
      </span>
      跟随系统
      <input type="radio" name="appearance-mode" value="auto"
        :checked="mode === 'auto'" @change="setMode('auto')" />
    </label>

    <label class="mode-item">
      <span class="mode-icon">
        <!-- 太阳 -->
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 17a5 5 0 1 1 0-10 5 5 0 0 1 0 10Zm0 2a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0v-1a1 1 0 0 1 1-1Zm0-14a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0V6a1 1 0 0 1 1-1Zm8 8a1 1 0 0 1-1 1h-1a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1ZM6 12a1 1 0 0 1-1 1H4a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1Zm11.071-6.071a1 1 0 0 1 0 1.414l-.707.707a1 1 0 1 1-1.414-1.414l.707-.707a1 1 0 0 1 1.414 0ZM8.05 15.95a1 1 0 0 1 0 1.414l-.707.707a1 1 0 1 1-1.414-1.414l.707-.707a1 1 0 0 1 1.414 0Zm9.9 2.121a1 1 0 0 1-1.415 0l-.707-.707a1 1 0 0 1 1.415-1.414l.707.707a1 1 0 0 1 0 1.414ZM7.343 6.636a1 1 0 0 1-1.414 0l-.707-.707a1 1 0 0 1 1.414-1.415l.707.707a1 1 0 0 1 0 1.415Z" />
        </svg>
      </span>
      浅色模式
      <input type="radio" name="appearance-mode" value="light"
        :checked="mode === 'light'" @change="setMode('light')" />
    </label>

    <label class="mode-item">
      <span class="mode-icon">
        <!-- 月亮 -->
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" />
        </svg>
      </span>
      深色模式
      <input type="radio" name="appearance-mode" value="dark"
        :checked="mode === 'dark'" @change="setMode('dark')" />
    </label>
  </div>
</template>

<style scoped>
.mode-card {
  max-width: 340px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.25rem 1rem;
  background: var(--vp-c-bg);
  border-radius: 6px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.09);
  transition: box-shadow 0.3s ease;
}

.dark .mode-card {
  background: var(--vp-c-bg-elv);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.45);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  user-select: none;
  color: var(--vp-c-text-1);
}

.mode-item {
  position: relative;
  height: 3.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 3rem 0 0.75rem; /* 右侧留出单选圆点位置 */
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.95rem;
  color: var(--vp-c-text-1);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.mode-item:hover {
  background: var(--vp-c-bg-soft);
}

/* 选中态：替代原版 has-[:checked]:bg-blue-50 / ring / text-blue-500，
   颜色全部跟调色板（--vp-c-brand）走 */
.mode-item:has(input:checked) {
  color: var(--vp-c-brand-1);
  background: rgba(var(--vp-c-brand-rgb), 0.08);
  box-shadow: inset 0 0 0 1px rgba(var(--vp-c-brand-rgb), 0.35);
}

.mode-icon {
  width: 20px;
  height: 20px;
  display: inline-flex;
  flex: none;
}

.mode-icon svg {
  width: 100%;
  height: 100%;
  fill: currentColor; /* 跟随文字颜色，选中时变成品牌色 */
}

.mode-item input {
  position: absolute;
  right: 0.75rem;
  width: 16px;
  height: 16px;
  margin: 0;
  cursor: pointer;
  accent-color: var(--vp-c-brand-1);
}
</style>
