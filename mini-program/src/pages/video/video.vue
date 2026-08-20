<template>
  <view class="video-page">
    <!-- 加载中 -->
    <view v-if="loading" class="state-tip">加载中...</view>

    <!-- 空态 -->
    <view v-else-if="videos.length === 0" class="state-tip">
      <text>暂无视频,敬请期待~</text>
    </view>

    <!-- 视频列表 -->
    <view v-else class="video-list">
      <view
        v-for="v in videos"
        :key="v.id"
        class="video-card"
        :style="{ height: cardHeight }"
      >
        <!-- 封面/预览 -->
        <image
          v-if="!playingId || playingId !== v.id"
          class="cover"
          :src="v.cover_url || '/static/tab-video.png'"
          mode="aspectFill"
          @tap="playVideo(v)"
        />
        <!-- 播放器 -->
        <video
          v-else
          class="player"
          :src="v.video_url"
          :poster="v.cover_url"
          controls
          :autoplay="true"
          object-fit="fill"
          @ended="playingId = null"
          @error="playingId = null"
        />

        <!-- 信息遮罩 -->
        <view
          v-if="!playingId || playingId !== v.id"
          class="info"
          @tap="playVideo(v)"
        >
          <view class="title-row">
            <text class="title">{{ v.title }}</text>
          </view>
          <view class="meta-row">
            <text class="meta">▶ {{ v.view_count }} 浏览</text>
            <text class="meta">⏱ {{ formatDuration(v.duration) }}</text>
          </view>
        </view>
        <!-- 播放中时长角标 -->
        <view v-if="playingId === v.id" class="playing-tip">
          {{ formatDuration(v.duration) }}
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShareAppMessage, onShow } from '@dcloudio/uni-app'

import { getVideos, reportVideoView, type VideoItem } from '@/api/video'
import { getDeviceKey } from '@/utils/device'

const videos = ref<VideoItem[]>([])
const loading = ref(true)
const playingId = ref<number | null>(null)

// 竖屏卡片 9:16 高度(视口宽按 100vw)
const cardHeight = computed(() => `calc(100vw * 16 / 9 + 80rpx)`)

onShow(async () => {
  await loadVideos()
})

async function loadVideos() {
  loading.value = true
  try {
    videos.value = await getVideos()
  } catch {
    videos.value = []
  } finally {
    loading.value = false
  }
}

async function playVideo(v: VideoItem) {
  playingId.value = v.id
  // 上报浏览量(去重由后端保证)
  try {
    const res = await reportVideoView(v.id, getDeviceKey())
    if (res.viewed) {
      // 更新本地计数
      const target = videos.value.find((x) => x.id === v.id)
      if (target) target.view_count = res.view_count
    }
  } catch {
    // 浏览上报失败不阻塞播放
  }
}

function formatDuration(seconds: number) {
  const s = Math.max(0, Number(seconds) || 0)
  const m = Math.floor(s / 60)
  const rest = s % 60
  return `${String(m).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
}
// 分享
onShareAppMessage(() => ({
  title: 'Arya_handcraft 手作毛毡猫咪',
  path: '/pages/video/video',
}))
</script>



<style scoped lang="scss">
.video-page {
  min-height: 100vh;
  background: #faf6f0;
}
.state-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 40vh;
  color: #b9b1ac;
  font-size: 28rpx;
}
.video-list {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  padding: 24rpx 24rpx 60rpx;
}
.video-card {
  position: relative;
  width: 100%;
  border-radius: 24rpx;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 4px 16px rgba(90, 83, 80, 0.08);
}
.cover {
  width: 100%;
  height: 100%;
  display: block;
}
.player {
  width: 100%;
  height: 100%;
}
.info {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 24rpx;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.55) 100%);
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta-row {
  margin-top: 12rpx;
  display: flex;
  gap: 24rpx;
}
.meta {
  color: rgba(255, 255, 255, 0.9);
  font-size: 24rpx;
}
.playing-tip {
  position: absolute;
  right: 16rpx;
  top: 16rpx;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
}
</style>
