<script setup>
// Emoji 无限滚动胶囊（改造自 Uiverse sliding emojis）
// - 固定右下角、涂鸦菜单上方
// - 悬停暂停滚动（原版注释掉的功能，这里启用）
// - 暗色模式毛玻璃适配；纯装饰（aria-hidden，不参与键盘焦点）
</script>

<template>
  <div class="emoji-strip" aria-hidden="true">
    <div class="cardm">
      <div class="emojis">
        <button tabindex="-1">😄</button>
        <button tabindex="-1">😁</button>
        <button tabindex="-1">😆</button>
        <button tabindex="-1">😂</button>
        <button tabindex="-1">🤣</button>
        <button tabindex="-1">🙂</button>
      </div>
      <div class="emojis">
        <button tabindex="-1">😄</button>
        <button tabindex="-1">😁</button>
        <button tabindex="-1">😆</button>
        <button tabindex="-1">😂</button>
        <button tabindex="-1">🤣</button>
        <button tabindex="-1">🙂</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 外层定位：右下角、涂鸦菜单上方 */
.emoji-strip {
  position: fixed;
  right: 20px; /* 回到右下角原位 */
  bottom: 24px;
  z-index: 60;
  pointer-events: auto;
}

.cardm {
  width: 220px;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  white-space: nowrap;
  overflow: hidden;
  border-radius: 50px;
  box-shadow:
    -10px 0 33px -7px rgba(0, 0, 0, 0.12),
    10px 0 33px -7px rgba(0, 0, 0, 0.12);
}

/* 悬停暂停（原版被注释的功能） */
.cardm:hover .emojis {
  animation-play-state: paused;
}

.emojis {
  display: inline-block;
  animation: emoji-sliding 6s infinite linear;
}

button {
  font-size: 44px;
  margin: 0 5px;
  padding: 0;
  line-height: 1;
  border: none;
  background-color: transparent;
  cursor: grab;
  vertical-align: middle;
}
button:hover {
  transform: scale(1.15);
  transition: transform 0.3s ease;
}

@keyframes emoji-sliding {
  from { transform: translateX(0); }
  to { transform: translateX(-101%); }
}

/* 暗色模式：深色毛玻璃 */
html.dark .cardm {
  background: rgba(40, 40, 46, 0.55);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow:
    -10px 0 33px -7px rgba(0, 0, 0, 0.35),
    10px 0 33px -7px rgba(0, 0, 0, 0.35);
}

/* 窄屏隐藏 */
@media (max-width: 768px) {
  .emoji-strip { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .emojis { animation: none; }
}
</style>