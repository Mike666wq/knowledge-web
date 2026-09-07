<script setup>
// iOS 风格设置面板（改造自 Uiverse modern settings）
// 实功能：
//   Wi-Fi · Cellular · Battery · Privacy —— 点击弹状态气泡
//   Bluetooth · Display · Sounds · Notifications —— 拨动开关
//   卡片有 0.05s 错峰淡入动画
import { ref, onMounted, onBeforeUnmount } from 'vue'

const toggles = ref({
  bluetooth: true,
  display: true,
  sounds: false,
  notifications: true,
})

const brightness = ref(72)   // 显示与亮度滑条
const wifi = ref({ name: '~/bbben-home', signal: 5 })
const cellular = ref({ used: 28.6, total: 30 })
const battery = ref(87)

const popover = ref(null)  // 当前展示气泡的卡片

function tap(name) {
  // Wi-Fi/Cellular/Battery/Privacy → 弹状态气泡（再点同一张关闭，点其它张切换；点卡片外区域也关闭）
  popover.value = (popover.value === name) ? null : name
}

function toggle(key) {
  toggles.value[key] = !toggles.value[key]
}

// 点卡片/气泡外部区域 → 自动关闭气泡
function onDocClick(e) {
  if (!e.target.closest('.ios-set__card')) {
    popover.value = null
  }
}
onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>

<template>
  <div class="ios-set">
    <div class="ios-set__container">
      <div class="ios-set__header">Settings</div>

      <!-- Wi-Fi：点击弹气泡 -->
      <div class="ios-set__card" @click="tap('wifi')">
        <div class="ios-set__icon" style="background: linear-gradient(135deg, #007aff, #00c4ff);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="#fff" d="M12 21q-1.05 0-1.775-.725T9.5 18.5t.725-1.775T12 16t1.775.725t.725 1.775t-.725 1.775T12 21m0-11q1.875 0 3.563.6t3.062 1.65q.5.375.513.988T18.7 14.3q-.425.425-1.05.438t-1.125-.338q-.95-.65-2.1-1.025T12 13t-2.425.375t-2.1 1.025q-.5.35-1.125.325t-1.05-.45q-.425-.45-.425-1.062t.5-.988q1.375-1.05 3.063-1.638T12 10m0-6q3.125 0 5.888 1.025t4.962 2.9q.5.425.525 1.05t-.425 1.075q-.425.425-1.05.438t-1.125-.388q-1.8-1.475-4.037-2.287T12 7t-4.737.813T3.225 10.1q-.5.4-1.125.388t-1.05-.438Q.6 9.6.625 8.975t.525-1.05q2.2-1.875 4.963-2.9T12 4"></path>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Wi-Fi</div>
          <div class="ios-set__description">{{ wifi.name }} · 信号 {{ '▮'.repeat(wifi.signal) }}</div>
        </div>
        <div class="ios-set__chev">›</div>
        <div v-if="popover === 'wifi'" class="ios-set__popover">
          <div class="ios-set__popover-title">📶 已连接</div>
          <div class="ios-set__popover-row"><b>{{ wifi.name }}</b><span>RSSI -38dBm · 满格</span></div>
          <div class="ios-set__popover-row"><span>安全：WPA3-Personal</span></div>
        </div>
      </div>

      <!-- Bluetooth：拨动开关 -->
      <div class="ios-set__card" @click="toggle('bluetooth')">
        <div class="ios-set__icon" :class="{ 'is-on': toggles.bluetooth }" style="background: linear-gradient(135deg, #5856d6, #8a84ff);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m7 8l10 8l-5 4V4l5 4l-10 8"></path>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Bluetooth</div>
          <div class="ios-set__description">{{ toggles.bluetooth ? '已开启 · 1 台设备已连接' : '已关闭' }}</div>
        </div>
        <div class="ios-set__switch" :class="{ on: toggles.bluetooth }"><span></span></div>
      </div>

      <!-- Cellular：点击弹气泡 -->
      <div class="ios-set__card" @click="tap('cellular')">
        <div class="ios-set__icon" style="background: linear-gradient(135deg, #34c759, #5ce883);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
            <path fill="#fff" d="M472 432h-48a24 24 0 0 1-24-24V104a24 24 0 0 1 24-24h48a24 24 0 0 1 24 24v304a24 24 0 0 1-24 24m-128 0h-48a24 24 0 0 1-24-24V184a24 24 0 0 1 24-24h48a24 24 0 0 1 24 24v224a24 24 0 0 1-24 24m-128 0h-48a24 24 0 0 1-24-24V248a24 24 0 0 1 24-24h48a24 24 0 0 1 24 24v160a24 24 0 0 1-24 24m-128 0H40a24 24 0 0 1-24-24v-96a24 24 0 0 1 24-24h48a24 24 0 0 1 24 24v96a24 24 0 0 1-24 24"></path>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Cellular</div>
          <div class="ios-set__description">本周期已用 {{ cellular.used }} / {{ cellular.total }} GB</div>
        </div>
        <div class="ios-set__chev">›</div>
        <div v-if="popover === 'cellular'" class="ios-set__popover">
          <div class="ios-set__popover-title">📊 本月流量</div>
          <div class="ios-set__bar"><div class="ios-set__bar-fill" :style="{ width: (cellular.used/cellular.total*100) + '%' }"></div></div>
          <div class="ios-set__popover-row"><span>已用</span><b>{{ cellular.used }} GB</b></div>
          <div class="ios-set__popover-row"><span>剩余</span><b>{{ (cellular.total - cellular.used).toFixed(1) }} GB</b></div>
        </div>
      </div>

      <!-- Battery：点击弹气泡 -->
      <div class="ios-set__card" @click="tap('battery')">
        <div class="ios-set__icon" style="background: linear-gradient(135deg, #00ddeb, #00b8d4);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 10.5v3M6 17h10a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2"></path>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Battery</div>
          <div class="ios-set__description">{{ battery }}% · 普通使用还可撑 6h</div>
        </div>
        <div class="ios-set__chev">›</div>
        <div v-if="popover === 'battery'" class="ios-set__popover">
          <div class="ios-set__popover-title">🔋 电池</div>
          <div class="ios-set__battery">
            <div class="ios-set__battery-shell"><div class="ios-set__battery-fill" :style="{ width: battery + '%' }"></div></div>
            <div class="ios-set__battery-tip"></div>
          </div>
          <div class="ios-set__popover-row"><span>电量</span><b>{{ battery }}%</b></div>
          <div class="ios-set__popover-row"><span>状态</span><b>已连接电源</b></div>
        </div>
      </div>

      <!-- Display & Brightness：滑条 -->
      <div class="ios-set__card" @click.stop>
        <div class="ios-set__icon" style="background: linear-gradient(135deg, #ff9500, #ffcc00);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 21 21">
            <path fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" d="M5 3.5h11a2 2 0 0 1 2 2v6.049a2 2 0 0 1-1.85 1.994l-.158.006l-11-.042a2 2 0 0 1-1.992-2V5.5a2 2 0 0 1 2-2m.464 12H15.5m-8 2h6" stroke-width="1.5"></path>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Display & Brightness</div>
          <div class="ios-set__description">亮度 {{ brightness }}% · 自动调节</div>
          <input class="ios-set__slider" type="range" min="20" max="100" :value="brightness" @input="e => brightness = +e.target.value" @click.stop />
        </div>
        <div class="ios-set__switch" :class="{ on: toggles.display }" @click.stop="toggle('display')"><span></span></div>
      </div>

      <!-- Sounds & Haptics：拨动 -->
      <div class="ios-set__card" @click="toggle('sounds')">
        <div class="ios-set__icon" :class="{ 'is-on': toggles.sounds }" style="background: linear-gradient(135deg, #ff2d55, #ff6b88);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <g fill="none" stroke="#fff" stroke-width="2">
              <path d="M3.158 13.93a3.75 3.75 0 0 1 0-3.86a1.5 1.5 0 0 1 .993-.7l1.693-.339a.45.45 0 0 0 .258-.153L8.17 6.395c1.182-1.42 1.774-2.129 2.301-1.938S11 5.572 11 7.42v9.162c0 1.847 0 2.77-.528 2.962c-.527.19-1.119-.519-2.301-1.938L6.1 15.122a.45.45 0 0 0-.257-.153L4.15 14.63a1.5 1.5 0 0 1-.993-.7Z"></path>
              <path stroke-linecap="round" d="M15.536 8.464a5 5 0 0 1 .027 7.044m4.094-9.165a8 8 0 0 1 .044 11.27"></path>
            </g>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Sounds & Haptics</div>
          <div class="ios-set__description">{{ toggles.sounds ? '已开启 · 静音模式' : '已关闭' }}</div>
        </div>
        <div class="ios-set__switch" :class="{ on: toggles.sounds }"><span></span></div>
      </div>

      <!-- Notifications：拨动 -->
      <div class="ios-set__card" @click="toggle('notifications')">
        <div class="ios-set__icon" :class="{ 'is-on': toggles.notifications }" style="background: linear-gradient(135deg, #ff3b30, #ff7964);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
            <path fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="M427.68 351.43C402 320 383.87 304 383.87 217.35C383.87 138 343.35 109.73 310 96c-4.43-1.82-8.6-6-9.95-10.55C294.2 65.54 277.8 48 256 48s-38.21 17.55-44 37.47c-1.35 4.6-5.52 8.71-9.95 10.53c-33.39 13.75-73.87 41.92-73.87 121.35C128.13 304 110 320 84.32 351.43C73.68 364.45 83 384 101.61 384h308.88c18.51 0 27.77-19.61 17.19-32.57M320 384v16a64 64 0 0 1-128 0v-16"></path>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Notifications</div>
          <div class="ios-set__description">{{ toggles.notifications ? '允许通知 · 12 个应用' : '通知已静音' }}</div>
        </div>
        <div class="ios-set__switch" :class="{ on: toggles.notifications }"><span></span></div>
      </div>

      <!-- Privacy & Security：弹气泡 -->
      <div class="ios-set__card" @click="tap('privacy')">
        <div class="ios-set__icon" style="background: linear-gradient(135deg, #007aff, #00c4ff);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"></path>
          </svg>
        </div>
        <div class="ios-set__content">
          <div class="ios-set__title">Privacy & Security</div>
          <div class="ios-set__description">Face ID 已启用 · 此设备安全</div>
        </div>
        <div class="ios-set__chev">›</div>
        <div v-if="popover === 'privacy'" class="ios-set__popover">
          <div class="ios-set__popover-title">🛡️ 隐私与安全</div>
          <div class="ios-set__popover-row"><span>Face ID</span><b>已开启</b></div>
          <div class="ios-set__popover-row"><span>跟踪请求</span><b>0 条待处理</b></div>
          <div class="ios-set__popover-row"><span>密码</span><b>•••••••</b></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ios-set { display: flex; justify-content: center; }

/* 容器：圆角玻璃面板 */
.ios-set__container {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro", sans-serif;
  max-width: 300px;
  width: 100%;
  height: 420px;
  background-color: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border-radius: 18px;
  padding: 14px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow-y: auto;
  position: relative;
  scrollbar-width: none;
}
.ios-set__container::-webkit-scrollbar { display: none; }
.dark .ios-set__container {
  background-color: rgba(28, 28, 30, 0.92);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.ios-set__header {
  font-size: 20px;
  font-weight: 600;
  color: #000;
  margin: 8px 0 14px 12px;
  letter-spacing: -0.4px;
}
.dark .ios-set__header { color: #f5f5f7; }

/* 卡片 */
.ios-set__card {
  position: relative;
  display: flex;
  flex-wrap: wrap; /* 气泡展开时换行到卡片内，撑高卡片而不遮挡其它卡 */
  align-items: center;
  background-color: #fff;
  border-radius: 12px;
  padding: 12px 14px;
  margin: 4px 0;
  cursor: pointer;
  transition: transform 0.1s ease, background-color 0.25s ease, box-shadow 0.25s ease;
  opacity: 0;
  transform: translateY(12px);
  animation: ios-set__fadeInUp 0.35s cubic-bezier(0.28, 0.11, 0.32, 1) forwards;
}
.dark .ios-set__card { background-color: #1c1c1e; }
.ios-set__card:hover { background-color: #f7f7f8; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); }
.dark .ios-set__card:hover { background-color: #2c2c2e; }
.ios-set__card:active { transform: scale(0.96); transition: transform 0.1s ease; }
.ios-set__card:nth-child(1) { animation-delay: 0.05s; }
.ios-set__card:nth-child(2) { animation-delay: 0.10s; }
.ios-set__card:nth-child(3) { animation-delay: 0.15s; }
.ios-set__card:nth-child(4) { animation-delay: 0.20s; }
.ios-set__card:nth-child(5) { animation-delay: 0.25s; }
.ios-set__card:nth-child(6) { animation-delay: 0.30s; }
.ios-set__card:nth-child(7) { animation-delay: 0.35s; }
.ios-set__card:nth-child(8) { animation-delay: 0.40s; }
.ios-set__card:nth-child(9) { animation-delay: 0.45s; }
@keyframes ios-set__fadeInUp { to { opacity: 1; transform: translateY(0); } }

/* 图标方块 */
.ios-set__icon {
  width: 34px;
  height: 34px;
  margin-right: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 10px;
  transition: filter 0.25s, transform 0.25s;
  flex-shrink: 0;
}
.ios-set__icon svg { width: 22px; height: 22px; }
.ios-set__card:hover .ios-set__icon { transform: scale(1.05); }
.ios-set__icon.is-on { filter: saturate(1.15) brightness(1.05); }

/* 内容 */
.ios-set__content { flex: 1; min-width: 0; }
.ios-set__title {
  font-size: 16px;
  font-weight: 500;
  color: #000;
  margin: 0;
  letter-spacing: -0.3px;
}
.dark .ios-set__title { color: #f5f5f7; }
.ios-set__description {
  font-size: 13px;
  color: #6b7280;
  margin: 2px 0 0;
  line-height: 1.3;
}
.dark .ios-set__description { color: #9aa0a6; }

/* 右侧箭头 */
.ios-set__chev {
  color: #c7c7cc;
  font-size: 18px;
  margin-left: 8px;
}
.dark .ios-set__chev { color: #48484a; }

/* 拨动开关 */
.ios-set__switch {
  position: relative;
  width: 44px;
  height: 26px;
  background: #e5e5ea;
  border-radius: 999px;
  margin-left: 8px;
  transition: background 0.3s;
  flex-shrink: 0;
}
.ios-set__switch span {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 22px;
  height: 22px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s;
}
.ios-set__switch.on { background: #34c759; }
.ios-set__switch.on span { transform: translateX(18px); }
.dark .ios-set__switch { background: #39393d; }
.dark .ios-set__switch.on { background: #30d158; }

/* 亮度滑条 */
.ios-set__slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(to right, #007aff 0%, #007aff var(--val, 72%), #d1d1d6 var(--val, 72%), #d1d1d6 100%);
  margin-top: 8px;
  outline: none;
  cursor: pointer;
}
.ios-set__slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  cursor: pointer;
}
.ios-set__slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: #fff;
  border: none;
  border-radius: 50%;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  cursor: pointer;
}
.dark .ios-set__slider {
  background: linear-gradient(to right, #0a84ff 0%, #0a84ff var(--val, 72%), #48484a var(--val, 72%), #48484a 100%);
}

/* 弹气泡（Wi-Fi / Cellular / Battery / Privacy）*/
.ios-set__popover {
  /* 文档流内展开：卡片自己长高，把下面的卡片推下去，不再互相遮挡 */
  flex-basis: 100%;
  margin-top: 10px;
  background: rgba(245, 245, 245, 0.96);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  padding: 10px 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  z-index: 20;
  animation: ios-set__pop 0.18s ease-out;
}
.dark .ios-set__popover { background: rgba(44, 44, 46, 0.96); }
.ios-set__popover-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #000;
}
.dark .ios-set__popover-title { color: #f5f5f7; }
.ios-set__popover-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #3a3a3c;
  line-height: 1.7;
}
.dark .ios-set__popover-row { color: #d1d1d6; }
.ios-set__popover-row b { font-weight: 500; color: #007aff; }
.dark .ios-set__popover-row b { color: #0a84ff; }

/* 进度条 */
.ios-set__bar {
  height: 8px;
  background: #d1d1d6;
  border-radius: 999px;
  overflow: hidden;
  margin: 6px 0;
}
.ios-set__bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #34c759, #30d158);
  border-radius: 999px;
  transition: width 0.4s;
}
.dark .ios-set__bar { background: #48484a; }

/* 电池 */
.ios-set__battery {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 8px 0;
}
.ios-set__battery-shell {
  width: 80px;
  height: 28px;
  border: 2px solid #1d0e01;
  border-radius: 5px;
  padding: 2px;
  background: #fff;
}
.ios-set__battery-fill {
  height: 100%;
  background: linear-gradient(90deg, #34c759, #30d158);
  border-radius: 2px;
  transition: width 0.4s;
}
.ios-set__battery-tip {
  width: 3px;
  height: 12px;
  background: #1d0e01;
  border-radius: 0 2px 2px 0;
  margin-left: 1px;
}

@keyframes ios-set__pop {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .ios-set__card { animation: none; opacity: 1; transform: none; }
}
</style>
