// 中国行政区划三级树：省 → 市 → 区/县
// 数据来源：npm 包 china-region v1.4.1（按 GB/T 2260 行政区划代码）
// 该包提供扁平数据（行政代码 → 名称），本模块构建成树形结构供级联选择器使用
import provinceData from './province.json' // [[code, name, shortName], ...]
import regionMap from './region.json'     // { code: name }

// 树形化：
// - 省级：code 以 "0000" 结尾（provinceData 给出的 34 条）
// - 市级：code 末尾为 "00" 且不是省级 → 归属到所属省级（按前 2 位）
// - 区/县级：code 末尾不是 "00" → 归属到所属市级（按前 4 位）

function buildTree() {
  const allCodes = Object.keys(regionMap)

  // 1. 省级
  const provinces = provinceData.map(([code, name, shortName]) => {
    const provincePrefix = code.slice(0, 2)
    // 该省的市级条目（末 2 位 = 00）
    const cities = []
    for (const c of allCodes) {
      if (c === code) continue
      if (!c.startsWith(provincePrefix)) continue
      if (!c.endsWith('00')) continue
      const cityPrefix = c.slice(0, 4)
      // 该市的区/县（不在省级、以市级 4 位开头、不以 00 结尾）
      const districts = []
      for (const d of allCodes) {
        if (!d.startsWith(cityPrefix)) continue
        if (d === c) continue
        if (d.endsWith('00')) continue
        // 跳过 12 位镇/街道级别
        if (d.length > 6) continue
        districts.push({ code: d, name: regionMap[d] })
      }
      cities.push({ code: c, name: regionMap[c], districts })
    }

    // ★ 直辖市/省直辖县级市等"无中间市级"的特殊处理
    // 这种情况：省级下没有以省前缀 + 'XX00' 的市级条目，但有以省前缀开头的区/县级条目
    // （如上海 310000 下没有 310100，但有 310101 黄浦区）
    // 把这些区/县级条目直接作为"二级"暴露给 picker（用一个虚拟"市辖区"包装）
    if (cities.length === 0) {
      const directDivisions = []
      for (const d of allCodes) {
        if (!d.startsWith(provincePrefix)) continue
        if (d === code) continue
        // 跳过省级条目（北京市/上海市等已是省级，不进二级）
        if (d.endsWith('0000')) continue
        // 只收"XXYYZZ" 6 位中末两位非 00 的（避免把省级自带的 xx0000 算进来）
        if (d.endsWith('00')) continue
        if (d.length > 6) continue
        directDivisions.push({ code: d, name: regionMap[d] })
      }
      directDivisions.sort((a, b) => a.code.localeCompare(b.code))
      if (directDivisions.length) {
        cities.push({
          code: code + '000', // 虚拟市级 code：上海市辖区 → 310000000（实际不会出现于 region.json，纯粹标识）
          name: '市辖区',
          districts: directDivisions,
          isVirtual: true
        })
      }
    }

    cities.sort((a, b) => a.code.localeCompare(b.code))
    cities.forEach(c => c.districts.sort((a, b) => a.code.localeCompare(b.code)))
    return { code, name, shortName, cities }
  })

  return provinces
}

// 单例：模块加载时构建一次
const TREE = buildTree()

export function listProvinces() {
  return TREE.map(p => ({ code: p.code, name: p.name, shortName: p.shortName }))
}

export function listCities(provinceCode) {
  const p = TREE.find(x => x.code === provinceCode)
  return p ? p.cities : []
}

export function listDistricts(cityCode) {
  for (const p of TREE) {
    const c = p.cities.find(x => x.code === cityCode)
    if (c) return c.districts
  }
  return []
}

export function getDefault() {
  // 默认：江苏省 → 常州市 → 新北区（GB 2260 代码 320411）
  return {
    provinceCode: '320000',  // 江苏省
    cityCode: '320400',      // 常州市
    districtCode: '320411',  // 新北区
    provinceName: '江苏省',
    cityName: '常州市',
    districtName: '新北区'
  }
}