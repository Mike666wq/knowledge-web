<script setup>
// 浏览器窗口 mockup（改造自 Uiverse browser card）
// 放在首页「关注 & 链接」：银行卡 + 手机 + 浏览器 组成个人生态三件套
// 地址栏显示 ~/bbben；深色模式自适应
</script>

<template>
  <div class="card" aria-hidden="true">
    <div class="chrome">
      <div class="circles">
        <div class="c"></div>
        <div class="c"></div>
        <div class="c"></div>
      </div>

      <div class="browser">
        <div class="chevrons">
          <svg viewBox="0 0 20 20" height="14" width="14" xmlns="http://www.w3.org/2000/svg">
            <path transform="translate(6.25 3.75)" d="M0,6.25,6.25,0l.875.875L1.75,6.25l5.375,5.375L6.25,12.5Z" fill="currentColor"></path>
          </svg>
          <svg viewBox="0 0 20 20" height="14" width="14" xmlns="http://www.w3.org/2000/svg">
            <path transform="translate(6.625 3.75)" d="M7.125,6.25.875,12.5,0,11.625,5.375,6.25,0,.875.875,0Z" fill="currentColor"></path>
          </svg>
        </div>
        <div class="search-bar">
          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="9" viewBox="0 0 16.89 16.887">
            <path d="M16.006,16.887h0l-4.743-4.718a6.875,6.875,0,1,1,.906-.906l4.719,4.744-.88.88ZM6.887,1.262a5.625,5.625,0,1,0,5.625,5.625A5.631,5.631,0,0,0,6.887,1.262Z" transform="translate(0.003 0)"></path>
          </svg>
          ~/bbben
        </div>
      </div>
    </div>

    <!-- 窗口屏幕区 -->
    <div class="screen">
      <div class="tab-hint">…</div>
    </div>
  </div>
</template>

<style scoped>
.card {
  width: 300px;
  border-radius: 10px;
  overflow: hidden;
  background: #f1f3f6;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  pointer-events: none;
}

/* ---- 顶部工具条 ---- */
.chrome {
  display: flex;
  align-items: center;
  height: 34px;
  padding: 0 10px;
  background: #e6e9ef;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.circles {
  display: flex;
  align-items: center;
  gap: 7px;
  width: 20%;
}

.c {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  box-shadow: inset 2px 2px 5px rgba(235, 235, 235, 0.356);
}
.c:first-child { background-color: #ff5f57; }
.c:nth-child(2) { background-color: #febc2e; }
.c:last-child { background-color: #28c840; }

.browser {
  width: 80%;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chevrons {
  display: flex;
  gap: 2px;
  color: #5a6072;
}

.search-bar {
  position: relative;
  border: 0.5px solid rgba(0, 0, 0, 0.55);
  border-radius: 5px;
  padding: 4px 8px 4px 22px;
  width: 100%;
  height: 22px;
  display: flex;
  align-items: center;
  font-size: 10px;
  font-family: 'Courier New', monospace;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #585858;
  background: #fff;
  box-shadow: inset 2px 2px 2px rgba(5, 5, 5, 0.15);
}

.search-bar svg {
  position: absolute;
  left: 7px;
  fill: #8a8f9c;
}

/* ---- 屏幕区 ---- */
.screen {
  height: 150px;
  background:
    radial-gradient(80% 60% at 70% 20%, rgba(59, 130, 246, 0.12), transparent 70%),
    linear-gradient(180deg, #eef2f8 0%, #f8fafc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-hint {
  font-family: 'Courier New', monospace;
  font-size: 28px;
  color: rgba(70, 80, 100, 0.18);
  font-weight: 700;
  letter-spacing: 0.2em;
}

/* ---- 深色模式 ---- */
.dark .card {
  background: #26262b;
  border-color: rgba(255, 255, 255, 0.08);
}
.dark .chrome {
  background: #1d1d21;
  border-bottom-color: rgba(255, 255, 255, 0.07);
}
.dark .chevrons { color: #9aa3b5; }
.dark .search-bar {
  background: #17171c;
  border-color: rgba(255, 255, 255, 0.25);
  color: #b9c0cf;
}
.dark .search-bar svg { fill: #7d8496; }
.dark .screen {
  background:
    radial-gradient(80% 60% at 70% 20%, rgba(59, 130, 246, 0.14), transparent 70%),
    linear-gradient(180deg, #202229 0%, #17181d 100%);
}
.dark .tab-hint { color: rgba(180, 195, 220, 0.16); }
</style>
