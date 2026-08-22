<template>
  <view class="container">
    <!-- 欢迎界面 -->
    <view v-if="showWelcome" class="welcome">
      <view class="paw-wrap">
        <image class="paw" src="/static/logo.png" mode="aspectFit" />
      </view>
      <view class="brand">
        <text class="name">Arya_handcraft</text>
        <text class="sub">手作毛毡猫咪</text>
      </view>
      <view class="loading-dots">
        <view class="dot" />
        <view class="dot" />
        <view class="dot" />
      </view>
    </view>

    <!-- 竖图轮播(卡片式:四周留边、四角圆角、图下展示标题与描述) -->
    <view v-else class="carousel-container">
      <swiper :vertical="true" :circular="false" :indicator-dots="carouselImages.length > 1"
        indicator-color="rgba(255,255,255,0.5)" indicator-active-color="#fff" :interval="3000" :duration="500"
        class="full-swiper" @change="onSwiperChange">
        <swiper-item v-for="item in carouselImages" :key="item.id">
          <view class="slide" @tap="handleImageTap">
            <image :src="item.image_url" class="carousel-image" mode="aspectFill" />
            <view v-if="item.title || item.description" class="slide-overlay">
              <text class="slide-title">{{ item.title }}</text>
              <text v-if="item.description" class="slide-desc">{{ item.description }}</text>
            </view>
          </view>
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

<script setup
  lang="ts">
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

<style scoped
  lang="scss">
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

    /* 轮播图容器:四周留边,露出品牌渐变底色 */
    .carousel-container {
      width: 100%;
      height: 100vh;
      box-sizing: border-box;
      padding: 24rpx;
      background: linear-gradient(180deg, #faf6f0 0%, #eadcd9 100%);
    }

    /* 全屏轮播 */
    .full-swiper {
      width: 100%;
      height: 100%;
    }

    /* 单张轮播卡片:四角圆角 + 轻阴影 */
    .slide {
      position: relative;
      width: 100%;
      height: 100%;
      overflow: hidden;
      border-radius: 28rpx;
      background: #fff;
      box-shadow: 0 8rpx 24rpx rgba(90, 83, 80, 0.12);
    }

    /* 轮播图图片:铺满整张圆角卡片 */
    .carousel-image {
      display: block;
      width: 100%;
      height: 100%;
    }

    /* 文字叠加层:压在图片底部,渐变暗化保证可读性,靠左对齐 */
    .slide-overlay {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      padding: 72rpx 24rpx 28rpx;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.5) 100%);
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      text-align: left;
      pointer-events: none; /* 点击穿透到图片(预览大图) */
    }

    .slide-title {
      font-size: 30rpx;
      font-weight: 700;
      color: #fff;
      letter-spacing: 2rpx;
      text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.35);
    }

    .slide-desc {
      margin-top: 10rpx;
      font-size: 24rpx;
      line-height: 1.6;
      color: rgba(255, 255, 255, 0.88);
    }

    /* 空状态(卡片式圆角) */
    .empty-state {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 28rpx;
      background: #fff;
    }

    .empty-text {
      font-size: 28rpx;
      color: $arya-dove;
    }


  </style>