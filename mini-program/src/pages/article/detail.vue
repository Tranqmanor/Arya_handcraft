<template>
  <view class="detail-page">
    <view v-if="loading" class="state-tip">加载中...</view>
    <view v-else-if="article" class="detail">
      <text class="title">{{ article.title }}</text>
      <text class="meta">
        {{ categoryText(article.category) }} · {{ article.view_count }} 阅读
      </text>
      <rich-text class="content" :nodes="htmlContent" />
      <button class="contact-btn" @click="contactVisible = true">联系店主 · 定制咨询</button>
      <contact-modal :visible="contactVisible" @close="contactVisible = false" />
    </view>
    <view v-else class="state-tip">文章不存在</view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

import { getArticle, reportArticleView, type ArticleDetail } from '@/api/article'
import { renderMarkdown } from '@/utils/markdown'
import ContactModal from '@/components/contact-modal.vue'

const article = ref<ArticleDetail | null>(null)
const loading = ref(true)
const contactVisible = ref(false)

onLoad(async (options) => {
  const id = Number(options?.id || 0)
  if (!id) {
    loading.value = false
    return
  }
  try {
    article.value = await getArticle(id)
    reportArticleView(id).catch(() => {})
  } catch {
    article.value = null
  } finally {
    loading.value = false
  }
})

const htmlContent = computed(() =>
  article.value ? renderMarkdown(article.value.content) : '',
)

function categoryText(category: string) {
  const map: Record<string, string> = { photo_guide: '定制指南', general: '文章' }
  return map[category] || '文章'
}
</script>

<style scoped lang="scss">
.detail-page {
  min-height: 100vh;
  background: #fff;
  padding: 32rpx;
}
.state-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 40vh;
  color: #b9b1ac;
  font-size: 28rpx;
}
.detail {
  display: flex;
  flex-direction: column;
}
.title {
  font-size: 40rpx;
  font-weight: 700;
  color: #5a5350;
  line-height: 1.4;
}
.meta {
  margin: 16rpx 0 32rpx;
  font-size: 24rpx;
  color: #b9b1ac;
}
.content {
  font-size: 30rpx;
  color: #5a5350;
  line-height: 1.8;
  word-break: break-word;
}

.contact-btn {
  margin-top: 48rpx;
  border-radius: 999rpx;
  background: #c9a9a6;
  color: #fff;
  border: none;
  font-size: 30rpx;
  font-weight: 500;
}
</style>

