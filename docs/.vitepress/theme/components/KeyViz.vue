<script setup>
// 实时键盘可视化（改造自 Uiverse Mac keyboard）
// - 固定在主页左下角；按下真实键盘任意键，对应键位点亮（按啥亮啥）
// - 用 e.code 映射键位（不受输入法/大小写影响），修饰键按住常亮
// - 仅主页挂载（index.md ClientOnly），离开页面自动卸载监听
import { ref, reactive, onMounted, onUnmounted } from 'vue'

// 让键盘刚好铺满左侧边栏宽度（不同窗口下侧栏宽度不同，动态测量）
const NATURAL_W = 524 // 键盘原始宽度
const scale = ref(0.52)

function fit() {
  const sb = document.querySelector('.VPSidebar')
  if (!sb) return
  const w = sb.getBoundingClientRect().width
  let s = w / NATURAL_W
  s = Math.min(Math.max(s, 0.45), 0.95)
  scale.value = s
}

// 键位数据（id 用于点亮匹配，w 是宽度类）
const rows = [
  [
    { t: 'esc', w: 'fn', id: 'esc' }, { t: 'F1', w: 'fn', id: 'f1' }, { t: 'F2', w: 'fn', id: 'f2' }, { t: 'F3', w: 'fn', id: 'f3' },
    { t: 'F4', w: 'fn', id: 'f4' }, { t: 'F5', w: 'fn', id: 'f5' }, { t: 'F6', w: 'fn', id: 'f6' }, { t: 'F7', w: 'fn', id: 'f7' },
    { t: 'F8', w: 'fn', id: 'f8' }, { t: 'F9', w: 'fn', id: 'f9' }, { t: 'F10', w: 'fn', id: 'f10' }, { t: 'F11', w: 'fn', id: 'f11' }, { t: 'F12', w: 'fn', id: 'f12' },
    { t: '⏏', w: 'eject' },
  ],
  [
    { t: '`', w: 'num', id: '`' }, { t: '1', w: 'num', id: '1' }, { t: '2', w: 'num', id: '2' }, { t: '3', w: 'num', id: '3' }, { t: '4', w: 'num', id: '4' }, { t: '5', w: 'num', id: '5' },
    { t: '6', w: 'num', id: '6' }, { t: '7', w: 'num', id: '7' }, { t: '8', w: 'num', id: '8' }, { t: '9', w: 'num', id: '9' }, { t: '0', w: 'num', id: '0' },
    { t: '-', w: 'num', id: '-' }, { t: '=', w: 'num', id: '=' }, { t: 'delete', w: 'delete', id: 'delete' },
  ],
  [
    { t: 'tab', w: 'tab', id: 'tab' }, { t: 'Q', id: 'q' }, { t: 'W', id: 'w' }, { t: 'E', id: 'e' }, { t: 'R', id: 'r' },
    { t: 'T', id: 't' }, { t: 'Y', id: 'y' }, { t: 'U', id: 'u' }, { t: 'I', id: 'i' }, { t: 'O', id: 'o' },
    { t: 'P', id: 'p' }, { t: '[', id: '[' }, { t: ']', id: ']' }, { t: '\\', w: 'backslash', id: '\\' },
  ],
  [
    { t: 'caps lock', w: 'caps', id: 'caps lock' }, { t: 'A', id: 'a' }, { t: 'S', id: 's' }, { t: 'D', id: 'd' },
    { t: 'F', id: 'f' }, { t: 'G', id: 'g' }, { t: 'H', id: 'h' }, { t: 'J', id: 'j' }, { t: 'K', id: 'k' },
    { t: 'L', id: 'l' }, { t: ';', id: ';' }, { t: "'", id: "'" }, { t: 'return', w: 'return', id: 'return' },
  ],
  [
    { t: 'shift', w: 'shift', id: 'shift' }, { t: 'Z', id: 'z' }, { t: 'X', id: 'x' }, { t: 'C', id: 'c' },
    { t: 'V', id: 'v' }, { t: 'B', id: 'b' }, { t: 'N', id: 'n' }, { t: 'M', id: 'm' }, { t: ',', id: ',' },
    { t: '.', id: '.' }, { t: '/', id: '/' }, { t: 'shift', w: 'shift', id: 'shift' },
  ],
  [
    { t: 'fn', id: 'fn' }, { t: 'ctrl', w: 'ctrl', id: 'ctrl' }, { t: '⌥', w: 'alt', id: 'alt' },
    { t: '⌘', w: 'cmd', id: 'cmd' }, { t: '', w: 'space', id: 'space' }, { t: '⌘', w: 'cmd', id: 'cmd' },
    { t: '⌥', w: 'alt', id: 'alt' }, { t: '◀', w: 'arrow', id: '◀' }, { t: '▼', w: 'arrow', id: '▼' },
    { t: '▲', w: 'arrow', id: '▲' }, { t: '▶', w: 'arrow', id: '▶' },
  ],
]

// KeyboardEvent.code → 键位 id
const CODE_MAP = {
  Escape: 'esc', Tab: 'tab', CapsLock: 'caps lock', Enter: 'return', Backspace: 'delete', Space: 'space',
  ShiftLeft: 'shift', ShiftRight: 'shift', ControlLeft: 'ctrl', ControlRight: 'ctrl',
  AltLeft: 'alt', AltRight: 'alt', MetaLeft: 'cmd', MetaRight: 'cmd',
  Backquote: '`', Minus: '-', Equal: '=', BracketLeft: '[', BracketRight: ']',
  Backslash: '\\', Semicolon: ';', Quote: "'", Comma: ',', Period: '.', Slash: '/',
  ArrowLeft: '◀', ArrowDown: '▼', ArrowUp: '▲', ArrowRight: '▶',
}

const pressed = reactive(new Set())

function idOf(e) {
  if (CODE_MAP[e.code]) return CODE_MAP[e.code]
  if (/^F\d{1,2}$/.test(e.key)) return e.key.toLowerCase()
  if (/^Key[A-Z]$/.test(e.code)) return e.code.slice(3).toLowerCase()
  if (/^Digit\d$/.test(e.code)) return e.code.slice(5)
  return null
}

function onDown(e) {
  const id = idOf(e)
  if (id) pressed.add(id)
}
function onUp(e) {
  const id = idOf(e)
  if (id) pressed.delete(id)
}
function onBlur() {
  pressed.clear()
}

const isLit = (id) => pressed.has((id || '').toLowerCase())

onMounted(() => {
  window.addEventListener('keydown', onDown)
  window.addEventListener('keyup', onUp)
  window.addEventListener('blur', onBlur)
  window.addEventListener('resize', fit)
  fit()
})
onUnmounted(() => {
  window.removeEventListener('keydown', onDown)
  window.removeEventListener('keyup', onUp)
  window.removeEventListener('blur', onBlur)
  window.removeEventListener('resize', fit)
})
</script>

<template>
  <div class="kb-live" aria-hidden="true" :style="{ transform: `scale(${scale})` }">
    <div class="kb-hint">按啥亮啥 · 试试敲键盘</div>
    <div class="keyboard">
      <div v-for="(row, ri) in rows" :key="ri" class="kb-row">
        <div
          v-for="key in row"
          :key="key.id + ri"
          class="key"
          :class="[key.w ? 'w-' + key.w : '', { lit: isLit(key.id) }]"
        >{{ key.t }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 文档流中显示（曾是固定在主页左下方的浮层，现搬到页面里） */
.kb-live {
  position: static;
  max-width: 760px;
  margin: 0.5rem auto 0;
  z-index: 70;
  pointer-events: none; /* 纯展示，绝不挡内容点击 */
}

.kb-hint {
  font-size: 11px;
  letter-spacing: 0.15em;
  opacity: 0.45;
  margin: 0 0 6px 4px;
  color: var(--vp-c-text-2);
}

.keyboard {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  border-radius: 14px;
  user-select: none;
  background: linear-gradient(180deg, rgba(216, 221, 227, 0.92), rgba(199, 204, 211, 0.92));
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    0 10px 30px rgba(0, 0, 0, 0.22);
}

.kb-row { display: flex; gap: 3px; }

.key {
  background: linear-gradient(180deg, #f7f8f9, #e9ebee);
  border: 1px solid #b8bec6;
  border-bottom-width: 2.5px;
  border-radius: 5px;
  min-width: 30px;
  text-align: center;
  padding: 5px 3px;
  font-size: 9px;
  color: #333;
  transition: background-color 0.08s, color 0.08s, box-shadow 0.08s, transform 0.08s;
}

/* 点亮态 */
.key.lit {
  background: linear-gradient(180deg, #7dd3fc, #38bdf8);
  border-color: #0284c7;
  color: #fff;
  transform: translateY(2px);
  box-shadow:
    0 0 12px rgba(56, 189, 248, 0.8),
    inset 0 -2px 3px rgba(0, 0, 0, 0.15);
}

.w-fn { flex: 1; padding: 7px 4px; font-size: 9px; }
.w-eject { padding: 3px 16px; }
.w-num { flex: 1; }
.w-delete { flex: 1.6; padding: 5px 14px; }
.w-tab { flex: 2; }
.w-backslash { flex: 2; }
.w-caps { flex: 2; }
.w-return { flex: 2; }
.w-shift { flex: 3; }
/* 空格别占太大，方向键有自己一排的空间 */
.w-space { flex: 3.5; min-width: 120px; }
.w-cmd, .w-alt { min-width: 32px; font-size: 13px; }
.w-arrow { min-width: 30px; flex: 0 0 auto; }
.w-ctrl { min-width: 44px; }

/* 暗色模式 */
html.dark .keyboard {
  background: linear-gradient(180deg, rgba(43, 43, 49, 0.92), rgba(34, 34, 40, 0.92));
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 10px 30px rgba(0, 0, 0, 0.5);
}
html.dark .key {
  background: linear-gradient(180deg, #3a3a41, #323238);
  border-color: #1c1c21;
  color: #e5e7eb;
}
html.dark .key.lit {
  background: linear-gradient(180deg, #38bdf8, #0284c7);
  border-color: #7dd3fc;
  color: #062c43;
}

@media (max-width: 959px) {
  .kb-live { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .key { transition: none; }
}
</style>