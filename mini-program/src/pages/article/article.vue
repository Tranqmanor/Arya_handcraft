<template>
  <view class="article-page">
    <view v-if="loading" class="state-tip">加载中...</view>
    <view v-else-if="articles.length === 0" class="state-tip">暂无文章</view>

    <view v-else class="article-list">
      <view v-for="a in articles" :key="a.id" class="article-card" @click="openArticle(a.id)">
        <image v-if="a.cover_url" class="cover" :src="a.cover_url" mode="aspectFill" />
        <view class="info">
          <text class="tag">{{ categoryText(a.category) }}</text>
          <text class="title">{{ a.title }}</text>
          <text class="summary">{{ a.summary }}</text>
          <view class="meta">
            <text>{{ a.view_count }} 阅读</text>
            <text>{{ formatDate(a.created_at) }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import { getArticles, type ArticleListItem } from '@/api/article'

const articles = ref<ArticleListItem[]>([])
const loading = ref(true)

onShow(async () => {
  await loadArticles()
})

async function loadArticles() {
  loading.value = true
  try {
    articles.value = await getArticles()
  } catch {
    articles.value = []
  } finally {
    loading.value = false
  }
}

function openArticle(id: number) {
  uni.navigateTo({ url: `/pages/article/detail?id=${id}` })
}

function categoryText(category: string) {
  const map: Record<string, string> = { photo_guide: '定制指南', general: '文章' }
  return map[category] || '文章'
}

function formatDate(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
</script>

<style scoped lang="scss">
.article-page {
  min-height: 100vh;
  padding: 24rpx;
  background: #faf6f0;
}
.state-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 40vh;
  color: #b9b1ac;
  font-size: 28rpx;
}
.article-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.article-card {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(90, 83, 80, 0.06);
}
.cover {
  width: 100%;
  height: 320rpx;
  display: block;
  background: #f0ebe6;
}
.info {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.tag {
  align-self: flex-start;
  font-size: 22rpx;
  color: #fff;
  background: #9fb0b5;
  border-radius: 999rpx;
  padding: 4rpx 16rpx;
}
.title {
  font-size: 32rpx;
  font-weight: 600;
  color: #5a5350;
}
.summary {
  font-size: 26rpx;
  color: #b9b1ac;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.meta {
  margin-top: 8rpx;
  display: flex;
  gap: 24rpx;
  font-size: 22rpx;
  color: #b9b1ac;
}
</style>

