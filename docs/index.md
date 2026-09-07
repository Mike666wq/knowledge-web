---
layout: doc
sidebar: true
aside: false
---

<script setup>
import { useData } from 'vitepress'
import { computed } from 'vue'

const { theme } = useData()
const tree = computed(() => theme.value?.customNotesTree || [])
</script>

# ~/bbben

这里汇总了所有笔记。点击任意卡片即可进入阅读，或使用顶栏搜索 (`Ctrl+K`)。

## 分类展示

<ClientOnly>
  <div class="drop-accent">
    <WaterDrop :size="72" hue="#a3d8ff" />
  </div>
</ClientOnly>

<ClientLoader>
  <template #placeholder>
    <div style="min-height: 700px">
      <PlaneLoader :scale="0.55" />
    </div>
  </template>
  <RotatingCards :tree="tree" />
</ClientLoader>

## 全部笔记

<ClientLoader>
  <template #placeholder>
    <div style="min-height: 280px">
      <PlaneLoader :scale="0.55" />
    </div>
  </template>
  <NotesTree :tree="tree" />
</ClientLoader>

## 探索本站

<ClientOnly>
  <div class="explore-stage">
    <Stacked3DCard />
  </div>
</ClientOnly>

<style>
.explore-stage {
  display: flex;
  justify-content: center;
  padding: 3rem 0 2rem;
  perspective: 1200px;
}
</style>

## 关注 & 链接

<ClientOnly>
  <div class="link-zone">
    <MemberCard />
    <PhoneMock wallpaper="/wallpaper.png" cover="/cover.png" />
    <BrowserMockup />
    <GlassCards />
  </div>
</ClientOnly>

<style>
.link-zone {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2.5rem;
  padding: 0.5rem 0;
}
</style>

## 外观设置

<ClientOnly>
  <div class="theme-row">
    <Panda2 />
    <ThemeModeCard />
    <Panda />
  </div>
</ClientOnly>

<style>
.theme-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 3rem;
  padding: 0.5rem 0;
}
</style>

## 使用说明

<ClientOnly>
  <FlipBook cover="使用说明">
    <ul>
      <li>点击分类标题折叠 / 展开卡片</li>
      <li>点击卡片进入对应笔记</li>
      <li>Ctrl + K 全文搜索</li>
      <li>「外观设置」或右上角开关切换明暗</li>
    </ul>
  </FlipBook>
</ClientOnly>

<style>
.drop-accent {
  display: inline-block;
  margin: -8px 0 4px 14px;
  vertical-align: middle;
  transform: translateY(-6px) rotate(-8deg);
  filter: drop-shadow(0 6px 10px rgba(99, 150, 200, 0.3));
  transition: transform 0.3s;
}
.drop-accent:hover {
  transform: translateY(-10px) rotate(8deg) scale(1.1);
}
</style>
