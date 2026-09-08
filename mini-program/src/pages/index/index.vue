<template>
  <view class="container">
    <!-- 欢迎界面 -->
    <view v-if="showWelcome" class="welcome">
      <view class="paw-wrap">
        <image class="paw" src="/static/logo.png" mode="aspectFit" />
      </view>
      <view class="brand">
        <text class="name">Arya手作</text>
        <text class="en-name">Arya Handcraft</text>
        <text class="sub">手作毛毡猫咪</text>
      </view>
      <view class="loading-dots">
        <view class="dot" />
        <view class="dot" />
        <view class="dot" />
      </view>
    </view>

    <!-- 主页 -->
    <view v-else class="home">
      <!-- ① 横图轮播 -->
      <swiper
        class="banner-swiper"
        :circular="carouselImages.length > 1"
        :autoplay="carouselImages.length > 1"
        :indicator-dots="carouselImages.length > 1"
        indicator-color="rgba(255,255,255,0.5)"
        indicator-active-color="#fff"
        :interval="3500"
        :duration="500"
      >
        <swiper-item v-for="item in carouselImages" :key="item.id" @click="previewCarousel(item.image_url)">
          <image :src="item.image_url" class="banner-image" mode="aspectFill" />
        </swiper-item>
      </swiper>

      <!-- ② 六宫格导航 -->
      <view class="nav-grid">
        <view class="nav-item" @click="go('/pages/video/video')">
          <view class="nav-icon" style="background: linear-gradient(160deg, #f6e8e6, #ecd6d3)"><text>🎬</text></view>
          <text class="nav-label">成品展示</text>
        </view>
        <view class="nav-item" @click="go('/pages/article/article?category=photo_guide')">
          <view class="nav-icon" style="background: linear-gradient(160deg, #e8f0f1, #d3e2e5)"><text>📷</text></view>
          <text class="nav-label">供图tips</text>
        </view>
        <view class="nav-item" @click="go('/pages/orders/orders')">
          <view class="nav-icon" style="background: linear-gradient(160deg, #fdf3e3, #f5e3c3)"><text>📦</text></view>
          <text class="nav-label">我的订单</text>
        </view>
        <view class="nav-item">
          <button class="nav-icon contact-icon" open-type="contact" style="background: linear-gradient(160deg, #e9f0e7, #d5e3d2)">
            <text>💬</text>
          </button>
          <text class="nav-label">官方客服</text>
        </view>
        <view class="nav-item" @click="go('/pages/article/article?category=about_wool')">
          <view class="nav-icon" style="background: linear-gradient(160deg, #f0eaf6, #ddd2ec)"><text>🧶</text></view>
          <text class="nav-label">关于羊毛毡</text>
        </view>
        <view class="nav-item" @click="go('/pages/article/article?category=about_arya')">
          <view class="nav-icon" style="background: linear-gradient(160deg, #fdeeea, #f6d9d2)"><text>🐱</text></view>
          <text class="nav-label">关于Arya</text>
        </view>
      </view>

      <!-- ③ 横版宣传图(后台可配置) -->
      <view class="promo" @click="previewPromo">
        <image v-if="promoImage" :src="promoImage" class="promo-image" mode="aspectFill" />
        <view v-else class="promo-placeholder">
          <text class="promo-title">Arya Handcraft</text>
          <text class="promo-sub">一针一戳 · 只为遇见你</text>
        </view>
      </view>

      <!-- ④ 成品套图瀑布流(按订单) -->
      <view v-if="works.length" class="works-section">
        <view class="section-head">
          <text class="section-title">成品欣赏</text>
          <text class="section-sub">每一只都是独一无二</text>
        </view>
        <view class="works-flow">
          <view class="works-col">
            <view v-for="w in worksLeft" :key="'L' + w.id" class="work-card" :style="{ height: w.height }" @click="previewWork(w.cover_image_url)">
              <image :src="w.cover_image_url" class="work-image" mode="aspectFill" />
              <view class="work-info">
                <text class="work-name">{{ w.cat_name }}</text>
              </view>
            </view>
          </view>
          <view class="works-col">
            <view v-for="w in worksRight" :key="'R' + w.id" class="work-card" :style="{ height: w.height }" @click="previewWork(w.cover_image_url)">
              <image :src="w.cover_image_url" class="work-image" mode="aspectFill" />
              <view class="work-info">
                <text class="work-name">{{ w.cat_name }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <app-tabbar current="home" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'

import { getCarouselImages, type CarouselImageItem } from '@/api/carousel'
import { getHomeSettings, getWorks, type WorkItem } from '@/api/order'
import AppTabbar from '@/components/app-tabbar.vue'
import { appState } from '@/utils/app-state'

// 欢迎页仅小程序冷启动后的首次进入展示;从其他页面返回首页不再出现
const showWelcome = ref(!appState.welcomed)
if (!appState.welcomed) {
  setTimeout(() => {
    showWelcome.value = false
    appState.welcomed = true
  }, 2000)
}

const carouselImages = ref<CarouselImageItem[]>([])
const promoImage = ref('')
const works = ref<(WorkItem & { id: number; height: string })[]>([])

onLoad((options) => {
  // 分享卡片进入时记录推荐人(下单时归因)
  const referrer = (options as { referrer?: string } | undefined)?.referrer
  if (referrer) uni.setStorageSync('referrer_id', Number(referrer))
})

onShow(() => {
  loadCarousel()
  loadWorks()
  loadPromo()
})

async function loadCarousel() {
  try {
    carouselImages.value = await getCarouselImages()
  } catch {
    carouselImages.value = []
  }
}

async function loadPromo() {
  try {
    const settings = await getHomeSettings()
    promoImage.value = settings.promo_image_url
  } catch {
    promoImage.value = ''
  }
}

async function loadWorks() {
  try {
    const list = await getWorks()
    // 暂无已完成作品订单时,用占位图展示瀑布流效果;后台筛图设封面后自动替换为真实照片
    if (list.length === 0) {
      const placeholders = ['雪球', '煤球', '团子', '花卷', '布丁', '年糕']
      list.push(
        ...placeholders.map((name, i) => ({
          cat_name: name,
          cover_image_url: `https://picsum.photos/seed/arya-cat-${i + 1}/400/${340 + i * 60}`,
          completed_at: null,
        })),
      )
    }
    // 基于 id+名字长度的稳定伪随机高度:刷新不跳动,呈现"随机大小分布"
    const heights = ['440rpx', '540rpx', '360rpx']
    works.value = list.map((w, idx) => ({
      ...w,
      id: idx,
      height: heights[(w.cat_name.length + idx) % 3],
    }))
  } catch {
    works.value = []
  }
}

const worksLeft = computed(() => works.value.filter((_, i) => i % 2 === 0))
const worksRight = computed(() => works.value.filter((_, i) => i % 2 === 1))

function go(url: string) {
  uni.navigateTo({ url })
}

function previewCarousel(url: string) {
  uni.previewImage({ urls: carouselImages.value.map((c) => c.image_url), current: url })
}

function previewPromo() {
  if (promoImage.value) uni.previewImage({ urls: [promoImage.value] })
}

function previewWork(url: string) {
  uni.previewImage({ urls: [url] })
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

    /* 英文品牌小字 */
    .en-name {
      margin-top: 12rpx;
      font-size: 24rpx;
      color: $arya-dove;
      letter-spacing: 6rpx;
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

    /* 主页容器 */
    .home {
      padding: 24rpx 24rpx 0;
      padding-bottom: 240rpx; /* tabbar 基础预留 */
    }

    /* ① 横图轮播 */
    .banner-swiper {
      width: 100%;
      height: 380rpx;
      border-radius: 24rpx;
      overflow: hidden;
      box-shadow: 0 8rpx 24rpx rgba(90, 83, 80, 0.12);
    }

    .banner-image {
      width: 100%;
      height: 100%;
      display: block;
    }

    /* ② 六宫格导航 */
    .nav-grid {
      margin-top: 32rpx;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 28rpx 12rpx;
      background: #fff;
      border-radius: 24rpx;
      padding: 32rpx 16rpx;
      box-shadow: 0 4rpx 16rpx rgba(90, 83, 80, 0.06);
    }

    .nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12rpx;
    }

    .nav-icon {
      width: 96rpx;
      height: 96rpx;
      border-radius: 28rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      border: none;
      line-height: 1;
      padding: 0;
      margin: 0;
    }

    .nav-icon::after {
      border: none;
    }

    .nav-icon text {
      font-size: 44rpx;
    }

    .nav-label {
      font-size: 24rpx;
      color: #5a5350;
    }

    /* ③ 横版宣传图 */
    .promo {
      margin-top: 32rpx;
      border-radius: 24rpx;
      overflow: hidden;
      box-shadow: 0 4rpx 16rpx rgba(90, 83, 80, 0.06);
    }

    .promo-image {
      width: 100%;
      height: 240rpx;
      display: block;
    }

    .promo-placeholder {
      height: 240rpx;
      background: linear-gradient(135deg, #eadcd9 0%, #d9c7a5 60%, #c9a9a6 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12rpx;
    }

    .promo-title {
      font-size: 40rpx;
      font-weight: 700;
      color: #fff;
      letter-spacing: 4rpx;
    }

    .promo-sub {
      font-size: 24rpx;
      color: rgba(255, 255, 255, 0.85);
      letter-spacing: 6rpx;
    }

    /* ④ 作品瀑布流 */
    .works-section {
      margin-top: 40rpx;
    }

    .section-head {
      display: flex;
      align-items: baseline;
      gap: 16rpx;
      margin-bottom: 24rpx;
      padding: 0 4rpx;
    }

    .section-title {
      font-size: 34rpx;
      font-weight: 700;
      color: $arya-ink;
    }

    .section-sub {
      font-size: 22rpx;
      color: $arya-dove;
    }

    .works-flow {
      display: flex;
      gap: 20rpx;
    }

    .works-col {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20rpx;
    }

    .work-card {
      border-radius: 20rpx;
      overflow: hidden;
      background: #fff;
      box-shadow: 0 4rpx 16rpx rgba(90, 83, 80, 0.08);
      position: relative;
    }

    .work-image {
      width: 100%;
      height: 100%;
      display: block;
    }

    .work-info {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      padding: 40rpx 20rpx 16rpx;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.45) 100%);
      display: flex;
      justify-content: flex-start;
    }

    .work-name {
      font-size: 26rpx;
      color: #fff;
      font-weight: 600;
      text-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.3);
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