<script setup>
// 新粗野主义搜索栏（改造自 Uiverse brutalist input），替换导航栏默认搜索按钮
// - 定位：fixed 贴视口右缘（VitePress 带 sidebar 时导航内容区很窄，flex 布局不可靠）
// - 行为：点击/聚焦 = 打开本地搜索弹窗（弹窗自动聚焦，在弹窗里输入）；
//   输入框设 readonly 只做扳机，避免弹窗抢焦点导致的镜像不同步
// - 关闭弹窗时若焦点被还原回本框，用 allowOpen 标志防止重新打开死循环
import { ref } from 'vue'

const inputEl = ref(null)
let allowOpen = false

function openSearch() {
  document.querySelector('#local-search .DocSearch-Button')?.click()
}

function armAndOpen() {
  allowOpen = true
  openSearch()
}

function onFocus() {
  if (allowOpen) {
    allowOpen = false
    openSearch()
  }
}
</script>

<template>
  <div class="input-container">
    <input
      ref="inputEl"
      class="input"
      name="text"
      type="text"
      placeholder="Search..."
      readonly
      aria-label="打开搜索"
      @mousedown="armAndOpen"
      @focus="onFocus"
      @keydown.enter="armAndOpen"
    />
  </div>
</template>

<style scoped>
.input-container {
  position: relative;
  width: 170px;
}

.input {
  width: 100%;
  height: 34px;
  padding: 6px 11px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  color: #000;
  background-color: #fff;
  border: 3px solid #000;
  border-radius: 0;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 4px 4px 0 #000;
}

.input::placeholder {
  color: #888;
}

.input:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #000;
}

.input:focus {
  background-color: #010101;
  color: #fff;
  border-color: #d6d9dd;
  animation: sb-shake 0.5s ease-in-out;
}

.input:focus::placeholder {
  color: #fff;
}

/* 右侧闪烁光标装饰 */
.input-container::after {
  content: '|';
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #000;
  pointer-events: none;
  animation: sb-blink 0.7s step-end infinite;
}

@keyframes sb-shake {
  0% { transform: translateX(0); }
  25% { transform: translateX(-3px) rotate(-2deg); }
  50% { transform: translateX(3px) rotate(2deg); }
  75% { transform: translateX(-3px) rotate(-2deg); }
  100% { transform: translateX(0); }
}

@keyframes sb-blink {
  50% { opacity: 0; }
}

@media (max-width: 959px) {
  .input-container { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .input:focus { animation: none; }
  .input-container::after { animation: none; }
}
</style>

<style>
/* 隐藏默认搜索按钮（弹窗与按钮同在 .VPNavBarSearch 内，只能精确隐藏按钮容器） */
#local-search {
  display: none !important;
}
</style>
