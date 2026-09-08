<template>
  <view class="referral-page">
    <view class="hero">
      <text class="hero-title">推荐好友 · 双方有礼</text>
      <text class="hero-sub">把独一无二的手作猫咪分享给朋友吧</text>
    </view>

    <view class="rules-card">
      <view class="rule-item">
        <text class="rule-num">1</text>
        <text class="rule-text">点击下方按钮,把小程序分享到微信聊天</text>
      </view>
      <view class="rule-item">
        <text class="rule-num">2</text>
        <text class="rule-text">朋友通过你的分享进入小程序并下单</text>
      </view>
      <view class="rule-item">
        <text class="rule-num">3</text>
        <text class="rule-text">朋友付清尾款(订单完成)后,你将自动获得一张 50 元优惠券</text>
      </view>
      <view class="rule-item">
        <text class="rule-num">4</text>
        <text class="rule-text">奖励不设上限;想兑换现金奖励请联系店主</text>
      </view>
    </view>

    <button class="share-btn" open-type="share">
      🧧 分享给微信好友
    </button>
    <view class="tip">分享出去的卡片会带上你的专属推荐标识</view>
  </view>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 分享携带推荐人 ID,新用户下单时自动归因
function onShareAppMessage() {
  const referrer = userStore.user?.id || 0
  return {
    title: 'Arya手作 · 一针一戳的手作毛毡猫咪',
    path: `/pages/index/index?referrer=${referrer}`,
  }
}

defineExpose({ onShareAppMessage })
</script>

<style scoped lang="scss">
.referral-page {
  min-height: 100vh;
  padding: 24rpx;
  background: #faf6f0;
}

.hero {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.hero-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2rpx;
}

.hero-sub {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.85);
}

.rules-card {
  margin-top: 24rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 26rpx;
}

.rule-item {
  display: flex;
  gap: 20rpx;
  align-items: flex-start;
}

.rule-num {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: #f0e8e4;
  color: #a98b84;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rule-text {
  font-size: 27rpx;
  color: #5a5350;
  line-height: 1.7;
}

.share-btn {
  margin-top: 48rpx;
  border-radius: 999rpx;
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  border: none;
  font-size: 32rpx;
  font-weight: 600;
}

.tip {
  margin-top: 16rpx;
  text-align: center;
  font-size: 22rpx;
  color: #b9b1ac;
}
</style>