<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Terminal from './Terminal.vue'

const open = ref(false)

function toggle() { open.value = !open.value }

function close() { open.value = false }

// Esc 关闭
function onKey(e) {
  if (e.key === 'Escape') close()
}
// 涂鸦菜单等外部触发打开
function onOpenTerminal() { open.value = true }

onMounted(() => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('open-terminal', onOpenTerminal)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('open-terminal', onOpenTerminal)
})
</script>

<template>
  <!-- 触发按钮：终端图标 -->
  <button class="terminal-btn" title="打开终端" @click="toggle">
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="4 17 10 11 4 5"/>
      <line x1="12" y1="19" x2="20" y2="19"/>
    </svg>
    <span>终端</span>
  </button>

  <!-- 弹窗遮罩 -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="terminal-modal" @click.self="close">
        <div class="terminal-modal-box">
          <div class="terminal-modal-bar">
            <span class="modal-dots">
              <span class="dot dot-red"></span>
              <span class="dot dot-yellow"></span>
              <span class="dot dot-green"></span>
            </span>
            <span class="modal-title">终端 — bbben@bbben-Vivobook-Slate-T3300KA-T3300KA</span>
            <button class="modal-close" @click="close" aria-label="关闭">✕</button>
          </div>
          <Terminal class="terminal-body" @click.stop />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* 触发按钮 */
.terminal-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  border: 0.5px solid var(--vp-c-border);
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-1);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.terminal-btn:hover {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

/* 弹窗遮罩 */
.terminal-modal {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.terminal-modal-box {
  width: 100%;
  max-width: 640px;
  background: rgba(20, 20, 26, 0.95);
  border-radius: 12px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  transform: translateY(20px);
  transition: transform 0.3s;
}

.terminal-modal-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #2c2c2e;
  border-bottom: 0.5px solid rgba(255, 255, 255, 0.08);
}

.modal-dots { display: flex; gap: 6px; }
.dot { width: 12px; height: 12px; border-radius: 50%; }
.dot-red { background: #ff5f57; }
.dot-yellow { background: #febc2e; }
.dot-green { background: #28c840; }

.modal-title {
  color: var(--vp-c-text-2);
  font-size: 0.8rem;
  font-family: var(--vp-font-family-mono);
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--vp-c-text-2);
  font-size: 1rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
}
.modal-close:hover { background: rgba(255, 255, 255, 0.1); color: #fff; }

/* 终端组件适配弹窗 */
.terminal-body :deep(.terminal-window) {
  margin: 0;
  max-width: 100%;
}
.terminal-body :deep(.terminal_body) {
  height: 260px;
  border-radius: 0;
}

/* 过渡 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>