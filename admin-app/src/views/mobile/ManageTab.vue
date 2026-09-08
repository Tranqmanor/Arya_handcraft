<template>
  <div class="tab-page">
    <!-- 订单管理内页 -->
    <OrdersPage v-if="page === 'orders'" @back="page = 'tabs'" />

    <!-- 管理菜单 -->
    <template v-else>
      <div class="page-title">🛠️ 管理</div>
      <div class="menu-list">
        <div class="menu-item" @click="page = 'orders'">
          <span class="menu-icon">📦</span><span class="menu-label">订单信息</span><span class="arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">📝</span><span class="menu-label">文章管理</span><span class="arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">🖼️</span><span class="menu-label">图片管理</span><span class="arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">🎬</span><span class="menu-label">视频管理</span><span class="arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">🎟️</span><span class="menu-label">优惠券管理</span><span class="arrow">›</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import OrdersPage from '@/views/mobile/OrdersPage.vue'

const page = ref<'tabs' | 'orders'>('tabs')
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
.arrow {
  color: #d9cfc9;
  font-size: 20px;
}
</style>