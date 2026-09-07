import { fileURLToPath } from 'node:url'
import { dirname, resolve, extname } from 'node:path'
import { readdirSync, statSync, readFileSync, existsSync } from 'node:fs'
import taskLists from 'markdown-it-task-lists'

const __dirname = dirname(fileURLToPath(import.meta.url))

/** ============================================================
 *  可配置项
 *  ============================================================ */
const NOTES_ROOT   = resolve(__dirname, '../../notes') // ./notes
const BASE_PREFIX  = '/notes/'                          // 路由前缀
const SITE_BASE    = '/'                                // 子域名部署：保持 '/'
const SITE_DESC    = '~/bbben — bbben 的个人 Markdown 笔记，持续记录。'

/** ============================================================
 *  工具：从 front-matter 读取 title，否则用文件名
 *  ============================================================ */
function readTitleFromFrontMatter(file) {
  try {
    const txt = readFileSync(file, 'utf-8')
    const m = txt.match(/^---\s*\n([\s\S]*?)\n---/)
    if (m) {
      const t = m[1].match(/^title:\s*['"]?(.+?)['"]?\s*$/m)
      if (t) return t[1].trim()
    }
  } catch {}
  return null
}

function prettyTitle(filename) {
  const base = filename.replace(/\.md$/i, '')
  // 处理日期前缀：2024-01-15-morning-run → 2024-01-15 · morning run
  const m = base.match(/^(\d{4}-\d{2}-\d{2})[-_](.+)$/)
  if (m) return `${m[1]} · ${m[2].replace(/[-_]/g, ' ')}`
  return base.replace(/[-_]/g, ' ')
}

/** ============================================================
 *  工具：递归扫描目录树 → VitePress sidebar 格式
 *  ============================================================ */
function buildSidebar(dir, urlPrefix = BASE_PREFIX) {
  let entries
  try {
    entries = readdirSync(dir, { withFileTypes: true })
  } catch {
    return []
  }

  // ★ 防呆：检测大小写冲突（Linux 与 linux 同时存在）
  const lowerSeen = new Map()
  for (const e of entries) {
    const lower = e.name.toLowerCase()
    if (lowerSeen.has(lower)) {
      console.warn(`[vitepress] ⚠ 目录大小写冲突：'${lowerSeen.get(lower)}' 和 '${e.name}' 共存，会产生重复路由。请统一为一种大小写。`)
    }
    lowerSeen.set(lower, e.name)
  }

  const visible = entries.filter(e => !e.name.startsWith('.'))
  visible.sort((a, b) => {
    if (a.isDirectory() !== b.isDirectory()) return a.isDirectory() ? -1 : 1
    return a.name.localeCompare(b.name, 'zh-Hans-CN')
  })

  const items = []
  for (const e of visible) {
    const fullPath = resolve(dir, e.name)
    const linkUrl  = urlPrefix + e.name.replace(/\.md$/, '')

    if (e.isDirectory()) {
      const children = buildSidebar(fullPath, linkUrl + '/')
      if (children.length) {
        items.push({ text: e.name, collapsed: true, items: children })
      }
    } else if (e.isFile() && e.name.endsWith('.md')) {
      const title = readTitleFromFrontMatter(fullPath) ?? prettyTitle(e.name)
      items.push({ text: title, link: linkUrl })
    }
  }
  return items
}

/**
 * 构建树形结构（给首页 NotesTree 组件用）
 * 格式：[{ name, type: 'directory'|'file', title?, link?, children? }]
 */
function buildTree(dir, urlPrefix = BASE_PREFIX) {
  let entries
  try {
    entries = readdirSync(dir, { withFileTypes: true })
  } catch {
    return []
  }

  const lowerSeen = new Map()
  for (const e of entries) {
    const lower = e.name.toLowerCase()
    if (lowerSeen.has(lower)) {
      console.warn(`[vitepress] ⚠ 目录大小写冲突：'${lowerSeen.get(lower)}' 和 '${e.name}'`)
    }
    lowerSeen.set(lower, e.name)
  }

  const visible = entries.filter(e => !e.name.startsWith('.'))
  visible.sort((a, b) => {
    if (a.isDirectory() !== b.isDirectory()) return a.isDirectory() ? -1 : 1
    return a.name.localeCompare(b.name, 'zh-Hans-CN')
  })

  const nodes = []
  for (const e of visible) {
    const fullPath = resolve(dir, e.name)

    if (e.isDirectory()) {
      const children = buildTree(fullPath, urlPrefix + e.name + '/')
      if (children.length) {
        nodes.push({
          name: e.name,
          type: 'directory',
          children
        })
      }
    } else if (e.isFile() && e.name.endsWith('.md')) {
      const link = urlPrefix + e.name.replace(/\.md$/, '')
      const title = readTitleFromFrontMatter(fullPath) ?? prettyTitle(e.name)
      nodes.push({
        name: e.name,
        type: 'file',
        title,
        link
      })
    }
  }
  return nodes
}

const sidebar = {
  // ★ 让侧边栏在所有路径（包括首页 /）都显示
  '/': buildSidebar(NOTES_ROOT),
  [BASE_PREFIX]: buildSidebar(NOTES_ROOT)
}

// ★ 给首页 NotesTree 组件用的完整树
const notesTree = buildTree(NOTES_ROOT)

/** ============================================================
 *  手机播放器歌单：扫描 docs/public/music/ 下的音频文件自动生成
 *  - 支持 mp3 / flac / wav / ogg / m4a / aac / opus
 *  - 文件名（去扩展名）就是歌名：晴天.flac → 「晴天」
 *  - 同名图片（晴天.png/jpg/webp...）自动作为该曲封面
 *  - 加/换歌后需重新 npm run dev 或 npm run build 生效
 *  ============================================================ */
const MUSIC_DIR = resolve(__dirname, '../public/music')
const AUDIO_EXTS = ['.mp3', '.flac', '.mflac', '.wav', '.ogg', '.m4a', '.aac', '.opus']
const IMG_EXTS = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif']

function buildPhonePlaylist() {
  try {
    if (!existsSync(MUSIC_DIR)) return []
    return readdirSync(MUSIC_DIR, { withFileTypes: true })
      .filter(e => e.isFile() && AUDIO_EXTS.includes(extname(e.name).toLowerCase()))
      .sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'))
      .map(e => {
        const base = e.name.replace(/\.[^.]+$/, '')
        const coverImg = IMG_EXTS.map(ext => base + ext).find(name =>
          existsSync(resolve(MUSIC_DIR, name))
        )
        return {
          src: `/music/${encodeURIComponent(e.name)}`,
          title: base,
          ...(coverImg ? { cover: `/music/${coverImg}` } : {})
        }
      })
  } catch {
    return []
  }
}

const phonePlaylist = buildPhonePlaylist()

/** ============================================================
 *  导出配置
 *  ============================================================ */
export default {
  title: '~/bbben',
  description: SITE_DESC,
  base: SITE_BASE,
  lastUpdated: true,
  cleanUrls: true,
  appearance: 'auto',  // 浅色为主（Apple 风），跟随系统
  ignoreDeadLinks: true,

  themeConfig: {
    // ★ 纯文字站名（Apple 风，避免 logo + 文字重复）
    logo: undefined,
    siteTitle: '~/bbben',

    nav: [
      { text: '首页', link: '/' },
      { text: '关于', link: '/about' },
      { text: '实验室', link: '/fun' }
    ],

    sidebar,

    search: {
      provider: 'local',
      options: {
        miniSearch: {
          searchOptions: { fuzzy: 0.2, prefix: true, boost: { title: 4, text: 1 } }
        }
      }
    },

    outline: { level: [2, 3], label: '本页目录' },

    docFooter: { prev: '上一篇', next: '下一篇' },

    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换为浅色',
    darkModeSwitchTitle: '切换为深色',

    socialLinks: [
      // ★ 改这里：替换成你自己的链接
      { icon: 'github', link: 'https://github.com/Mike666wq' }
      // 可以加更多社交图标，例如：
      // { icon: 'twitter', link: 'https://twitter.com/your-name' }
      // { icon: 'discord', link: 'https://discord.gg/your-invite' }
    ],

    footer: {
      message: `
        <span>© ${new Date().getFullYear()} <code>~/bbben</code> · bbben · Powered by <a href="https://vitepress.dev/" target="_blank">VitePress</a></span><br/>
        <span style="opacity:.7;font-size:0.85em">最后构建于 ${new Date().toISOString().replace('T', ' ').slice(0, 16)} UTC</span>
      `,
      copyright: false
    },

    docFooterText: { prev: '上一篇', next: '下一篇' },

    // ★ 把树结构注入 themeConfig 透传到 siteData
    // （VitePress 1.x 的 userConfig.siteData 不被识别，必须挂在 themeConfig 里）
    customNotesTree: notesTree,

    // ★ 手机播放器歌单（扫描 public/music/ 自动生成）
    phonePlaylist
  },

  markdown: {
    config: md => md.use(taskLists, { enabled: true, label: true }),
    // ★ Apple 风格：不需要行号
    lineNumbers: false,
    // ★ 统一代码高亮主题
    theme: {
      light: 'vitesse-light',
      dark: 'vitesse-dark'
    }
  },

  // ★ 防御：图片资源解析失败时不中断构建（降级为警告）
  //     解决：用户笔记里写 <img src="中文路径/..."> 时的 Rollup 报错
  vite: {
    server: {
      // ★ 局域网访问：监听全部网卡，手机/其他电脑可通过 http://电脑IP:5173 访问
      host: '0.0.0.0',
      port: 5173,
      // ★ 允许通过自定义主机名（如 mint、bbben.local 等 hosts 里映射的名字）访问
      //    默认 Vite 只放行 localhost / 127.0.0.1 / ::1，自定义主机名会被拒（DNS rebinding 保护）
      //    局域网下用任意 IP/主机名都能访问就设 true；想限定可以写成 ['mint', '192.168.31.60']
      allowedHosts: true,
      watch: {
        // ★ 关键：排除 Python 虚拟环境和 node_modules，避免 VitePress dev 文件监视器崩溃（ENOSPC）
        ignored: ['**/.venv/**', '**/node_modules/**', '**/__pycache__/**', '**/.git/**']
      }
    },
    preview: {
      // ★ 预览服务（npm run preview）也开放到局域网，端口 4173
      host: '0.0.0.0',
      port: 4173
    },
    build: {
      rollupOptions: {
        // 任何无法解析的 import（典型：中文路径被当模块名）→ 视为外部依赖，跳过
        // VitePress 会把图片引用转成 import，这个钩子确保失败时只是警告
        onwarn(warning, defaultHandler) {
          if (warning.code === 'UNRESOLVED_IMPORT' || warning.code === 'MISSING_EXPORT') {
            console.warn(`[vite] 已跳过未解析的 import：${warning.message?.split('\n')[0] || ''}`)
            return
          }
          defaultHandler(warning)
        }
      }
    }
  },

  head: [
    ['link', { rel: 'icon', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#3b82f6' }]
  ]
}
