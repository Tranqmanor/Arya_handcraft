<template>
  <view class="container">
    <!-- 欢迎界面 -->
    <view v-if="showWelcome" class="welcome">
      <view class="paw-wrap">
        <image class="paw" src="/static/logo-paw.png" mode="aspectFit" />
      </view>
      <view class="brand">
        <text class="name">Arya_handcraft</text>
        <text class="sub">手作毛毡猫咪 · 温暖相伴</text>
      </view>
      <view class="loading-dots">
        <view class="dot" />
        <view class="dot" />
        <view class="dot" />
      </view>
    </view>

    <!-- 全屏竖图轮播 -->
    <view v-else class="carousel-container">
      <swiper
        :vertical="true"
        :circular="false"
        :indicator-dots="carouselImages.length > 1"
        indicator-color="rgba(255,255,255,0.5)"
        indicator-active-color="#fff"
        :interval="3000"
        :duration="500"
        class="full-swiper"
        @change="onSwiperChange"
      >
        <swiper-item v-for="item in carouselImages" :key="item.id">
          <image
            :src="item.image_url"
            class="carousel-image"
            mode="aspectFill"
            @tap="handleImageTap"
          />
        </swiper-item>
        <!-- 空状态 -->
        <swiper-item v-if="carouselImages.length === 0">
          <view class="empty-state">
            <text class="empty-text">暂无轮播图</text>
          </view>
        </swiper-item>
      </swiper>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCarouselImages } from '@/api/carousel'
import type { CarouselImageItem } from '@/api/carousel'

const showWelcome = ref(true)
const carouselImages = ref<CarouselImageItem[]>([])
const currentIndex = ref(0)

let welcomeTimer: any = null

onMounted(async () => {
  // 加载轮播图数据
  try {
    carouselImages.value = await getCarouselImages()
  } catch (error) {
    console.error('加载轮播图失败:', error)
  }

  // 欢迎界面停留 2 秒后进入轮播
  welcomeTimer = setTimeout(() => {
    showWelcome.value = false
  }, 2000)
})

function onSwiperChange(e: any) {
  currentIndex.value = e.detail.current
}

function handleImageTap() {
  // 可在此扩展点击事件，例如全屏预览
  uni.previewImage({
    urls: carouselImages.value.map(img => img.image_url),
    current: carouselImages.value[currentIndex.value].image_url,
  })
}
</script>

<style scoped lang="scss">
.container {
  width: 100%;
  height: 100vh;
}

/* 欢迎界面 */
.welcome {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #faf6f0 0%, #eadcd9 100%);
  overflow: hidden;
}

/* 猫爪浮入 + 呼吸 */
.paw-wrap {
  animation: paw-in 0.9s ease-out both;
}
.paw {
  width: 180rpx;
  height: 180rpx;
  animation: breathe 2.4s ease-in-out infinite;
}
@keyframes paw-in {
  from {
    opacity: 0;
    transform: translateY(40rpx) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
@keyframes breathe {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.08);
  }
}

/* 品牌字渐显 */
.brand {
  margin-top: 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fade-up 0.8s 0.4s ease-out both;
}
.name {
  font-size: 56rpx;
  font-weight: 700;
  color: $arya-clay;
  letter-spacing: 4rpx;
}
.sub {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: $arya-dove;
  letter-spacing: 2rpx;
}

/* 加载点 */
.loading-dots {
  position: absolute;
  bottom: 12vh;
  display: flex;
  gap: 16rpx;
}
.dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: $arya-pink;
  animation: pulse 1.2s ease-in-out infinite;
}
.dot:nth-child(2) {
  animation-delay: 0.2s;
}
.dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 轮播图容器 */
.carousel-container {
  width: 100%;
  height: 100vh;
  background: #000;
}

/* 全屏轮播 */
.full-swiper {
  width: 100%;
  height: 100%;
}

/* 轮播图图片 */
.carousel-image {
  width: 100%;
  height: 100%;
}

/* 空状态 */
.empty-state {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #faf6f0 0%, #eadcd9 100%);
}
.empty-text {
  font-size: 28rpx;
  color: $arya-dove;
}
</style>