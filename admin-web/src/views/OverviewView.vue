<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getSummary } from '@/api/admin'

const stats = ref({ user_count: 0, video_count: 0, article_count: 0, total_views: 0, coupon_count: 0, unused_coupon_count: 0 })

onMounted(async () => {
  try {
    stats.value = await getSummary()
  } catch { /* ignore */ }
})
</script>

<template>
  <div>
    <h3>数据概览</h3>
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-num">{{ stats.user_count }}</div>
          <div class="stat-label">用户数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-num">{{ stats.video_count }}</div>
          <div class="stat-label">视频数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-num">{{ stats.article_count }}</div>
          <div class="stat-label">文章数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-num">{{ stats.total_views }}</div>
          <div class="stat-label">总浏览量</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-num">{{ stats.coupon_count }}</div>
          <div class="stat-label">优惠券总数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-num">{{ stats.unused_coupon_count }}</div>
          <div class="stat-label">未使用券</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.stat-cards { margin-top: 16px; }
.stat-cards .el-card { margin-bottom: 20px; text-align: center; }
.stat-num { font-size: 36px; font-weight: 700; color: #a98b84; }
.stat-label { font-size: 14px; color: #999; margin-top: 8px; }
</style>