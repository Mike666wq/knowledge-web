<script setup>
// 带占位的 ClientOnly：SSR 输出 placeholder，客户端挂载后切换为默认插槽
// （VitePress 1.6.4 自带的 ClientOnly 不支持 #placeholder，SSR 输出为空）
import { ref, onMounted } from 'vue'

const mounted = ref(false)
onMounted(() => { mounted.value = true })
</script>

<template>
  <slot v-if="mounted" />
  <slot v-else name="placeholder" />
</template>
