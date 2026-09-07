<script setup>
// 音乐播放器（改造自 Uiverse vinyl record 组件）
// - 同源：复用 PhoneMock 的歌单（themeConfig.phonePlaylist，扫描 public/music/）
// - 简化：去掉 hover 展开（保证 play 按钮始终可点），保留旋转黑胶 + 标题/进度条/控件
// - Tailwind → scoped CSS；原生 Vue 状态管理 play/pause/next/prev
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useData } from 'vitepress'

const { theme } = useData()
const playlist = computed(() => theme.value?.phonePlaylist || [])

const index = ref(0)
const current = computed(() => playlist.value[index.value % Math.max(playlist.value.length, 1)] || null)
const currentSrc = computed(() => current.value?.src || '')

const audioEl = ref(null)
const playing = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progress = computed(() => duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0)

const title = computed(() => {
  const t = current.value?.title || ''
  return t.replace(/\.[^.]+$/, '') || '暂无音乐'
})

const repeatOn = ref(false)        // 单曲/列表循环切换
const shuffleOn = ref(false)       // 随机切换

function fmt(sec) {
  if (!isFinite(sec) || sec < 0) sec = 0
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

function loadAndPlay(autoplay) {
  const a = audioEl.value
  if (!a || !current.value) return
  a.src = current.value.src
  a.load()
  if (autoplay) {
    const onReady = () => {
      a.play().then(() => { playing.value = true }).catch(() => { playing.value = false })
      a.removeEventListener('canplay', onReady)
    }
    a.addEventListener('canplay', onReady)
  }
}

function togglePlay() {
  const a = audioEl.value
  if (!a) return
  if (!playlist.value.length) return
  if (playing.value) {
    a.pause()
    playing.value = false
  } else {
    if (!a.src) a.src = current.value.src
    a.play()
      .then(() => { playing.value = true })
      .catch(() => { playing.value = false })
  }
}

function next() {
  if (!playlist.value.length) return
  if (shuffleOn.value) {
    if (playlist.value.length > 1) {
      let n
      do { n = Math.floor(Math.random() * playlist.value.length) } while (n === index.value)
      index.value = n
    }
  } else {
    index.value = (index.value + 1) % playlist.value.length
  }
  loadAndPlay(true)
}

function prev() {
  if (!playlist.value.length) return
  if (currentTime.value > 3) { audioEl.value.currentTime = 0; return }
  index.value = (index.value - 1 + playlist.value.length) % playlist.value.length
  loadAndPlay(true)
}

function onTimeUpdate() { currentTime.value = audioEl.value?.currentTime || 0 }
function onLoadedMeta() { duration.value = audioEl.value?.duration || 0 }
function onEnded() {
  if (repeatOn.value) {
    audioEl.value.currentTime = 0
    audioEl.value.play()
  } else {
    next()
  }
}

function seek(e) {
  const a = audioEl.value
  if (!a || !duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const ratio = Math.min(Math.max((e.clientX - rect.left) / rect.width, 0), 1)
  a.currentTime = ratio * duration.value
}

function toggleRepeat() { repeatOn.value = !repeatOn.value }
function toggleShuffle() { shuffleOn.value = !shuffleOn.value; if (shuffleOn.value) repeatOn.value = false }

onMounted(() => {
  // 不自动播（浏览器策略 + 避免突兀）；UI 渲染第一首作为展示
  if (playlist.value.length) audioEl.value && (audioEl.value.src = current.value.src)
})
onBeforeUnmount(() => {
  audioEl.value?.pause()
})
</script>

<template>
  <div class="mp-stage">
    <!-- 旋转黑胶（始终显示，播放时旋转；有专辑封面时显示封面图） -->
    <div class="mp-vinyl" :class="{ 'is-playing': playing }">
      <div class="mp-disc">
        <img
          v-if="current && current.cover"
          :src="current.cover"
          alt="专辑封面"
          class="mp-disc-img"
        />
        <svg v-else width="128" height="128" viewBox="0 0 128 128" class="mp-disc-svg">
          <svg>
            <rect width="128" height="128" fill="black"></rect>
            <circle cx="20" cy="20" r="2" fill="white"></circle>
            <circle cx="40" cy="30" r="2" fill="white"></circle>
            <circle cx="60" cy="10" r="2" fill="white"></circle>
            <circle cx="80" cy="40" r="2" fill="white"></circle>
            <circle cx="100" cy="20" r="2" fill="white"></circle>
            <circle cx="120" cy="50" r="2" fill="white"></circle>
            <circle cx="90" cy="30" r="10" fill="white" fill-opacity="0.5"></circle>
            <circle cx="90" cy="30" r="8" fill="white"></circle>
            <path d="M0 128 Q32 64 64 128 T128 128" fill="purple" stroke="black" stroke-width="1"></path>
            <path d="M0 128 Q32 48 64 128 T128 128" fill="mediumpurple" stroke="black" stroke-width="1"></path>
            <path d="M0 128 Q32 32 64 128 T128 128" fill="rebeccapurple" stroke="black" stroke-width="1"></path>
            <path d="M0 128 Q16 64 32 128 T64 128" fill="purple" stroke="black" stroke-width="1"></path>
            <path d="M64 128 Q80 64 96 128 T128 128" fill="mediumpurple" stroke="black" stroke-width="1"></path>
          </svg>
        </svg>
      </div>
      <div class="mp-vinyl-center"></div>
    </div>

    <!-- 卡片：始终显示（保证 play 按钮可点） -->
    <div class="mp-card">
      <p class="mp-title">{{ title }}</p>
      <p class="mp-artist">bbben 的播放列表</p>

      <!-- 进度条 -->
      <div class="mp-progress-row">
        <span class="mp-time">{{ fmt(currentTime) }}</span>
        <div class="mp-progress" @click="seek">
          <div class="mp-progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="mp-time">{{ fmt(duration) }}</span>
      </div>

      <!-- 控件 -->
      <div class="mp-controls">
        <button class="mp-btn" :class="{ active: shuffleOn }" @click="toggleShuffle" aria-label="随机">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 3 21 3 21 8"></polyline>
            <line x1="4" y1="20" x2="21" y2="3"></line>
            <polyline points="21 16 21 21 16 21"></polyline>
            <line x1="15" y1="15" x2="21" y2="21"></line>
            <line x1="4" y1="4" x2="9" y2="9"></line>
          </svg>
        </button>

        <button class="mp-btn" @click="prev" aria-label="上一首">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="19 20 9 12 19 4 19 20"></polygon>
            <line x1="5" y1="19" x2="5" y2="5"></line>
          </svg>
        </button>

        <button class="mp-btn mp-btn-play" @click="togglePlay" :aria-label="playing ? '暂停' : '播放'">
          <svg v-if="!playing" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="6 4 20 12 6 20 6 4"></polygon>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16"></rect>
            <rect x="14" y="4" width="4" height="16"></rect>
          </svg>
        </button>

        <button class="mp-btn" @click="next" aria-label="下一首">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 4 15 12 5 20 5 4"></polygon>
            <line x1="19" y1="5" x2="19" y2="19"></line>
          </svg>
        </button>

        <button class="mp-btn" :class="{ active: repeatOn }" @click="toggleRepeat" aria-label="单曲循环">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="17 1 21 5 17 9"></polyline>
            <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
            <polyline points="7 23 3 19 7 15"></polyline>
            <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
          </svg>
        </button>
      </div>
    </div>

    <audio
      v-if="currentSrc"
      ref="audioEl"
      preload="metadata"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMeta"
      @ended="onEnded"
    ></audio>

    <p v-if="!playlist.length" class="mp-empty">歌单还是空的，往 <code>public/music/</code> 丢点音频就亮起来了 🎵</p>
  </div>
</template>

<style scoped>
.mp-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  user-select: none;
  max-width: 320px;
  margin: 0 auto;
}

/* ==== 旋转黑胶 ==== */
.mp-vinyl {
  position: relative;
  width: 128px;
  height: 128px;
  margin-bottom: -8px;
}
.mp-disc {
  position: relative;
  width: 128px;
  height: 128px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #a1a1aa;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  background: #000;
  animation: mp-spin 3s linear infinite;
  animation-play-state: paused;
}
.mp-vinyl.is-playing .mp-disc {
  animation-play-state: running;
}
.mp-disc-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.mp-vinyl-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  border: 4px solid #a1a1aa;
  z-index: 2;
}
@keyframes mp-spin {
  to { transform: rotate(360deg); }
}

/* ==== 卡片 ==== */
.mp-card {
  position: relative;
  z-index: 3;
  width: 100%;
  max-width: 288px;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
  padding: 0.75rem 0.9rem 0.6rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.dark .mp-card {
  background: #1f1f23;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);
}

.mp-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f1f23;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.dark .mp-title { color: #f5f5f7; }
.mp-artist {
  margin: 0.1rem 0 0.6rem;
  font-size: 0.8rem;
  color: #71717a;
}
.dark .mp-artist { color: #a1a1aa; }

/* ==== 进度条 ==== */
.mp-progress-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  margin-bottom: 0.5rem;
}
.mp-time {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  color: #71717a;
  min-width: 30px;
  text-align: center;
}
.mp-progress {
  flex: 1;
  height: 5px;
  background: #d4d4d8;
  border-radius: 999px;
  cursor: pointer;
  overflow: hidden;
  position: relative;
}
.dark .mp-progress { background: #3f3f46; }
.mp-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 999px;
  transition: width 0.15s linear;
}

/* ==== 控件 ==== */
.mp-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  width: 100%;
  padding: 0 0.2rem;
}
.mp-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #71717a;
  padding: 0.4rem;
  border-radius: 8px;
  transition: all 0.2s;
}
.mp-btn:hover {
  color: #6366f1;
  background: rgba(99, 102, 241, 0.08);
}
.dark .mp-btn { color: #a1a1aa; }
.dark .mp-btn:hover { color: #a78bfa; background: rgba(167, 139, 250, 0.12); }
.mp-btn.active {
  color: #6366f1;
  background: rgba(99, 102, 241, 0.12);
}
.dark .mp-btn.active { color: #a78bfa; background: rgba(167, 139, 250, 0.18); }
.mp-btn-play {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}
.mp-btn-play:hover {
  background: linear-gradient(135deg, #4f46e5, #9333ea);
  transform: scale(1.06);
}
.mp-btn-play svg { fill: #fff; }

.mp-empty {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--vp-c-text-3);
}
.mp-empty code {
  font-family: 'Courier New', monospace;
  background: rgba(0, 0, 0, 0.06);
  padding: 0.1em 0.4em;
  border-radius: 4px;
  font-size: 0.8em;
}

@media (prefers-reduced-motion: reduce) {
  .mp-disc { animation: none; }
}
</style>
