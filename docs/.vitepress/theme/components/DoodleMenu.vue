<script setup>
// 手绘涂鸦放射菜单（改造自 Uiverse radial menu）
// 全站右下角浮动球：点中心 "+" 弹出 8 个贴纸快捷入口
// 原版是 Google 全家桶图标，这里全部换成站点真实功能：
//   首页 / 搜索 / 随机一篇 / 使用说明 / 回到顶部 / 终端 / GitHub / 夜间模式
// 开合保持纯 CSS（checkbox hack），零 JS 状态；卫星动作为 Vue 事件
import { useData, useRouter } from 'vitepress'

const { theme } = useData()
const router = useRouter()

const GITHUB_URL = 'https://github.com/Mike666wq'

function goHome() {
  router.go('/')
}

function goUsage() {
  router.go('/#使用说明')
}

function openSearch() {
  const btn =
    document.querySelector('.DocSearch-Button') ||
    document.querySelector('.VPNavBarSearch button') ||
    document.querySelector('.VPNavBarSearch')
  if (btn) btn.click()
  else
    window.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true })
    )
}

function randomNote() {
  const links = []
  // customNotesTree 节点结构：目录 { type:'directory', children:[...] }，
  // 文件 { type:'file', link:'...' }（字段是 children 不是 items）
  const walk = (arr) =>
    (arr || []).forEach((n) => {
      if (n.type === 'file' && n.link) links.push(n.link)
      if (n.children) walk(n.children)
    })
  walk(theme.value?.customNotesTree)
  if (links.length) router.go(links[Math.floor(Math.random() * links.length)])
}

function scrollTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openTerminal() {
  window.dispatchEvent(new CustomEvent('open-terminal'))
}

function openGithub() {
  window.open(GITHUB_URL, '_blank', 'noopener')
}

function toggleTheme() {
  const dark = document.documentElement.classList.toggle('dark')
  try {
    localStorage.setItem('vitepress-theme-appearance', dark ? 'dark' : 'light')
  } catch {}
  window.dispatchEvent(
    new CustomEvent('theme-mode-changed', { detail: dark ? 'dark' : 'light' })
  )
}
</script>

<template>
  <div class="radial-menu-container">
    <!-- 装饰涂鸦 -->
    <svg class="doodle-decorations" viewBox="0 0 400 400" aria-hidden="true">
      <g stroke="var(--ink)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none">
        <path d="M 50 80 Q 60 80 60 70 Q 60 80 70 80 Q 60 80 60 90 Q 60 80 50 80" fill="#ffdf70"></path>
        <path d="M 330 60 Q 340 60 340 50 Q 340 60 350 60 Q 340 60 340 70 Q 340 60 330 60" fill="#89ffb4"></path>
        <path d="M 80 320 Q 90 320 90 310 Q 90 320 100 320 Q 90 320 90 330 Q 90 320 80 320" fill="#ff8989"></path>
        <path d="M 320 330 Q 330 330 330 320 Q 330 330 340 330 Q 330 330 330 340 Q 330 330 320 330" fill="#89b4ff"></path>
        <path d="M 40 200 Q 50 180 60 210 T 80 190"></path>
        <path d="M 320 200 Q 330 220 340 190 T 360 210"></path>
        <circle cx="120" cy="80" r="3" fill="var(--ink)"></circle>
        <circle cx="280" cy="340" r="2.5" fill="var(--ink)"></circle>
        <circle cx="280" cy="90" r="4" fill="var(--ink)"></circle>
        <circle cx="130" cy="310" r="3" fill="var(--ink)"></circle>
        <path d="M 180 30 L 180 40 M 175 35 L 185 35"></path>
        <path d="M 220 360 L 220 370 M 215 365 L 225 365"></path>
      </g>
    </svg>

    <input type="checkbox" id="doodle-menu-toggle" class="menu-toggle" />

    <!-- 中心按钮 -->
    <label for="doodle-menu-toggle" class="center-icon" tabindex="0" role="button" aria-label="打开快捷菜单">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
    </label>

    <!-- 手绘连接线 -->
    <svg class="connection-lines" viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
      <defs>
        <filter id="handDrawn" x="-20%" y="-20%" width="140%" height="140%">
          <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise"></feTurbulence>
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="4" xChannelSelector="R" yChannelSelector="G"></feDisplacementMap>
        </filter>
      </defs>
      <path class="line line-1" d="M 200 200 Q 230 130 200 60"></path>
      <path class="line line-2" d="M 200 200 Q 271 172 299 101"></path>
      <path class="line line-3" d="M 200 200 Q 270 230 340 200"></path>
      <path class="line line-4" d="M 200 200 Q 228 271 299 299"></path>
      <path class="line line-5" d="M 200 200 Q 170 270 200 340"></path>
      <path class="line line-6" d="M 200 200 Q 129 228 101 299"></path>
      <path class="line line-7" d="M 200 200 Q 130 170 60 200"></path>
      <path class="line line-8" d="M 200 200 Q 172 129 101 101"></path>
    </svg>

    <!-- 1 首页 -->
    <div class="menu-item item-1">
      <button class="icon-circle" aria-label="首页" data-tooltip="首页" @click="goHome">
        <svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
          <path fill="#fafafa" d="M22.586,4.414L5.879,21.121C5.316,21.684,5,22.447,5,23.243V41c0,1.105,0.895,2,2,2h34 c1.105,0,2-0.895,2-2V23.243c0-0.796-0.316-1.559-0.879-2.121L25.414,4.414C24.633,3.633,23.367,3.633,22.586,4.414z"></path>
          <path fill="#43a047" d="M12 35H36V43H12z"></path>
          <path fill="#fbc02d" d="M13,24v19H7c-1.1,0-2-0.9-2-2V24H13z"></path>
          <path fill="#1e88e5" d="M42.12,21.12L29.59,8.59l-5.55,5.55L35,25.1V43h6c1.1,0,2-0.9,2-2V23.24 C43,22.45,42.68,21.68,42.12,21.12z"></path>
          <path fill="#e64a19" d="M29.59,8.59L5,33.18v-9.94c0-0.79,0.32-1.56,0.88-2.12L22.59,4.41c0.78-0.78,2.04-0.78,2.82,0 L29.59,8.59z"></path>
        </svg>
      </button>
    </div>

    <!-- 2 搜索 -->
    <div class="menu-item item-2">
      <button class="icon-circle" aria-label="搜索" data-tooltip="搜索 Ctrl+K" @click="openSearch">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="10.5" cy="10.5" r="6.5" fill="#ffdf70" stroke="#1f2937" stroke-width="2.4"></circle>
          <line x1="15.5" y1="15.5" x2="21" y2="21" stroke="#1f2937" stroke-width="2.8" stroke-linecap="round"></line>
        </svg>
      </button>
    </div>

    <!-- 3 随机一篇 -->
    <div class="menu-item item-3">
      <button class="icon-circle" aria-label="随机一篇笔记" data-tooltip="随机一篇" @click="randomNote">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <rect x="3.5" y="3.5" width="17" height="17" rx="4.5" fill="#fff" stroke="#1f2937" stroke-width="2.2"></rect>
          <circle cx="8.6" cy="8.6" r="1.8" fill="#ff8989"></circle>
          <circle cx="15.4" cy="8.6" r="1.8" fill="#89b4ff"></circle>
          <circle cx="12" cy="12" r="1.8" fill="#1f2937"></circle>
          <circle cx="8.6" cy="15.4" r="1.8" fill="#89ffb4"></circle>
          <circle cx="15.4" cy="15.4" r="1.8" fill="#ffdf70"></circle>
        </svg>
      </button>
    </div>

    <!-- 4 使用说明 -->
    <div class="menu-item item-4">
      <button class="icon-circle" aria-label="使用说明" data-tooltip="使用说明" @click="goUsage">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="#4285F4" stroke="#4285F4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
          <polyline points="14,2 14,8 20,8" fill="#fff" stroke="#fff" stroke-linejoin="round"></polyline>
          <line x1="8" y1="13" x2="16" y2="13" stroke="#fff" stroke-width="2.5" stroke-linecap="round"></line>
          <line x1="8" y1="17" x2="16" y2="17" stroke="#fff" stroke-width="2.5" stroke-linecap="round"></line>
        </svg>
      </button>
    </div>

    <!-- 5 回到顶部 -->
    <div class="menu-item item-5">
      <button class="icon-circle" aria-label="回到顶部" data-tooltip="回到顶部" @click="scrollTop">
        <svg viewBox="0 0 24 24" fill="none" stroke="#1f2937" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20V5"></path>
          <path d="M5.5 11.5 12 5l6.5 6.5"></path>
        </svg>
      </button>
    </div>

    <!-- 6 终端 -->
    <div class="menu-item item-6">
      <button class="icon-circle" aria-label="打开终端" data-tooltip="终端" @click="openTerminal">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2.5" y="3.5" width="19" height="17" rx="3.5" fill="#fff" stroke="#1f2937" stroke-width="2.2"></rect>
          <polyline points="6.5 9 10 12 6.5 15" stroke="#34a853" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></polyline>
          <line x1="12.5" y1="15.5" x2="17.5" y2="15.5" stroke="#ea4335" stroke-width="2.2" stroke-linecap="round"></line>
        </svg>
      </button>
    </div>

    <!-- 7 GitHub -->
    <div class="menu-item item-7">
      <button class="icon-circle" aria-label="GitHub" data-tooltip="GitHub" @click="openGithub">
        <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="#1f2937">
          <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"></path>
        </svg>
      </button>
    </div>

    <!-- 8 夜间模式 -->
    <div class="menu-item item-8">
      <button class="icon-circle" aria-label="切换深浅色" data-tooltip="深浅色" @click="toggleTheme">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z" fill="#fbc02d" stroke="#1f2937" stroke-width="2"></path>
          <circle cx="17" cy="6" r="1.4" fill="#89b4ff"></circle>
          <circle cx="20" cy="9.5" r="1" fill="#ff8989"></circle>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.radial-menu-container {
  --ink: #1f2937;
  --c-blue: #89b4ff;
  --c-red: #ff8989;
  --c-yellow: #ffdf70;
  --c-green: #89ffb4;
  --radius-1: 50% 45% 55% 40% / 55% 45% 50% 50%;
  --radius-2: 40% 60% 45% 55% / 50% 55% 40% 60%;
  --radius-3: 55% 45% 50% 55% / 45% 55% 60% 40%;

  position: fixed;
  right: 16px;
  bottom: 16px;
  width: 420px;
  height: 420px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-family: 'Comic Sans MS', 'Chalkboard SE', 'Marker Felt', sans-serif;
  background: transparent;
  overflow: hidden;
  z-index: 80;
  /* 关键：容器全屏占位但不挡点击，只有按钮本身可点 */
  pointer-events: none;
}

/* 中心按钮可点 */
.radial-menu-container .center-icon {
  pointer-events: auto;
}
/* 卫星按钮：展开后才可点，收起时不留隐形点击区 */
.radial-menu-container .menu-item {
  pointer-events: none;
}
.radial-menu-container .menu-toggle:checked ~ .menu-item {
  pointer-events: auto;
}

.radial-menu-container .doodle-decorations {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0;
  transform: scale(0.9);
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.radial-menu-container:has(.menu-toggle:checked) .doodle-decorations {
  opacity: 1;
  transform: scale(1);
}

.radial-menu-container .menu-toggle {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

/* 中心按钮 */
.radial-menu-container .center-icon {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 4.4em;
  height: 4.4em;
  transform: translate(-50%, -50%);
  background: #ffffff;
  border: 3.5px solid var(--ink);
  border-radius: 45% 55% 45% 55% / 55% 45% 55% 45%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  color: var(--ink);
  box-shadow: 5px 5px 0px var(--ink);
  transition:
    transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.2s ease;
}
.radial-menu-container .center-icon:hover {
  transform: translate(-50%, -50%) scale(1.05) rotate(-3deg);
  box-shadow: 7px 7px 0px var(--c-blue);
}
.radial-menu-container .center-icon:active {
  transform: translate(-50%, -50%) scale(0.95);
  box-shadow: 2px 2px 0px var(--ink);
}
.radial-menu-container .center-icon svg {
  width: 2.6em;
  height: 2.6em;
  transition: transform 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.radial-menu-container .menu-toggle:checked ~ .center-icon svg {
  transform: rotate(180deg) scale(0.9);
}

/* 连接线 */
.radial-menu-container .connection-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  overflow: visible;
}
.radial-menu-container .line {
  fill: none;
  stroke-width: 4.5;
  stroke-linecap: round;
  opacity: 0;
  stroke-dasharray: 200;
  stroke-dashoffset: 200;
  filter: url(#handDrawn) drop-shadow(2px 2px 0px rgba(0, 0, 0, 0.1));
  transition:
    opacity 0.3s ease,
    stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.radial-menu-container .line-1 { stroke: var(--c-red); }
.radial-menu-container .line-2 { stroke: var(--c-blue); }
.radial-menu-container .line-3 { stroke: var(--c-yellow); }
.radial-menu-container .line-4 { stroke: var(--c-green); }
.radial-menu-container .line-5 { stroke: var(--c-red); }
.radial-menu-container .line-6 { stroke: var(--c-blue); }
.radial-menu-container .line-7 { stroke: var(--c-yellow); }
.radial-menu-container .line-8 { stroke: var(--c-green); }

.radial-menu-container .menu-toggle:checked ~ .connection-lines .line {
  opacity: 1;
  stroke-dashoffset: 0;
}
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-1 { transition-delay: 0.05s; }
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-2 { transition-delay: 0.1s; }
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-3 { transition-delay: 0.15s; }
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-4 { transition-delay: 0.2s; }
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-5 { transition-delay: 0.25s; }
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-6 { transition-delay: 0.3s; }
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-7 { transition-delay: 0.35s; }
.radial-menu-container .menu-toggle:checked ~ .connection-lines .line-8 { transition-delay: 0.4s; }

/* 卫星贴纸 */
.radial-menu-container .menu-item {
  position: absolute;
  left: 50%;
  top: 50%;
  opacity: 0;
  transform: translate(-50%, -50%) scale(0) rotate(-20deg);
  transition:
    opacity 0.35s ease,
    top 0.55s cubic-bezier(0.68, -0.55, 0.265, 1.55),
    left 0.55s cubic-bezier(0.68, -0.55, 0.265, 1.55),
    transform 0.55s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  z-index: 10;
}
.radial-menu-container .menu-toggle:checked ~ .menu-item {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1) rotate(0deg);
}
.radial-menu-container .menu-toggle:checked ~ .item-1 { top: 15%; left: 50%; transition-delay: 0.08s; }
.radial-menu-container .menu-toggle:checked ~ .item-2 { top: 25.25%; left: 74.75%; transition-delay: 0.13s; }
.radial-menu-container .menu-toggle:checked ~ .item-3 { top: 50%; left: 85%; transition-delay: 0.18s; }
.radial-menu-container .menu-toggle:checked ~ .item-4 { top: 74.75%; left: 74.75%; transition-delay: 0.23s; }
.radial-menu-container .menu-toggle:checked ~ .item-5 { top: 85%; left: 50%; transition-delay: 0.28s; }
.radial-menu-container .menu-toggle:checked ~ .item-6 { top: 74.75%; left: 25.25%; transition-delay: 0.33s; }
.radial-menu-container .menu-toggle:checked ~ .item-7 { top: 50%; left: 15%; transition-delay: 0.38s; }
.radial-menu-container .menu-toggle:checked ~ .item-8 { top: 25.25%; left: 25.25%; transition-delay: 0.43s; }

.radial-menu-container .icon-circle {
  position: relative;
  width: 3.2em;
  height: 3.2em;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 3px solid var(--ink);
  padding: 0;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.radial-menu-container .item-1 .icon-circle,
.radial-menu-container .item-5 .icon-circle {
  border-radius: var(--radius-1);
  box-shadow: 4px 4px 0px var(--c-red);
}
.radial-menu-container .item-2 .icon-circle,
.radial-menu-container .item-6 .icon-circle {
  border-radius: var(--radius-2);
  box-shadow: -4px 4px 0px var(--c-blue);
}
.radial-menu-container .item-3 .icon-circle,
.radial-menu-container .item-7 .icon-circle {
  border-radius: var(--radius-3);
  box-shadow: 4px -4px 0px var(--c-yellow);
}
.radial-menu-container .item-4 .icon-circle,
.radial-menu-container .item-8 .icon-circle {
  border-radius: var(--radius-1);
  box-shadow: -4px -4px 0px var(--c-green);
}

@keyframes sticker-wiggle {
  0% { transform: scale(1.15) rotate(-6deg); }
  50% { transform: scale(1.15) rotate(6deg); }
  100% { transform: scale(1.15) rotate(-6deg); }
}
.radial-menu-container .icon-circle:hover {
  animation: sticker-wiggle 0.4s ease-in-out infinite;
  box-shadow: 6px 6px 0px var(--ink) !important;
  z-index: 20;
}
.radial-menu-container .icon-circle svg {
  width: 1.8em;
  height: 1.8em;
}

/* 漫画风气泡提示 */
.radial-menu-container .icon-circle::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 130%;
  left: 50%;
  transform: translateX(-50%) translateY(10px) rotate(-3deg) scale(0.8);
  background: #ffffff;
  color: var(--ink);
  border: 2px solid var(--ink);
  border-radius: 12px 12px 12px 0;
  padding: 0.4em 0.8em;
  font-size: 0.85em;
  font-weight: bold;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  box-shadow: 3px 3px 0px var(--c-yellow);
  transition:
    opacity 0.2s ease,
    transform 0.25s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  z-index: 999;
}
.radial-menu-container .icon-circle:hover::after,
.radial-menu-container .icon-circle:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0) rotate(-3deg) scale(1);
}

@keyframes subtle-float {
  0%, 100% { transform: translate(-50%, -50%) translateY(0); }
  50% { transform: translate(-50%, -50%) translateY(-5px); }
}
.radial-menu-container .menu-toggle:checked ~ .item-1 { animation: subtle-float 3s ease-in-out infinite 0.1s; }
.radial-menu-container .menu-toggle:checked ~ .item-2 { animation: subtle-float 3.2s ease-in-out infinite 0.3s; }
.radial-menu-container .menu-toggle:checked ~ .item-3 { animation: subtle-float 2.8s ease-in-out infinite 0.5s; }
.radial-menu-container .menu-toggle:checked ~ .item-4 { animation: subtle-float 3.5s ease-in-out infinite 0.2s; }
.radial-menu-container .menu-toggle:checked ~ .item-5 { animation: subtle-float 3.1s ease-in-out infinite 0.4s; }
.radial-menu-container .menu-toggle:checked ~ .item-6 { animation: subtle-float 2.9s ease-in-out infinite 0.6s; }
.radial-menu-container .menu-toggle:checked ~ .item-7 { animation: subtle-float 3.4s ease-in-out infinite 0.1s; }
.radial-menu-container .menu-toggle:checked ~ .item-8 { animation: subtle-float 3.3s ease-in-out infinite 0.7s; }

@media (max-width: 480px) {
  .radial-menu-container { font-size: 11px; }
  .radial-menu-container .icon-circle::after { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .radial-menu-container .menu-item,
  .radial-menu-container .icon-circle,
  .radial-menu-container .center-icon svg {
    animation: none !important;
    transition: none !important;
  }
}
</style>
