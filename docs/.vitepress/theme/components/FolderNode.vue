<script setup>
defineProps({
  open: { type: Boolean, default: false },   // 是否展开
  color: { type: String, default: '#f59e0b' }, // 主色（可跟随分类）
  name: { type: String, default: '' }          // 分类名
})
// 事件：点击文件夹
const emit = defineEmits(['toggle'])
</script>

<template>
  <div class="folder-node" :class="{ open }" @click.stop="emit('toggle')">
    <div class="file" :style="{ '--folder-color': color }">
      <!-- 后层页（work-5 到 work-1）hover 时展开 -->
      <div class="work like-work-5"></div>
      <div class="work like-work-4"></div>
      <div class="work like-work-3"></div>
      <div class="work like-work-2"></div>
      <div class="work like-work-1"><span class="folder-label">{{ name }}</span></div>
    </div>
  </div>
</template>

<style scoped>
.folder-node {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 52px;
  flex-shrink: 0;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.file {
  position: relative;
  width: 58px;
  height: 42px;
  cursor: pointer;
  transform-origin: bottom;
  perspective: 1200px;
  transition: transform 0.3s ease;
}

/* 每层页通用 */
.work {
  position: absolute;
  border-radius: 10px;
  transform-origin: bottom;
  transition: all 0.4s ease;
}

/* 最前面页（work-1，含内容） */
.like-work-1 {
  bottom: 0;
  width: 100%;
  height: 34px;
  background: linear-gradient(to top, color-mix(in srgb, var(--folder-color) 90%, black), var(--folder-color));
  border-radius: 10px;
  border-top-right-radius: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 4px;
}
.like-work-1::after {
  content: '';
  position: absolute;
  bottom: 99%;
  right: 0;
  width: 82%;
  height: 3px;
  background: var(--folder-color);
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}
.like-work-1::before {
  content: '';
  position: absolute;
  top: -3px;
  right: 44px;
  width: 4px;
  height: 4px;
  background: var(--folder-color);
  clip-path: polygon(100% 14%, 50% 100%, 100% 100%);
}

/* 后层页 */
.like-work-2 { inset: 3px; background: #e4e4e7; border-radius: 10px; transform-origin: bottom; }
.like-work-3 { inset: 3px; background: #d4d4d8; border-radius: 10px; transform-origin: bottom; }
.like-work-4 { inset: 3px; background: #c0c0c4; border-radius: 10px; transform-origin: bottom; }
.like-work-5 { inset: 3px; background: #a8a29e; border-radius: 10px; transform-origin: top; }
/* 最上面的夹子 */
.like-work-5::after {
  content: '';
  position: absolute;
  bottom: 99%;
  left: 0;
  width: 40%;
  height: 3px;
  background: color-mix(in srgb, var(--folder-color) 80%, black);
  border-top-left-radius: 6px;
}

/* Hover 时：层页旋转展开 + 整体上浮 */
.folder-node:hover .file {
  transform: translateY(-2px);
}
.folder-node:hover .like-work-4 { transform: rotateX(-20deg); }
.folder-node:hover .like-work-3 { transform: rotateX(-32deg); }
.folder-node:hover .like-work-2 { transform: rotateX(-42deg); }
.folder-node:hover .like-work-1 { transform: rotateX(-52deg) translateY(1px); }
.folder-node:hover .like-work-1 {
  box-shadow: inset 0 14px 28px rgba(255,255,255,0.3), inset 0 -14px 28px rgba(0,0,0,0.18);
}
.folder-node:hover .like-work-5 { transform: rotateX(8deg); }

/* 展开状态（点开时）保持打开 + 明确强调 */
.folder-node.open .file {
  transform: translateY(-3px);
}
.folder-node.open .like-work-4 { transform: rotateX(-20deg); }
.folder-node.open .like-work-3 { transform: rotateX(-32deg); }
.folder-node.open .like-work-2 { transform: rotateX(-42deg); }
.folder-node.open .like-work-1 { transform: rotateX(-52deg) translateY(1px); }
.folder-node.open .like-work-1 {
  box-shadow: inset 0 14px 28px rgba(255,255,255,0.3), inset 0 -14px 28px rgba(0,0,0,0.18);
}
.folder-node.open .like-work-5 { transform: rotateX(8deg); }

/* 展开时文件夹加一圈色光（明显但不夸张） */
.folder-node.open .file {
  filter: drop-shadow(0 4px 12px color-mix(in srgb, var(--folder-color) 40%, transparent));
}

.folder-label {
  font-size: 0.6rem;
  font-weight: 700;
  color: rgba(255,255,255,0.95);
  letter-spacing: 0.02em;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
</style>