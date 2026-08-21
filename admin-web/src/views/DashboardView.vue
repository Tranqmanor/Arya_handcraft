<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { getSummary } from '@/api/admin'

const router = useRouter()
const stats = ref({ user_count: 0, video_count: 0, article_count: 0, total_views: 0, coupon_count: 0, unused_coupon_count: 0 })

async function loadStats() {
  try {
    stats.value = await getSummary()
  } catch { /* ignore */ }
}

function handleLogout() {
  localStorage.removeItem('admin_token')
  router.push('/login')
}

onMounted(loadStats)
</script>

<template>
  <el-container class="dashboard">
    <el-aside width="200px" class="aside">
      <div class="logo">Arya_handcraft</div>
      <el-menu :default-active="$route.path" router>
        <el-menu-item index="/dashboard">概览</el-menu-item>
        <el-menu-item index="/dashboard/videos">视频管理</el-menu-item>
        <el-menu-item index="/dashboard/articles">文章管理</el-menu-item>
        <el-menu-item index="/dashboard/coupons">优惠券</el-menu-item>
        <el-menu-item index="/dashboard/carousel">轮播图管理</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>Arya_handcraft 管理后台</span>
        <el-button text @click="handleLogout">退出</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.dashboard { height: 100vh; }
.aside { background: #fff; border-right: 1px solid #f0ebe6; }
.logo { padding: 20px 16px; font-weight: 700; color: #a98b84; font-size: 18px; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #f0ebe6; }
</style>
