<template>
  <view class="tabbar">
    <view class="tabbar-inner">
      <!-- 首页 -->
      <view class="tab-item" :class="{ active: current === 'home' }" @click="go('/pages/index/index')">
        <image class="tab-icon-img" src="/static/home.png" mode="aspectFit" :class="{ dim: current !== 'home' }" />
        <text class="tab-label">首页</text>
      </view>

      <!-- 立即下单(中央凸起,图片图标) -->
      <view class="tab-item center" @click="go('/pages/order-create/order-create')">
        <view class="cta-btn">
          <image class="cta-icon-img" src="/static/shop.png" mode="aspectFit" />
          <text class="cta-label">立即下单</text>
        </view>
      </view>

      <!-- 我的 -->
      <view class="tab-item" :class="{ active: current === 'mine' }" @click="go('/pages/mine/mine')">
        <image class="tab-icon-img" src="/static/mine.png" mode="aspectFit" :class="{ dim: current !== 'mine' }" />
        <text class="tab-label">我的</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
defineProps<{ current: 'home' | 'create' | 'mine' }>()

function go(url: string) {
  // tab 级切换用 redirectTo,避免页面栈膨胀
  uni.redirectTo({ url })
}
</script>

<style scoped lang="scss">
.tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  background: #fff;
  box-shadow: 0 -4rpx 24rpx rgba(90, 83, 80, 0.08);
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

.tabbar-inner {
  display: flex;
  align-items: flex-end;
  height: 110rpx;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rpx;
  padding-bottom: 10rpx;

  &.center {
    flex: 2; /* 1:2:1 宽度比 */
  }
}

.tab-icon-img {
  width: 48rpx;
  height: 48rpx;

  /* 未选中态淡化,选中态全显(图片本身含品牌色,用透明度区分状态) */
  &.dim {
    opacity: 0.5;
  }
}

.tab-label {
  font-size: 22rpx;
  color: #b9b1ac;
}

.tab-item.active .tab-label {
  color: #a98b84;
  font-weight: 600;
}

/* 中央凸起按钮 */
.cta-btn {
  width: 140rpx;
  height: 140rpx;
  margin-top: -56rpx;
  border-radius: 50%;
  background: linear-gradient(160deg, #c9a9a6 0%, #a98b84 100%);
  box-shadow: 0 10rpx 24rpx rgba(169, 139, 132, 0.45);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rpx;
  border: 6rpx solid #faf6f0;
  box-sizing: border-box;
}

.cta-icon-img {
  width: 52rpx;
  height: 52rpx;
}

.cta-label {
  font-size: 24rpx;
  color: #fff;
  font-weight: 700;
  letter-spacing: 2rpx;
}
</style>