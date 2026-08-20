<template>
  <view class="welcome">
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
</template>
<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'

onLoad(() => {
  // 欢迎页停留 2 秒后进入视频页
  setTimeout(() => {
    uni.reLaunch({ url: '/pages/video/video' })
  }, 2000)
})
</script>
<style scoped lang="scss">
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
</style>