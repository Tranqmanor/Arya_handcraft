<template>
  <view class="mine-page">
    <!-- 未登录 -->
    <view v-if="!userStore.isLoggedIn" class="login-box">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
      <view class="title">欢迎来到 Arya手作</view>
      <view class="subtitle">登录后可下单并查看订单与优惠券</view>
      <button class="login-btn" :loading="loading" @click="handleLogin">
        微信一键登录
      </button>
    </view>

    <!-- 已登录 -->
    <view v-else class="profile">
      <!-- 资料卡(点击编辑) -->
      <view class="user-card" @click="go('/pages/profile-edit/profile-edit')">
        <image class="avatar" :src="userStore.avatar || '/static/tab-mine.png'" mode="aspectFill" />
        <view class="user-meta">
          <text class="nickname">{{ userStore.nickname }}</text>
          <text class="cat-name">{{ userStore.user?.cat_name ? `猫咪:${userStore.user.cat_name}` : '点击编辑资料' }}</text>
        </view>
        <text class="arrow">›</text>
      </view>

      <!-- 菜单 -->
      <view class="menu-card">
        <view class="menu-item" @click="go('/pages/orders/orders')">
          <text class="menu-icon">📦</text>
          <text class="menu-label">我的订单</text>
          <text class="arrow">›</text>
        </view>
        <view class="menu-item" @click="go('/pages/addresses/addresses')">
          <text class="menu-icon">📍</text>
          <text class="menu-label">我的地址</text>
          <text class="arrow">›</text>
        </view>
        <view class="menu-item" @click="go('/pages/referral/referral')">
          <text class="menu-icon">🧧</text>
          <text class="menu-label">推荐给他人</text>
          <text class="arrow">›</text>
        </view>
        <button class="menu-item contact-item" open-type="contact">
          <text class="menu-icon">💬</text>
          <text class="menu-label">联系客服</text>
          <text class="arrow">›</text>
        </button>
      </view>

      <!-- 优惠券 -->
      <view class="coupon-section">
        <view class="section-title">我的优惠券</view>
        <view v-if="coupons.length === 0" class="empty-tip">暂无优惠券</view>
        <view v-for="c in coupons" :key="c.id" class="coupon-card">
          <text class="coupon-amount">¥{{ Number(c.amount) || 0 }}</text>
          <view class="coupon-info">
            <text class="coupon-title">{{ c.title }}</text>
            <text class="coupon-status">{{ statusText(c.status) }}</text>
          </view>
        </view>
      </view>

      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>

    <view class="bottom-space" />
    <app-tabbar current="mine" />
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShareAppMessage, onShow } from '@dcloudio/uni-app'

import { getMyCoupons, type CouponItem } from '@/api/auth'
import AppTabbar from '@/components/app-tabbar.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const coupons = ref<CouponItem[]>([])

onShow(async () => {
  if (uni.getStorageSync('access_token')) {
    try {
      await userStore.fetchUser()
      await loadCoupons()
    } catch {
      /* token 失效已清理 */
    }
  }
})

// 分享携带推荐人 ID,朋友经此卡片下单即完成归因
onShareAppMessage(() => ({
  title: 'Arya手作 · 一针一戳的手作毛毡猫咪',
  path: `/pages/index/index?referrer=${userStore.user?.id || 0}`,
}))

function go(url: string) {
  uni.navigateTo({ url })
}

async function handleLogin() {
  loading.value = true
  try {
    await userStore.wxLogin()
    uni.showToast({ title: '登录成功', icon: 'success' })
    await loadCoupons()
  } catch {
    uni.showToast({ title: '登录失败,请重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function loadCoupons() {
  try {
    coupons.value = await getMyCoupons()
  } catch {
    coupons.value = []
  }
}

function statusText(status: string) {
  const map: Record<string, string> = { unused: '未使用', used: '已使用', expired: '已过期' }
  return map[status] || status
}

async function handleLogout() {
  await userStore.logout()
  coupons.value = []
  uni.showToast({ title: '已退出', icon: 'none' })
}
</script>

<style scoped lang="scss">
.mine-page {
  min-height: 100vh;
  padding: 32rpx;
  background: #faf6f0;
  padding-bottom: 360rpx; /* 预留凸起 tabbar 空间 */
}

.bottom-space {
  height: 20rpx;
}

/* 未登录 */
.login-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20vh;
  gap: 24rpx;
}

.login-box .logo {
  width: 120rpx;
  height: 120rpx;
  border-radius: 24rpx;
}

.login-box .title {
  font-size: 36rpx;
  font-weight: 600;
  color: $arya-clay;
}

.login-box .subtitle {
  font-size: 26rpx;
  color: #b9b1ac;
}

.login-btn {
  margin-top: 32rpx;
  width: 480rpx;
  border-radius: 999rpx;
  background: #c9a9a6;
  color: #fff;
  border: none;
  font-size: 30rpx;
}

/* 已登录 */
.profile {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}

.user-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx 32rpx;
  gap: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(90, 83, 80, 0.06);
}

.avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: #f0ebe6;
}

.user-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.nickname {
  font-size: 34rpx;
  font-weight: 600;
  color: #5a5350;
}

.cat-name {
  font-size: 24rpx;
  color: #b9b1ac;
}

.arrow {
  color: #d9cfc9;
  font-size: 36rpx;
}

/* 菜单 */
.menu-card {
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 30rpx 32rpx;
  border-bottom: 1px solid #f5f0eb;
  background: #fff;
  width: 100%;
  box-sizing: border-box;
  border-radius: 0;
  font-size: 28rpx;
  text-align: left;
  line-height: 1.5;
}

.menu-item::after {
  border: none;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  font-size: 36rpx;
}

.menu-label {
  flex: 1;
  color: #5a5350;
  font-weight: 500;
}

/* 优惠券 */
.coupon-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 24rpx;
}

.empty-tip {
  color: #b9b1ac;
  font-size: 26rpx;
  text-align: center;
  padding: 24rpx 0;
}

.coupon-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 20rpx 0;
  border-bottom: 1px solid #f5f0eb;
}

.coupon-card:last-child {
  border-bottom: none;
}

.coupon-amount {
  color: #a98b84;
  font-size: 40rpx;
  font-weight: 700;
}

.coupon-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.coupon-title {
  font-size: 28rpx;
  color: #5a5350;
}

.coupon-status {
  font-size: 24rpx;
  color: #9fb0b5;
}

.logout-btn {
  margin-top: 8rpx;
  border-radius: 999rpx;
  background: #fff;
  color: #a98b84;
  border: 1px solid #e5ded8;
  font-size: 28rpx;
}
</style>
