<script setup>
// 天气卡（左侧栏底部）—— 恢复原始 Uiverse 的悬停展开交互
// 数据：Open-Meteo 免费 API（geocoding + forecast + air-quality），无需 key
// 交互：
//   - 默认紧凑（天气+温度+城市），悬停/聚焦时展开
//   - 点击城市名 → 弹出三级级联选择（省 → 市 → 区/县）
//   - 选择区/县后再次查询 Open-Meteo 拉取该位置的预报
//   - 用户选择持久化到 localStorage
import { ref, computed, onMounted, watch } from 'vue'
import { listProvinces, listCities, listDistricts, getDefault } from '../data/chinaRegions/index.js'

const LS_KEY = 'weather.location.v1'

// 当前选中（code + name），默认常州新北区
const selected = ref(getDefault())
// 内部 state：是否显示选择器
const showPicker = ref(false)
// 临时编辑态：级联选择器中途状态（提交前不写回 selected）
const draft = ref({ ...selected.value })

const temp = ref('—')
const humidity = ref('—')
const wind = ref('—')
const realfeel = ref('—')
const pressure = ref('—')
// 头部显示：始终反映 picker 选中的位置（district > city > province，取最具体的）
// 不再用 API 返回的 name 覆盖，避免"选了北京但显示重庆"的错位感
const cityName = computed(() => {
  const s = selected.value
  const local = s.districtName || s.cityName || s.provinceName
  return `${local}, ${s.provinceName}`
})
const aqi = ref('—')
const aqiLevel = ref('')
const wxIcon = ref('☀️')
const loadingLoc = ref(false)
const locError = ref('')

const provinces = listProvinces()
const cities = computed(() => listCities(draft.value.provinceCode))
const districts = computed(() => listDistricts(draft.value.cityCode))

function persist() {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(selected.value))
  } catch {}
}
function restore() {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (!raw) return false
    const obj = JSON.parse(raw)
    // 粗略校验：默认值必填
    if (!obj.provinceCode || !obj.cityCode || !obj.districtCode) return false
    // 校验省/市/区在树里都存在（防止旧版本残留）
    if (!provinces.find(p => p.code === obj.provinceCode)) return false
    if (!listCities(obj.provinceCode).find(c => c.code === obj.cityCode)) return false
    if (!listDistricts(obj.cityCode).find(d => d.code === obj.districtCode)) return false
    selected.value = obj
    draft.value = { ...obj }
    return true
  } catch { return false }
}

// Open-Meteo 对中国地名查询极不一致：
//   - "常州市"能查到（特例），但"盐城市/南京市/苏州市"都查不到（"市"后缀被忽略）
//   - 必须剥掉"省/市/区/县"等行政区划后缀再查，但又要挨个试（"常州"反而查不到，"常州市"可以）
//   - 返回的 name 字段是简名（如"盐城"），用用户原选名显示更友好
function stripSuffix(name) {
  // 顺序很重要：先剥长的后缀（"自治州" "自治县"），再剥短的
  return name
    .replace(/自治[州县]$/, '')
    .replace(/特别行政区$/, '')
    .replace(/(?:省|市|区|县)$/, '')
}

async function geocoding(candidates) {
  // 对每个候选名，剥后缀和不剥后缀两个版本都试一遍；区/县 → 市 → 省逐级降级
  for (const name of candidates) {
    const stripped = stripSuffix(name)
    for (const variant of [name, stripped]) {
      if (!variant) continue
      const q = encodeURIComponent(variant)
      try {
        const res = await fetch(
          `https://geocoding-api.open-meteo.com/v1/search?name=${q}&count=1&language=zh&countryCode=CN`
        )
        const json = await res.json()
        const loc = json.results?.[0]
        if (loc) return loc
      } catch {}
    }
  }
  return null
}

async function geocodeAndLoad(districtName, cityNameZh, provinceName) {
  // 三层 fallback：区/县 → 市 → 省。Open-Meteo 对中国区级覆盖很差，自动降级到市级坐标
  const loc = await geocoding([districtName, cityNameZh, provinceName])
  if (!loc) throw new Error('未找到该地的坐标')
  // 头部 cityName 用 computed 派生自 selected.value，不再被 API 返回值覆盖
  //（API 只用于取坐标，不用于改显示文案——避免"选了北京但显示重庆"的错位感）

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
  if (!c) throw new Error('无当前天气数据')
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
}

async function load() {
  loadingLoc.value = true
  locError.value = ''
  try {
    await geocodeAndLoad(
      selected.value.districtName,
      selected.value.cityName,
      selected.value.provinceName
    )
  } catch (e) {
    locError.value = e.message || '天气加载失败'
    // 失败时保留现有值
  } finally {
    loadingLoc.value = false
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

function openPicker() {
  // 打开时复制当前选择作为草稿
  draft.value = { ...selected.value }
  // 防止省级已选但市/区不存在（极端情况：换省后旧的市/区在新省失效）
  if (!cities.value.find(c => c.code === draft.value.cityCode)) {
    draft.value.cityCode = cities.value[0]?.code || ''
  }
  if (!districts.value.find(d => d.code === draft.value.districtCode)) {
    draft.value.districtCode = districts.value[0]?.code || ''
  }
  showPicker.value = true
}
function closePicker() {
  showPicker.value = false
}

function onProvinceChange() {
  // 切换省级后重置市/区到该省第一个市/第一个区
  const firstCity = cities.value[0]
  draft.value.cityCode = firstCity?.code || ''
  draft.value.districtName = ''
  draft.value.districtCode = ''
  // 自动选第一个市/区
  const firstDist = listDistricts(draft.value.cityCode)[0]
  draft.value.districtCode = firstDist?.code || ''
  draft.value.districtName = firstDist?.name || ''
  // 同步名字
  const prov = provinces.find(p => p.code === draft.value.provinceCode)
  const city = firstCity
  draft.value.provinceName = prov?.name || ''
  draft.value.cityName = city?.name || ''
}
function onCityChange() {
  const firstDist = districts.value[0]
  draft.value.districtCode = firstDist?.code || ''
  draft.value.districtName = firstDist?.name || ''
  const city = cities.value.find(c => c.code === draft.value.cityCode)
  draft.value.cityName = city?.name || ''
}

async function confirmPicker() {
  // 同步选中
  const prov = provinces.find(p => p.code === draft.value.provinceCode)
  const city = cities.value.find(c => c.code === draft.value.cityCode)
  const dist = districts.value.find(d => d.code === draft.value.districtCode)
  if (!prov || !city || !dist) {
    locError.value = '请选择完整的省/市/区'
    return
  }
  // ★ 直辖市场景：city 是虚拟"市辖区"——cityName 直接用省名（如"上海市"），避免显示"上海市辖区"
  const isVirtual = city.isVirtual
  selected.value = {
    provinceCode: prov.code,
    provinceName: prov.name,
    cityCode: city.code,
    cityName: isVirtual ? prov.name : city.name,
    districtCode: dist.code,
    districtName: dist.name
  }
  showPicker.value = false
  locError.value = ''
  persist()
  await load()
}

onMounted(async () => {
  restore()
  await load()
})
</script>

<template>
  <div
    class="weather-card"
    tabindex="0"
    role="region"
    :aria-label="`天气：${cityName} ${temp}°C`"
  >
    <!-- 头部：始终可见，点击城市名打开选择器 -->
    <div class="header">
      <span class="weather">{{ wxIcon }}</span>
      <div class="info">
        <div class="main">{{ temp }}°C</div>
        <button class="city" type="button" :aria-label="`当前城市：${cityName}，点击切换`" @click.stop="openPicker">
          {{ cityName }} <span class="caret">▾</span>
        </button>
      </div>
    </div>

    <!-- 详情：默认折叠，悬停/聚焦展开 -->
    <div v-if="!showPicker" class="details">
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

      <div class="status">{{ temp !== '—' ? 'Healthy' : (locError || '—') }}</div>
    </div>

    <!-- 选择器：三级级联（替代详情区显示） -->
    <div v-else class="picker" @click.stop>
      <div class="picker-title">选择地区</div>
      <label class="picker-row">
        <span>省</span>
        <select v-model="draft.provinceCode" @change="onProvinceChange">
          <option v-for="p in provinces" :key="p.code" :value="p.code">{{ p.name }}</option>
        </select>
      </label>
      <label class="picker-row">
        <span>市</span>
        <select v-model="draft.cityCode" @change="onCityChange">
          <option v-for="c in cities" :key="c.code" :value="c.code">{{ c.name }}</option>
        </select>
      </label>
      <label class="picker-row">
        <span>区</span>
        <select v-model="draft.districtCode">
          <option v-for="d in districts" :key="d.code" :value="d.code">{{ d.name }}</option>
        </select>
      </label>
      <div class="picker-actions">
        <button type="button" class="btn-cancel" @click="closePicker">取消</button>
        <button type="button" class="btn-confirm" :disabled="loadingLoc" @click="confirmPicker">
          {{ loadingLoc ? '加载中…' : '确定' }}
        </button>
      </div>
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
  /* 默认紧凑、悬停/聚焦展开 */
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
  background: #fff8d6;
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
/* 城市名：改为 button，可点击；不破坏悬停展开 */
.city {
  font-size: 11px;
  opacity: 0.7;
  background: none;
  border: 0;
  padding: 0;
  margin-top: 2px;
  color: inherit;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: opacity 0.15s ease, color 0.15s ease;
}
.city:hover { opacity: 1; color: #d97706; }
.caret { font-size: 9px; opacity: 0.6; }

/* 详情块 */
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

/* 选择器 */
.picker {
  padding: 6px 4px 4px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 0;
  animation: picker-in 0.25s ease forwards;
}
@keyframes picker-in {
  to { opacity: 1; }
}
.picker-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-align: center;
  margin-bottom: 2px;
}
.picker-row {
  display: grid;
  grid-template-columns: 28px 1fr;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  opacity: 0.7;
}
.picker-row select {
  width: 100%;
  font-size: 12px;
  padding: 4px 6px;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: white;
  color: #1f2937;
  cursor: pointer;
  outline: none;
}
.picker-row select:focus {
  border-color: #f59e0b;
}
.picker-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.picker-actions button {
  flex: 1;
  padding: 6px 0;
  border: 0;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.15s ease;
}
.btn-cancel {
  background: rgba(0, 0, 0, 0.06);
  color: #1f2937;
}
.btn-cancel:hover { background: rgba(0, 0, 0, 0.1); }
.btn-confirm {
  background: limegreen;
  color: white;
}
.btn-confirm:hover { opacity: 0.9; }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

@media (prefers-reduced-motion: reduce) {
  .weather-card,
  .details,
  .picker { transition: none; animation: none; }
}
</style>