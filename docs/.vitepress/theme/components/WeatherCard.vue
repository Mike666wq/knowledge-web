<script setup>
// 天气卡（左侧栏底部）—— 恢复原始 Uiverse 的悬停展开交互
// 数据：Open-Meteo 免费 API（geocoding + forecast + air-quality），无需 key
// 交互：默认紧凑（天气+温度+城市），悬停/聚焦时展开显示其他字段 + Healthy
import { ref, onMounted } from 'vue'

const props = defineProps({
  city: { type: String, default: 'Changzhou' },
})

const temp = ref('—')
const humidity = ref('—')
const wind = ref('—')
const realfeel = ref('—')
const pressure = ref('—')
const cityName = ref(props.city)
const aqi = ref('—')
const aqiLevel = ref('')
const wxIcon = ref('☀️')

async function load() {
  try {
    const geoRes = await fetch(
      `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(props.city)}&count=1&language=zh`
    )
    const geo = await geoRes.json()
    const loc = geo.results?.[0]
    if (!loc) return
    cityName.value = loc.name + (loc.admin1 ? `, ${loc.admin1}` : '')

    const [wxRes, airRes] = await Promise.all([
      fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${loc.latitude}&longitude=${loc.longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,apparent_temperature,surface_pressure,weather_code&timezone=auto`
      ),
      fetch(
        `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${loc.latitude}&longitude=${loc.longitude}&current=us_aqi&timezone=auto`
      ),
    ])
    const [wx, air] = await Promise.all([wxRes.json(), airRes.json()])
    const c = wx.current
    if (!c) return
    temp.value = Math.round(c.temperature_2m)
    humidity.value = c.relative_humidity_2m
    wind.value = Math.round(c.wind_speed_10m)
    realfeel.value = Math.round(c.apparent_temperature)
    pressure.value = Math.round(c.surface_pressure)
    wxIcon.value = wmoIcon(c.weather_code)
    if (air.current?.us_aqi != null) {
      const a = Math.round(air.current.us_aqi)
      aqi.value = a
      aqiLevel.value = aqiLabel(a)
    }
  } catch (e) {
    // 网络失败时保留 "—"
  }
}

function aqiLabel(a) {
  if (a <= 50) return '优'
  if (a <= 100) return '良'
  if (a <= 150) return '轻度'
  if (a <= 200) return '中度'
  if (a <= 300) return '重度'
  return '严重'
}

function wmoIcon(code) {
  if (code == null) return '☀️'
  if (code === 0) return '☀️'
  if (code <= 3) return '⛅'
  if (code === 45 || code === 48) return '🌫️'
  if (code >= 51 && code <= 57) return '🌦️'
  if (code >= 61 && code <= 67) return '🌧️'
  if (code >= 71 && code <= 77) return '❄️'
  if (code >= 80 && code <= 82) return '🌧️'
  if (code >= 95) return '⛈️'
  return '☀️'
}

onMounted(load)
</script>

<template>
  <div
    class="weather-card"
    tabindex="0"
    role="region"
    :aria-label="`天气：${cityName} ${temp}°C`"
  >
    <!-- 头部：始终可见 -->
    <div class="header">
      <span class="weather">{{ wxIcon }}</span>
      <div class="info">
        <div class="main">{{ temp }}°C</div>
        <div class="city">{{ cityName }}</div>
      </div>
    </div>

    <!-- 详情：默认折叠，悬停/聚焦展开 -->
    <div class="details">
      <div class="divider"></div>
      <div class="row">
        <div class="cell">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3 C 8 9 6 12 6 15 a 6 6 0 0 0 12 0 c 0-3-2-6-6-12 z"></path>
          </svg>
          <div class="label">湿度</div>
          <div class="value">{{ humidity }}%</div>
        </div>
        <div class="cell">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 9 h11 a3 3 0 1 0 -3 -3"></path>
            <path d="M3 14 h15 a3 3 0 1 1 -3 3"></path>
            <path d="M5 19 h9"></path>
          </svg>
          <div class="label">风速</div>
          <div class="value">{{ wind }} km/h</div>
        </div>
      </div>

      <div class="row">
        <div class="cell">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <rect x="6" y="3" width="12" height="18" rx="2"></rect>
            <circle cx="12" cy="14" r="3"></circle>
          </svg>
          <div class="label">AQI</div>
          <div class="value">{{ aqi }}<span v-if="aqiLevel" class="level"> {{ aqiLevel }}</span></div>
        </div>
        <div class="cell">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 4 v10.54 a4 4 0 1 1 -4 0 V4 a2 2 0 0 1 4 0 z"></path>
          </svg>
          <div class="label">体感</div>
          <div class="value">{{ realfeel }}°C</div>
        </div>
        <div class="cell">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M12 7 v5 l3 3"></path>
          </svg>
          <div class="label">气压</div>
          <div class="value">{{ pressure }}</div>
        </div>
      </div>

      <div class="status">{{ temp !== '—' ? 'Healthy' : '—' }}</div>
    </div>
  </div>
</template>

<style scoped>
.weather-card {
  background: whitesmoke;
  color: #1f2937;
  border-radius: 16px;
  padding: 12px 14px;
  margin: 0 12px 16px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
  font-size: 12px;
  line-height: 1.3;
  /* 关键：默认紧凑、悬停/聚焦展开（复刻原 Uiverse 交互）*/
  max-height: 90px;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease;
  cursor: pointer;
  outline: none;
}
.weather-card:hover,
.weather-card:focus-within {
  max-height: 360px;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
  background: #fff8d6; /* 悬停微变黄 */
}
.weather-card:focus-visible {
  outline: 2px solid #f59e0b;
  outline-offset: 2px;
}

.header {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 66px;
}
.weather {
  font-size: 32px;
  line-height: 1;
  flex: none;
}
.info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}
.main {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.01em;
}
.city {
  font-size: 11px;
  opacity: 0.65;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 2px;
}

/* 详情块：默认折叠 */
.details {
  opacity: 0;
  transition: opacity 0.3s ease;
}
.weather-card:hover .details,
.weather-card:focus-within .details {
  opacity: 1;
  transition-delay: 0.12s;
}

.divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.08);
  margin: 4px 0 6px;
}

.row {
  display: flex;
  gap: 4px;
  margin-bottom: 6px;
}
.cell {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 2px 0;
}
.cell svg {
  width: 18px;
  height: 18px;
  color: #1f2937;
  flex: none;
}
.cell .label {
  font-size: 10px;
  opacity: 0.6;
}
.cell .value {
  font-size: 12px;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
}
.cell .level {
  font-weight: 400;
  font-size: 10px;
  opacity: 0.7;
}

.status {
  background: limegreen;
  color: white;
  text-align: center;
  font-weight: 600;
  font-size: 13px;
  border-radius: 999px;
  padding: 6px 0;
  margin-top: 6px;
  letter-spacing: 0.05em;
}

@media (prefers-reduced-motion: reduce) {
  .weather-card,
  .details { transition: none; }
}
</style>