<script setup>
defineProps({
  lang: { type: String, default: '' },  // 语言标签（HTML / Bash / Text / etc.）
  code: { type: String, default: '' }   // 可选：作为属性传入的代码（备用）
})
</script>

<template>
  <div class="mac-code">
    <div class="tools">
      <div class="circle"><span class="red box"></span></div>
      <div class="circle"><span class="yellow box"></span></div>
      <div class="circle"><span class="green box"></span></div>
      <span v-if="lang" class="lang">{{ lang }}</span>
    </div>
    <div class="content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.mac-code {
  margin: 1.5rem 0;
  border-radius: 10px;
  overflow: hidden;
  background: linear-gradient(180deg, #1c1c1e 0%, #0a0a0c 100%);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.tools {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  background: #2c2c2e;
  border-bottom: 0.5px solid rgba(255, 255, 255, 0.05);
  gap: 8px;
  position: relative;
}

.circle { padding: 0 4px; }
.box {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.red { background-color: #ff5f57; }
.yellow { background-color: #febc2e; }
.green { background-color: #28c840; }

.lang {
  position: absolute;
  right: 14px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
  font-family: -apple-system, "SF Pro", sans-serif;
  letter-spacing: 0.02em;
}

.content {
  padding: 1rem 1.25rem;
  color: #d4d4d8;
  font-family: var(--vp-font-family-mono);
  font-size: 0.85rem;
  line-height: 1.7;
  overflow-x: auto;
}

.content :deep(pre) {
  margin: 0;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  color: #d4d4d8 !important;
  font-family: var(--vp-font-family-mono) !important;
}

/* 行号浅灰 */
.content :deep(.line) {
  display: block;
  padding-left: 0;
}
.content :deep(.line)::before {
  display: none;
}
</style>