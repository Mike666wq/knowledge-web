<script setup>
import { ref, onMounted, computed } from 'vue'
import { useData } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import ThemeToggle from './components/ThemeToggle.vue'
import TerminalButton from './components/TerminalButton.vue'
import ColorPalette from './components/ColorPalette.vue'
import AnimatedFace from './components/AnimatedFace.vue'
import Not404 from './components/Not404.vue'
import StarField from './components/StarField.vue'
import UfoBg from './components/UfoBg.vue'
import DoodleMenu from './components/DoodleMenu.vue'
import EmojiMarquee from './components/EmojiMarquee.vue'
import SpeederRace from './components/SpeederRace.vue'
import SearchBar from './components/SearchBar.vue'
import PlaneLoader from './components/PlaneLoader.vue'
import SidePets from './components/PetsColumn.vue'

const { Layout } = DefaultTheme
const { page } = useData()
const is404 = computed(() => page.value?.isNotFound === true)
const relPath = computed(() => (page.value?.relativePath || '').replace(/^(\.\.\/|\.\/|\/)+/, ''))
const isNotesPage = computed(() => relPath.value.startsWith('notes/'))
// 宠物区（恐龙/太极/小狗）：笔记页 + 关于页
const showSidePets = computed(() => isNotesPage.value || relPath.value === 'about.md')

// ---- 启动加载屏 ----
// SSR 直出静态 HTML（打开瞬间就有），水合后等「资源加载完」且
// 「至少展示 SPLASH_MIN」两个条件都满足才淡出；SPLASH_MAX 兜底防卡死。
// 只在整页打开时出现，站内跳转不重播。
const splashLeaving = ref(false)
const SPLASH_MIN = 1000  // 最短展示时长(ms)
const SPLASH_MAX = 4000  // 安全兜底：最多展示这么久

onMounted(() => {
  const start = performance.now()
  let done = false
  const leave = () => {
    if (done) return
    done = true
    splashLeaving.value = true
  }
  const loaded = document.readyState === 'complete'
    ? Promise.resolve()
    : new Promise(r => window.addEventListener('load', r, { once: true }))
  loaded.then(() => {
    const rest = Math.max(0, SPLASH_MIN - (performance.now() - start))
    setTimeout(leave, rest)
  })
  setTimeout(leave, SPLASH_MAX)
})

// 把表情注入到 sidebar 底部
onMounted(() => {
  const mount = () => {
    const sidebar = document.querySelector('.VPSidebar')
    if (sidebar && !document.querySelector('.sidebar-face-injected')) {
      const nav = sidebar.querySelector('.nav')
      const holder = document.createElement('div')
      holder.className = 'sidebar-face'
      if (nav) nav.appendChild(holder)
      else sidebar.appendChild(holder)
      import('vue').then(({ createApp, h }) => {
        const app = createApp({ render: () => h(AnimatedFace) })
        app.mount(holder)
      })
    }
  }
  setTimeout(mount, 200)
})
</script>

<template>
  <!-- 启动加载屏：打开页面第一眼，资源就绪后淡出 -->
  <div class="app-splash" :class="{ leaving: splashLeaving }" aria-hidden="true">
    <div class="app-splash-inner">
      <PlaneLoader :scale="0.75" />
      <p class="app-splash-text">加载中…</p>
    </div>
  </div>

  <!-- 全站星空背景（暗色模式显示，fixed 在内容层之下） -->
  <StarField />
  <!-- 背景悬浮 UFO（暗色模式，与星空同层） -->
  <UfoBg />

  <!-- 小幽灵：跳动的像素小怪物 -->
  <Ghost />
  <Ghost color="blue" style="top: 380px" />
  <!-- 幽灵列下方：恐龙+小狗同列（笔记页 + 关于页） -->
  <SidePets v-if="showSidePets" />

  <!-- 右下角手绘快捷菜单 -->
  <DoodleMenu />

  <!-- 右下角 emoji 滚动胶囊（菜单上方） -->
  <EmojiMarquee />

  <!-- 404 页面用表情组件替代默认 -->
  <Not404 v-if="is404" />

  <Layout v-else>
    <!-- 导航栏右侧：调色盘 + 手绘主题开关 + 终端 + 搜索（间距统一，外观工具相邻） -->
    <template #nav-bar-content-after>
      <ColorPalette class="nav-palette" />
      <ThemeToggle />
      <TerminalButton class="nav-terminal" />
      <SearchBar class="nav-search" />
    </template>

    <!-- 左侧边栏底部：天气卡 -->
    <template #sidebar-nav-after>
      <WeatherCard />
    </template>

    <!-- 页面底部：双骑手赛车条（所有 doc 布局页，含首页与笔记） -->
    <template #doc-bottom>
      <SpeederRace :title="relPath" />
    </template>
  </Layout>
</template>

<style>
.nav-palette { margin: 0 6px; }
.nav-terminal { margin: 0 6px; }
.nav-terminal .terminal-btn { height: 32px; padding: 0 12px; }
.nav-search { margin: 0 8px 0 10px; }
.sidebar-face { padding: 2rem 0; display: flex; justify-content: center; }

/* ---- 启动加载屏 ---- */
.app-splash {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--vp-c-bg);
  opacity: 1;
  visibility: visible;
  transition: opacity 0.45s ease, visibility 0.45s ease;
}
.app-splash.leaving {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}
.app-splash-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.app-splash-text {
  margin: 6px 0 0;
  font-size: 13px;
  letter-spacing: 0.25em;
  color: var(--vp-c-text-2);
}
</style>