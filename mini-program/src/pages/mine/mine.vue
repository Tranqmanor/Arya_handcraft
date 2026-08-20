<template>
  <view class="mine-page">
    <!-- 未登录 -->
    <view v-if="!userStore.isLoggedIn" class="login-box">
      <image class="logo" src="/static/tab-mine.png" mode="aspectFit" />
      <view class="title">欢迎来到 Arya_handcraft</view>
      <view class="subtitle">登录后可查看优惠券与订单信息</view>
      <button class="login-btn" :loading="loading" @click="handleLogin">
        微信一键登录
      </button>
    </view>

    <!-- 已登录 -->
    <view v-else class="profile">
      <view class="user-card">
        <button class="avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
          <image class="avatar" :src="userStore.avatar || '/static/tab-mine.png'" mode="aspectFill" />
        </button>
        <view class="user-meta">
          <input
            class="nickname-input"
            type="nickname"
            :value="userStore.nickname"
            placeholder="点击填写昵称"
            @blur="onNicknameBlur"
          />
          <view class="phone-row">
            <text class="phone-label">手机号</text>
            <input
              class="phone-input"
              type="text"
              :value="userStore.user?.phone || ''"
              placeholder="选填,用于订单联系"
              @blur="onPhoneBlur"
            />
          </view>
        </view>
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

    <!-- 联系店主(通用) -->
    <button class="contact-btn" @click="contactVisible = true">联系店主 · 定制咨询</button>

    <contact-modal :visible="contactVisible" @close="contactVisible = false" />
  </view>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import { getMyCoupons, updateMe, type CouponItem } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import ContactModal from '@/components/contact-modal.vue'

const userStore = useUserStore()
const loading = ref(false)
const coupons = ref<CouponItem[]>([])
const contactVisible = ref(false)

onShow(async () => {
  // 已有 token 则拉取用户,否则停留在未登录态
  if (uni.getStorageSync('access_token')) {
    try {
      await userStore.fetchUser()
      await loadCoupons()
    } catch {
      // token 失效已清理
    }
  }
})

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

async function onChooseAvatar(e: any) {
  const tempPath = e.detail.avatarUrl as string
  // 实际生产应上传头像到服务器/CDN,这里先展示临时路径
  await saveProfile({ avatar_url: tempPath })
}

async function onNicknameBlur(e: any) {
  const val = (e.detail.value || '').trim()
  if (val && val !== userStore.user?.nickname) {
    await saveProfile({ nickname: val })
  }
}

async function onPhoneBlur(e: any) {
  const val = (e.detail.value || '').trim()
  if (val !== (userStore.user?.phone || '')) {
    await saveProfile({ phone: val })
  }
}

async function saveProfile(data: Record<string, unknown>) {
  try {
    const user = await updateMe(data)
    userStore.updateUser(user)
    uni.showToast({ title: '已保存', icon: 'success' })
  } catch {
    // 提示已由 request 统一处理
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

<style scoped lang="scss">
.mine-page {
  min-height: 100vh;
  padding: 32rpx;
  background: #faf6f0;
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
  gap: 32rpx;
}
.user-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
  gap: 24rpx;
}
.avatar-btn {
  padding: 0;
  margin: 0;
  background: transparent;
  line-height: 1;
}
.avatar-btn::after {
  border: none;
}
.avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
}
.user-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.nickname-input {
  font-size: 32rpx;
  font-weight: 600;
  color: #5a5350;
}
.phone-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.phone-label {
  font-size: 24rpx;
  color: #b9b1ac;
}
.phone-input {
  flex: 1;
  font-size: 26rpx;
  color: #5a5350;
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
  padding: 32rpx 0;
}
.coupon-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 0;
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
  gap: 8rpx;
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
  margin-top: 16rpx;
  border-radius: 999rpx;
  background: #fff;
  color: #a98b84;
  border: 1px solid #e5ded8;
  font-size: 28rpx;
}

.contact-btn {
  margin-top: 32rpx;
  border-radius: 999rpx;
  background: #c9a9a6;
  color: #fff;
  border: none;
  font-size: 30rpx;
  font-weight: 500;
}
</style>

}
</script>

</template>
