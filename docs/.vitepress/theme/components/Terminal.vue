<script setup>
import { ref, nextTick } from 'vue'

// 交互式终端：支持简单命令
const lines = ref([])
const input = ref('')
const inputEl = ref(null)
const isReady = ref(false)

// 启动横幅
const banner = [
  'Welcome to ~/bbben terminal',
  'Type "help" to see available commands.',
  '------------------------------------------------'
]

const commands = {
  help() {
    return 'Available commands: help, about, ls, whoami, date, clear'
  },
  about() {
    return 'bbben 的个人 Markdown 知识库.'
  },
  whoami() {
    return 'guest'
  },
  date() {
    return new Date().toString()
  },
  ls() {
    return 'safe/  ai-agent/  linux/  docs/  notes/'
  },
  neofetch() {
    return '┌─ ~/bbben ──────────────┐\n│ OS: bbben v0.1         │\n│ Shell: bash            │\n│ Notes: 70+             │\n│ Theme: Apple Style     │\n└────────────────────────┘'
  }
}

function init() {
  banner.forEach(l => lines.value.push({ type: 'out', text: l }))
  isReady.value = true
}

function run() {
  const cmd = input.value.trim()
  if (cmd) {
    lines.value.push({ type: 'cmd', text: cmd })
    if (cmd === 'clear') {
      lines.value = []
    } else if (commands[cmd]) {
      const res = commands[cmd]()
      res.split('\n').forEach(l => lines.value.push({ type: 'out', text: l }))
    } else {
      lines.value.push({ type: 'err', text: `command not found: ${cmd}` })
    }
    input.value = ''
  }
}

function onKeydown(e) {
  if (e.key === 'Enter') run()
}

init()
</script>

<template>
  <div class="terminal-window" @click="inputEl && inputEl.focus()">
    <div class="terminal_toolbar">
      <div class="butt">
        <button class="btn btn-color" aria-label="close"></button>
        <button class="btn" aria-label="min"></button>
        <button class="btn" aria-label="max"></button>
      </div>
      <p class="user">bbben@localhost: ~</p>
      <div class="add_tab">+</div>
    </div>
    <div class="terminal_body">
      <div v-for="(line, i) in lines" :key="i" class="terminal-line" :class="line.type">
        <span v-if="line.type === 'cmd'" class="term-promt">
          <span class="terminal_user">bbben@localhost:</span>
          <span class="terminal_location">~</span>
          <span class="terminal_bling">$</span>
        </span>
        <span class="term-text">{{ line.text }}</span>
      </div>
      <div class="terminal_promt">
        <span class="terminal_user">bbben@localhost:</span>
        <span class="terminal_location">~</span>
        <span class="terminal_bling">$</span>
        <input
          ref="inputEl"
          v-model="input"
          class="term-input"
          spellcheck="false"
          autocomplete="off"
          @keydown="onKeydown"
        />
        <span class="terminal_cursor"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.terminal-window {
  width: 100%;
  max-width: 560px;
  margin: 1rem auto;
  text-align: left;
  font-family: var(--vp-font-family-mono);
}

.terminal_toolbar {
  display: flex;
  height: 30px;
  align-items: center;
  padding: 0 8px;
  box-sizing: border-box;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  background: #212121;
  justify-content: space-between;
}

.butt { display: flex; align-items: center; }

.btn {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
  margin-right: 5px;
  font-size: 8px;
  height: 12px;
  width: 12px;
  box-sizing: border-box;
  border: none;
  border-radius: 100%;
  background: linear-gradient(#7d7871 0%, #595953 100%);
  box-shadow: 0px 0px 1px 0px #41403A, 0px 1px 1px 0px #474642;
}
.btn-color { background: #ee411a; }
.btn:hover { cursor: pointer; }
.btn:focus { outline: none; }

.add_tab {
  border: 1px solid #fff;
  color: #fff;
  padding: 0 6px;
  border-radius: 4px 4px 0 0;
  border-bottom: none;
  cursor: pointer;
}

.user {
  color: #d5d0ce;
  margin-left: 6px;
  font-size: 14px;
  line-height: 15px;
}

.terminal_body {
  background: rgba(12, 12, 16, 0.92);
  height: 220px;
  padding: 10px 12px;
  margin-top: -1px;
  font-size: 12px;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  overflow-y: auto;
  line-height: 1.7;
}

.terminal-line { display: flex; white-space: pre-wrap; }
.terminal-line .term-text { margin-left: 4px; color: #d5d0ce; }
.terminal-line.err .term-text { color: #ff7b72; }

.terminal_promt { display: flex; align-items: center; }
.terminal_promt span { margin-left: 4px; }
.terminal_user { color: #1eff8e; }
.terminal_location { color: #4878c0; }
.terminal_bling { color: #dddddd; }

.term-input {
  flex: 1;
  margin-left: 4px;
  background: transparent;
  border: none;
  outline: none;
  color: #d5d0ce;
  font-family: inherit;
  font-size: 12px;
}

.terminal_cursor {
  display: inline-block;
  height: 14px;
  width: 7px;
  background: #ffffff;
  animation: curbl 1200ms linear infinite;
}

@keyframes curbl {
  0% { background: #ffffff; }
  49% { background: #ffffff; }
  60% { background: transparent; }
  99% { background: transparent; }
  100% { background: #ffffff; }
}
</style>