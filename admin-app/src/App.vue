<script setup lang="ts">
import { computed, ref } from 'vue'

import HomeTab from '@/views/mobile/HomeTab.vue'
import ManageTab from '@/views/mobile/ManageTab.vue'
import StatsTab from '@/views/mobile/StatsTab.vue'
import MineTab from '@/views/mobile/MineTab.vue'
import Welcome from '@/views/Welcome.vue'
import LoginView from '@/views/LoginView.vue'
import { useAppStore } from '@/stores/app'

const store = useAppStore()

const BASE = import.meta.env.BASE_URL // './' ,适配安卓 WebView 相对加载
const TABS = [
  { key: 'home', label: '首页', icon: `${BASE}icons/home.png`, component: HomeTab },
  { key: 'manage', label: '管理', icon: `${BASE}icons/manage.png`, component: ManageTab },
  { key: 'stats', label: '账单', icon: `${BASE}icons/bill.png`, component: StatsTab },
  { key: 'mine', label: '我的', icon: `${BASE}icons/mine.png`, component: MineTab },
]

const showWelcome = ref(true)

function switchTab(key: string) {
  store.activeTab = key as typeof store.activeTab
  store.page = 'tabs'
}

const currentComponent = computed(
  () => TABS.find((t) => t.key === store.activeTab)?.component || HomeTab,
)

// 欢迎页展示 2 秒后进入主界面
setTimeout(() => {
  showWelcome.value = false
}, 2200)
</script>

<template>
  <!-- 欢迎页(冷启动展示) -->
  <Welcome v-if="showWelcome" />

  <!-- 全局登录门禁:未登录只能看到登录页,不可进入任何功能 -->
  <LoginView v-else-if="!store.loggedIn" />

  <div v-else class="app-root">
    <!-- 顶部导航 -->
    <header class="app-header">
      <img class="app-logo" :src="`${BASE}icons/logo.png`" alt="" />
      <span class="app-title">Arya手作 · 毛毡小店</span>
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
        :class="{ active: store.activeTab === t.key }"
        @click="switchTab(t.key)"
      >
        <img class="tab-icon-img" :src="t.icon" alt="" />
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
  gap: 8px;
  flex-shrink: 0;
}
.app-logo {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
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
.tab-icon-img {
  width: 24px;
  height: 24px;
  object-fit: contain;
  opacity: 0.55;
}

.tab-item.active .tab-icon-img {
  opacity: 1;
}

.tab-label {
  font-size: 12px;
  line-height: 1.3;
}
</style>