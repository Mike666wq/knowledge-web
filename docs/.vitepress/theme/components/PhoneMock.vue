<script setup>
// iPhone 样机装饰（改造自 Uiverse 手机锁屏 mockup，Tailwind 转 scoped CSS）
// - 时钟/日期/星期/日历图标全部实时（每秒刷新）
// - 可换的图标换成了站点功能：
//     手电筒 → 深浅色切换   相机 → 随机一篇
//     Dock：首页 / 终端 / GitHub
//     四宫格：日历(真日期) / 指南针(装饰) / GitHub / 搜索
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useData, useRouter } from 'vitepress'

// 自定义项（在 index.md 里传 props 即可）：
//   <PhoneMock wallpaper="/wallpaper.png" music="/music.mp3" music-title="歌名" artist="你的名字" />
// - wallpaper：壁纸图片路径（放 docs/public/ 下），不传则用默认渐变星空
// - music：音频路径，传了之后点击灵动岛=播放/暂停（浏览器需要点击才允许播放）
const props = defineProps({
  wallpaper: { type: String, default: '' },
  music: { type: String, default: '' },
  cover: { type: String, default: '' },
  musicTitle: { type: String, default: '' },
  artist: { type: String, default: 'BBBEN' },
})

const { theme } = useData()
const router = useRouter()

// 歌单：config.mjs 扫描 public/music/ 生成（themeConfig.phonePlaylist）
const playlist = computed(() => theme.value?.phonePlaylist || [])
const trackIndex = ref(0)
const currentTrack = computed(() =>
  playlist.value.length
    ? playlist.value[trackIndex.value % playlist.value.length]
    : null
)
// 兼容手动传入的 music 属性（无歌单时作为单曲）
const currentSrc = computed(() => currentTrack.value?.src || props.music || '')
const currentCover = computed(() => currentTrack.value?.cover || props.cover || '')
const hasMusic = computed(() => !!currentSrc.value)

// 歌名：优先 musicTitle；歌单模式用曲名；单曲模式从文件名推导
const musicName = computed(() => {
  if (props.musicTitle) return props.musicTitle
  if (currentTrack.value) return currentTrack.value.title
  if (props.music) {
    try {
      const file = decodeURIComponent(props.music.split('/').pop() || '')
      return file.replace(/\.[^.]+$/, '') || 'Playing Music'
    } catch {
      return 'Playing Music'
    }
  }
  return 'Playing Music'
})

const audioEl = ref(null)
const playing = ref(false)

function toggleMusic() {
  if (!hasMusic.value) return // 没配音乐时保持纯装饰
  const a = audioEl.value
  if (!a) return
  if (playing.value) {
    a.pause()
    playing.value = false
    return
  }
  // 命令式设置 src，避免依赖 Vue 绑定的时序
  if (!a.src) a.src = currentSrc.value
  a.play()
    .then(() => { playing.value = true })
    .catch(() => { playing.value = false })
}

// 双击灵动岛 = 下一首；播完自动切下一首（单曲则重播）
function nextTrack(autoplay = false) {
  if (playlist.value.length === 0) return
  const wasPlaying = autoplay || playing.value
  trackIndex.value = (trackIndex.value + 1) % playlist.value.length
  if (wasPlaying && audioEl.value) {
    const a = audioEl.value
    a.src = currentSrc.value // 命令式，新 src 同步写入，避免时序竞争
    const onReady = () => {
      a.play()
        .then(() => { playing.value = true })
        .catch(() => { playing.value = false })
      a.removeEventListener('canplay', onReady)
      a.removeEventListener('error', onError)
    }
    const onError = () => {
      playing.value = false
      a.removeEventListener('canplay', onReady)
      a.removeEventListener('error', onError)
    }
    a.addEventListener('canplay', onReady)
    a.addEventListener('error', onError)
    a.load()
  }
}

function onEnded() {
  nextTrack(true)
}

const now = ref(new Date())
let timer = null
onMounted(() => {
  timer = setInterval(() => (now.value = new Date()), 1000)
})
onUnmounted(() => clearInterval(timer))

const hhmm = computed(() => {
  const d = now.value
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
})
const dateCn = computed(() => {
  const d = now.value
  return `${d.getMonth() + 1}月${d.getDate()}日 周${'日一二三四五六'[d.getDay()]}`
})
const monCn = computed(() => `${now.value.getMonth() + 1}月`)
const dayNum = computed(() => now.value.getDate())

const GITHUB_URL = 'https://github.com/Mike666wq'

function goHome() { router.go('/') }

function openSearch() {
  document.querySelector('#local-search .DocSearch-Button')?.click()
}

function openTerminal() {
  window.dispatchEvent(new CustomEvent('open-terminal'))
}

function toggleTheme() {
  const dark = document.documentElement.classList.toggle('dark')
  try { localStorage.setItem('vitepress-theme-appearance', dark ? 'dark' : 'light') } catch {}
  window.dispatchEvent(new CustomEvent('theme-mode-changed', { detail: dark ? 'dark' : 'light' }))
}

function randomNote() {
  const links = []
  const walk = (arr) => (arr || []).forEach((n) => {
    if (n.type === 'file' && n.link) links.push(n.link)
    if (n.children) walk(n.children)
  })
  walk(theme.value?.customNotesTree)
  if (links.length) router.go(links[Math.floor(Math.random() * links.length)])
}
</script>

<template>
  <div class="pm-scene">
    <div class="pm-phone">
      <div class="pm-screen">
        <div class="pm-bg-grad"></div>
        <!-- 自定义壁纸（传入 wallpaper 时覆盖默认渐变） -->
        <div
          v-if="wallpaper"
          class="pm-wallpaper"
          :style="{ backgroundImage: `url(${wallpaper})` }"
        ></div>
        <div class="pm-orb pm-orb-purple"></div>
        <div class="pm-orb pm-orb-cyan"></div>

        <!-- 状态栏 -->
        <div class="pm-status">
          <span>{{ hhmm }}</span>
          <span class="pm-status-icons">
            <svg viewBox="0 0 24 24" fill="currentColor" width="10" height="10"><path d="M3 20h18V2L3 20z"></path></svg>
            <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M3 5.25a.75.75 0 01.75-.75h14.5a.75.75 0 01.75.75v13.5a.75.75 0 01-.75.75H3.75a.75.75 0 01-.75-.75V5.25zm17.5 4.5a.75.75 0 01.75.75v3a.75.75 0 01-.75.75h-1.5v-4.5h1.5z" clip-rule="evenodd"></path>
            </svg>
          </span>
        </div>

        <!-- 锁屏层（悬停时淡出） -->
        <div class="pm-lock">
          <div class="pm-lock-clock">
            <span class="pm-lock-date">{{ dateCn }}</span>
            <span class="pm-lock-time">{{ hhmm }}</span>
          </div>
          <div class="pm-quick">
            <button class="pm-quick-btn" aria-label="切换深浅色" title="切换深浅色" @click.stop="toggleTheme">
              <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="#fff" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"></path>
              </svg>
            </button>
            <button class="pm-quick-btn" aria-label="随机一篇笔记" title="随机一篇" @click.stop="randomNote">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <rect x="3.5" y="3.5" width="17" height="17" rx="4.5" fill="none" stroke="#fff" stroke-width="1.5"></rect>
                <circle cx="8.6" cy="8.6" r="1.6" fill="#fff"></circle>
                <circle cx="15.4" cy="8.6" r="1.6" fill="#fff"></circle>
                <circle cx="12" cy="12" r="1.6" fill="#fff"></circle>
                <circle cx="8.6" cy="15.4" r="1.6" fill="#fff"></circle>
                <circle cx="15.4" cy="15.4" r="1.6" fill="#fff"></circle>
              </svg>
            </button>
          </div>
          <div class="pm-homebar"></div>
        </div>

        <!-- 应用层（悬停时浮现） -->
        <div class="pm-apps">
          <div class="pm-grid">
            <div class="pm-app">
              <div class="pm-app-icon pm-ic-calendar">
                <span class="pm-cal-mon">{{ monCn }}</span>
                <span class="pm-cal-day">{{ dayNum }}</span>
              </div>
            </div>
            <div class="pm-app">
              <div class="pm-app-icon pm-ic-compass">
                <div class="pm-compass-dot"></div>
              </div>
            </div>
            <div class="pm-app">
              <a class="pm-app-icon pm-ic-github" :href="GITHUB_URL" target="_blank" rel="noopener" title="GitHub">
                <svg viewBox="0 0 16 16" width="20" height="20" fill="#fff">
                  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"></path>
                </svg>
              </a>
            </div>
            <div class="pm-app">
              <button class="pm-app-icon pm-ic-search" aria-label="搜索" title="搜索" @click.stop="openSearch">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1f2937" stroke-width="2">
                  <circle cx="10.5" cy="10.5" r="6"></circle>
                  <line x1="15" y1="15" x2="20" y2="20" stroke-linecap="round"></line>
                </svg>
              </button>
            </div>
          </div>

          <div class="pm-dock">
            <button class="pm-dock-icon pm-dock-home" aria-label="首页" title="首页" @click.stop="goHome">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 10.5 12 3l9 7.5"></path>
                <path d="M5.5 9.5V20h13V9.5"></path>
              </svg>
            </button>
            <button class="pm-dock-icon pm-dock-terminal" aria-label="终端" title="终端" @click.stop="openTerminal">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round">
                <polyline points="5 8 10 12 5 16"></polyline>
                <line x1="12.5" y1="15.5" x2="18" y2="15.5"></line>
              </svg>
            </button>
            <button class="pm-dock-icon pm-dock-theme" aria-label="切换深浅色" title="深浅色" @click.stop="toggleTheme">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 灵动岛（配了音乐时：点击=播放/暂停，双击=下一首） -->
      <div
        class="pm-island"
        :class="{ 'pm-playing': playing, 'pm-has-music': hasMusic }"
        title="点击播放/暂停 · 双击下一首"
        @click.stop="toggleMusic"
        @dblclick.stop="nextTrack(true)"
      >
        <div class="pm-island-inner">
          <div class="pm-island-art" :class="{ 'pm-spinning': playing && currentCover }">
            <!-- 专辑封面：当前曲目的同名图片 > 全局 cover > 音符图标 -->
            <img v-if="currentCover" :src="currentCover" alt="专辑封面" class="pm-cover-img" />
            <svg v-else viewBox="0 0 24 24" width="14" height="14" fill="#fff">
              <path fill-rule="evenodd" d="M19.952 1.651a.75.75 0 01.298.599V16.303a3 3 0 01-2.176 2.884l-1.32.377a2.553 2.553 0 11-1.403-4.909l2.311-.66a1.5 1.5 0 001.088-1.442V6.994l-9 2.572v9.737a3 3 0 01-2.176 2.884l-1.32.377a2.553 2.553 0 11-1.402-4.909l2.31-.66a1.5 1.5 0 001.088-1.442V9.017 5.25a.75.75 0 01.544-.721l10.5-3a.75.75 0 01.658.122z" clip-rule="evenodd"></path>
            </svg>
          </div>
          <div class="pm-island-text">
            <span class="pm-island-title">{{ musicName }}</span>
            <span class="pm-island-sub">{{ playing ? props.artist : (props.music ? '点击播放' : props.artist) }}</span>
          </div>
          <div class="pm-island-bars">
            <i></i><i></i><i></i>
          </div>
        </div>
      </div>

      <!-- 音乐（歌单来自 public/music/ 自动扫描，src 命令式设置） -->
      <audio v-if="currentSrc" ref="audioEl" preload="none" @ended="onEnded"></audio>

      <!-- 侧键 -->
      <span class="pm-key pm-key-r"></span>
      <span class="pm-key pm-key-l1"></span>
      <span class="pm-key pm-key-l2"></span>
      <span class="pm-key pm-key-l3"></span>

      <!-- 扫光 -->
      <div class="pm-shine"></div>
    </div>
  </div>
</template>

<style scoped>
.pm-scene {
  display: flex;
  justify-content: center;
  align-items: center;
}

.pm-phone {
  position: relative;
  display: flex;
  justify-content: center;
  width: 180px;
  height: 350px;
  border: 3px solid #1f2937;
  border-radius: 32px;
  background: #111827;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(17, 24, 39, 0.5);
  transition: all 0.5s;
  user-select: none;
  cursor: default;
}
.pm-phone:hover {
  transform: translateY(-4px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(17, 24, 39, 0.5);
}

.pm-screen {
  position: relative;
  height: 100%;
  width: 100%;
  overflow: hidden;
  border-radius: 28px;
  background: #000;
}

.pm-bg-grad {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top right, #0f172a, #1e1b4b, #0f172a);
  transition: transform 0.7s;
}

/* 自定义壁纸层 + 可读性遮罩 */
.pm-wallpaper {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
}
.pm-wallpaper::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(rgba(0, 0, 0, 0.12), rgba(0, 0, 0, 0.38));
}
.pm-phone:hover .pm-bg-grad { transform: scale(1.1); }

.pm-orb {
  position: absolute;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  filter: blur(40px);
  mix-blend-mode: screen;
  transition: all 0.7s;
}
.pm-orb-purple {
  top: 0; right: 0;
  background: rgba(147, 51, 234, 0.2);
}
.pm-orb-cyan {
  bottom: 0; left: 0;
  background: rgba(8, 145, 178, 0.2);
}
.pm-phone:hover .pm-orb-purple { transform: translate(16px, -16px); }
.pm-phone:hover .pm-orb-cyan { transform: translate(-16px, 16px); }

/* 状态栏 */
.pm-status {
  position: absolute;
  top: 4px;
  width: 100%;
  padding: 4px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
  color: #fff;
  font-size: 8px;
  font-weight: 500;
  opacity: 0.8;
}
.pm-status-icons { display: flex; gap: 4px; align-items: center; }

/* 锁屏层 */
.pm-lock {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 48px;
  z-index: 10;
  transition: all 0.5s ease-in-out;
}
.pm-phone:hover .pm-lock {
  opacity: 0;
  transform: translateY(-16px) scale(0.95);
  pointer-events: none;
}
.pm-lock-clock { display: flex; flex-direction: column; align-items: center; color: rgba(255, 255, 255, 0.9); }
.pm-lock-date { font-size: 8px; font-weight: 600; letter-spacing: 0.08em; }
.pm-lock-time { font-size: 56px; font-weight: 200; letter-spacing: -0.04em; margin-top: -6px; }

.pm-quick {
  position: absolute;
  bottom: 24px;
  width: 100%;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
}
.pm-quick-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  transition: background 0.2s;
}
.pm-quick-btn:hover { background: rgba(255, 255, 255, 0.25); }

.pm-homebar {
  position: absolute;
  bottom: 8px;
  width: 40%;
  height: 3px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 999px;
}

/* 应用层 */
.pm-apps {
  position: absolute;
  inset: 0;
  padding: 40px 12px 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  opacity: 0;
  transform: scale(1.05) translateY(16px);
  transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1);
  z-index: 5;
}
.pm-phone:hover .pm-apps {
  opacity: 1;
  transform: scale(1) translateY(0);
  z-index: 10;
}

.pm-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  column-gap: 8px;
  row-gap: 16px;
  place-items: center;
  margin-top: 8px;
}
.pm-app { display: flex; flex-direction: column; align-items: center; }
.pm-app-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  border: none;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}
.pm-app-icon:hover { transform: scale(1.12); }

.pm-ic-calendar { background: #fff; }
.pm-cal-mon { font-size: 5px; font-weight: 700; color: #ef4444; line-height: 1; margin-top: 4px; text-transform: uppercase; }
.pm-cal-day { font-size: 15px; font-weight: 300; color: #111; line-height: 1; }

.pm-ic-compass { background: linear-gradient(to top right, #fef08a, #ec4899, #a855f7); overflow: hidden; }
.pm-compass-dot { width: 16px; height: 16px; border-radius: 50%; background: rgba(255, 255, 255, 0.4); filter: blur(2px); }

.pm-ic-github { background: #111; }

.pm-ic-search { background: #e5e5e5; }

.pm-dock {
  width: 100%;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  padding: 0 8px;
  margin-bottom: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.pm-dock-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  border: none;
  transition: transform 0.2s;
}
.pm-dock-icon:hover { transform: scale(1.12); }
.pm-dock-home { background: #22c55e; box-shadow: 0 4px 6px -1px rgba(34, 197, 94, 0.2); }
.pm-dock-terminal { background: #4ade80; box-shadow: 0 4px 6px -1px rgba(74, 222, 128, 0.2); }
.pm-dock-theme { background: #3b82f6; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2); border: 1px solid #60a5fa; }

/* 灵动岛 */
.pm-island {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 30;
  height: 20px;
  width: 64px;
  border-radius: 999px;
  background: #000;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}
.pm-island:hover {
  width: 150px;
  height: 48px;
  border-radius: 18px;
}
.pm-island-inner {
  opacity: 0;
  transition: opacity 0.3s 0.1s;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  color: #fff;
  font-size: 8px;
}
.pm-island:hover .pm-island-inner { opacity: 1; }
.pm-island-art {
  height: 32px;
  width: 32px;
  border-radius: 8px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(to bottom right, #ef4444, #db2777);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
}
/* 专辑封面：播放时像黑胶一样旋转 */
.pm-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.pm-spinning .pm-cover-img {
  border-radius: 50%;
  animation: pm-spin 5s linear infinite;
}
@keyframes pm-spin {
  to { transform: rotate(360deg); }
}
.pm-island-text { display: flex; flex-direction: column; line-height: 1.2; white-space: nowrap; }
.pm-island-title {
  font-weight: 600;
  font-size: 9px;
  max-width: 72px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pm-island-sub { color: #9ca3af; font-size: 8px; }
.pm-island-bars {
  display: flex;
  align-items: flex-end;
  gap: 1.5px;
  height: 12px;
  margin-left: auto;
  padding-right: 4px;
}
.pm-island-bars i { width: 2px; background: #4ade80; display: block; }
.pm-island-bars i:nth-child(1) { height: 100%; animation: pm-bounce 1s infinite; }
.pm-island-bars i:nth-child(2) { height: 66%; animation: pm-bounce 1.2s infinite; }
.pm-island-bars i:nth-child(3) { height: 50%; animation: pm-bounce 0.8s infinite; }
/* 配了音乐时：绿条只在真正播放时跳动 */
.pm-island.pm-has-music .pm-island-bars i {
  animation: none;
  transform: scaleY(0.35);
  opacity: 0.5;
}
.pm-island.pm-has-music.pm-playing .pm-island-bars i {
  animation: pm-bounce 1s infinite;
  transform: none;
  opacity: 1;
}
@keyframes pm-bounce {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
}

/* 侧键 */
.pm-key {
  position: absolute;
  width: 3px;
  background: #374151;
  border-radius: 0 6px 6px 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.pm-key-r { right: -4px; top: 64px; height: 40px; border-left: 1px solid #111827; border-radius: 0 6px 6px 0; }
.pm-key-l1 { left: -4px; top: 48px; height: 24px; border-right: 1px solid #111827; border-radius: 6px 0 0 6px; }
.pm-key-l2 { left: -4px; top: 80px; height: 40px; border-right: 1px solid #111827; border-radius: 6px 0 0 6px; }
.pm-key-l3 { left: -4px; top: 128px; height: 40px; border-right: 1px solid #111827; border-radius: 6px 0 0 6px; }

/* 扫光 */
.pm-shine {
  position: absolute;
  top: 0;
  right: 0;
  width: 120%;
  height: 100%;
  background: linear-gradient(to top right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0));
  transform: skewX(-12deg) translateX(20%);
  pointer-events: none;
  transition: transform 1s ease-in-out;
}
.pm-phone:hover .pm-shine { transform: skewX(-12deg) translateX(-100%); }

@media (prefers-reduced-motion: reduce) {
  .pm-island-bars i, .pm-shine, .pm-bg-grad, .pm-orb { animation: none; transition: none; }
}
</style>
