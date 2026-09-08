<script setup lang="ts">
import { computed, ref } from 'vue'

import HomeTab from '@/views/mobile/HomeTab.vue'
import ManageTab from '@/views/mobile/ManageTab.vue'
import StatsTab from '@/views/mobile/StatsTab.vue'
import MineTab from '@/views/mobile/MineTab.vue'
import Welcome from '@/views/Welcome.vue'

const TABS = [
  { key: 'home', label: '首页', icon: '🏠', component: HomeTab },
  { key: 'manage', label: '管理', icon: '🛠️', component: ManageTab },
  { key: 'stats', label: '账单', icon: '📊', component: StatsTab },
  { key: 'mine', label: '我的', icon: '👤', component: MineTab },
]

const activeTab = ref('home')
const showWelcome = ref(true)

const welcomed = ref(false)

function switchTab(key: string) {
  activeTab.value = key
}

const currentComponent = computed(() => TABS.find((t) => t.key === activeTab.value)?.component || HomeTab)

// 欢迎页展示 2 秒后进入主界面
setTimeout(() => {
  showWelcome.value = false
  welcomed.value = true
}, 2200)
</script>

<template>
  <!-- 欢迎页(冷启动展示) -->
  <Welcome v-if="showWelcome" />

  <div v-else class="app-root">
    <!-- 顶部导航 -->
    <header class="app-header">
      <span class="app-title">Arya手作 · 管理</span>
    </header>

    <!-- 当前 Tab 内容 -->
    <main class="app-main">
      <component :is="currentComponent" />
    </main>

    <!-- 底部 TabBar:四个等宽 -->
    <nav class="app-tabbar">
      <div
        v-for="t in TABS"
        :key="t.key"
        class="tab-item"
        :class="{ active: activeTab === t.key }"
        @click="switchTab(t.key)"
      >
        <span class="tab-icon">{{ t.icon }}</span>
        <span class="tab-label">{{ t.label }}</span>
      </div>
    </nav>
  </div>
</template>

<style>
html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #faf6f0;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
* {
  box-sizing: border-box;
}
</style>

<style scoped>
.app-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.app-header {
  height: 44px;
  background: #faf6f0;
  border-bottom: 1px solid #f0ebe6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.app-title {
  font-size: 17px;
  font-weight: 600;
  color: #5a5350;
}
.app-main {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 60px; /* 给 tabbar 留出空间 */
}
.app-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 60px;
  background: #fff;
  border-top: 1px solid #f0ebe6;
  display: flex;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom);
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: #b9b1ac;
}
.tab-item.active {
  color: #a98b84;
}
.tab-item.active .tab-label {
  font-weight: 600;
}
.tab-icon {
  font-size: 22px;
  line-height: 1.2;
}
.tab-label {
  font-size: 12px;
  line-height: 1.3;
}
</style>