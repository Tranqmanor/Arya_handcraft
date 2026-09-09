<template>
  <div class="tab-page">
    <!-- 内页路由 -->
    <OrdersPage v-if="store.page === 'orders'" @back="store.page = 'tabs'" />
    <ArticlesOnline v-else-if="store.page === 'articles'" @back="store.page = 'tabs'" />
    <VideosOnline v-else-if="store.page === 'videos'" @back="store.page = 'tabs'" />
    <CarouselOnline v-else-if="store.page === 'carousel'" @back="store.page = 'tabs'" />
    <CouponsOnline v-else-if="store.page === 'coupons'" @back="store.page = 'tabs'" />

    <!-- 管理菜单 -->
    <template v-else>
      <div class="page-title">🛠️ 管理</div>
      <div class="menu-list">
        <div class="menu-item" @click="store.page = 'orders'">
          <span class="menu-icon">📦</span><span class="menu-label">订单信息<em class="tag-local">本地</em></span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="openOnline('articles')">
          <span class="menu-icon">📝</span><span class="menu-label">文章管理<em class="tag-online">在线</em></span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="openOnline('carousel')">
          <span class="menu-icon">🖼️</span><span class="menu-label">轮播图管理<em class="tag-online">在线</em></span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="openOnline('videos')">
          <span class="menu-icon">🎬</span><span class="menu-label">视频管理<em class="tag-online">在线</em></span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="openOnline('coupons')">
          <span class="menu-icon">🎟️</span><span class="menu-label">优惠券管理<em class="tag-online">在线</em></span><span class="arrow">›</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'

import OrdersPage from '@/views/mobile/OrdersPage.vue'
import ArticlesOnline from '@/views/mobile/online/ArticlesOnline.vue'
import VideosOnline from '@/views/mobile/online/VideosOnline.vue'
import CarouselOnline from '@/views/mobile/online/CarouselOnline.vue'
import CouponsOnline from '@/views/mobile/online/CouponsOnline.vue'
import { useAppStore, type AppPage } from '@/stores/app'

const store = useAppStore()

/** 在线模块:需先「我的」登录获取 token */
function openOnline(page: AppPage) {
  if (!localStorage.getItem('admin_token')) {
    ElMessage.warning('请先在「我的」页登录(与后台账号密码一致)后使用在线功能')
    return
  }
  store.page = page
}
</script>

<style scoped>
.tab-page {
  padding: 16px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 12px;
}
.menu-list {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-bottom: 1px solid #f5f0eb;
  cursor: pointer;
}
.menu-item:last-child {
  border-bottom: none;
}
.menu-icon {
  font-size: 20px;
}
.menu-label {
  flex: 1;
  color: #5a5350;
  font-size: 15px;
  font-weight: 500;
}
.tag-local,
.tag-online {
  font-style: normal;
  font-size: 10px;
  margin-left: 6px;
  padding: 1px 6px;
  border-radius: 999px;
}
.tag-local {
  background: #f0e8e4;
  color: #a98b84;
}
.tag-online {
  background: #e8f0f1;
  color: #6d8f96;
}
.arrow {
  color: #d9cfc9;
  font-size: 20px;
}
</style>

<style scoped>
.tab-page {
  padding: 16px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 12px;
}
.menu-list {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-bottom: 1px solid #f5f0eb;
  cursor: pointer;
}
.menu-item:last-child {
  border-bottom: none;
}
.menu-icon {
  font-size: 20px;
}
.menu-label {
  flex: 1;
  color: #5a5350;
  font-size: 15px;
  font-weight: 500;
}
.arrow {
  color: #d9cfc9;
  font-size: 20px;
}
</style>