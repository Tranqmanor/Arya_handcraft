<template>
  <view class="profile-page">
    <view class="card">
      <!-- 头像 -->
      <view class="row">
        <text class="label">头像</text>
        <button class="avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
          <image class="avatar" :src="avatarPreview || '/static/default_avatar.png'" mode="aspectFill" />
          <text class="avatar-tip">点击更换</text>
        </button>
      </view>

      <!-- 昵称 -->
      <view class="row">
        <text class="label">昵称</text>
        <input class="input" type="nickname" :value="nickname" placeholder="点击填写昵称" @input="(e: any) => (nickname = e.detail.value)" />
      </view>

      <!-- 猫咪名字 -->
      <view class="row">
        <text class="label">猫咪名字</text>
        <input class="input" :value="catName" placeholder="你家猫咪的名字(选填)" maxlength="32" @input="(e: any) => (catName = e.detail.value)" />
      </view>

      <!-- 手机号 -->
      <view class="row">
        <text class="label">手机号</text>
        <input class="input" type="number" :value="phone" placeholder="选填,用于订单联系" maxlength="11" @input="(e: any) => (phone = e.detail.value)" />
      </view>
    </view>

    <button class="save-btn" :loading="saving" @click="save">保存</button>
    <view class="tip">以上信息均为选填,仅用于订单联系与展示</view>
  </view>
</template>

<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { updateMe } from '@/api/auth'
import { uploadUserImage } from '@/api/order'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const nickname = ref(userStore.user?.nickname || '')
const avatarPreview = ref(userStore.user?.avatar_url || '')
const catName = ref(userStore.user?.cat_name || '')
const phone = ref(userStore.user?.phone || '')
const saving = ref(false)

onLoad(() => {
  if (!userStore.isLoggedIn) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 800)
  }
})

async function onChooseAvatar(e: any) {
  const tempPath = e.detail.avatarUrl as string
  try {
    // 微信头像为临时路径,上传到 R2 获得持久 URL
    const { url } = await uploadUserImage(tempPath)
    avatarPreview.value = url
    uni.showToast({ title: '头像已上传', icon: 'success' })
  } catch {
    avatarPreview.value = tempPath
  }
}

async function save() {
  saving.value = true
  try {
    const user = await updateMe({
      nickname: nickname.value.trim(),
      avatar_url: avatarPreview.value,
      cat_name: catName.value.trim(),
      phone: phone.value.trim() || null,
    })
    userStore.updateUser(user)
    uni.showToast({ title: '已保存', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 800)
  } catch {
    /* 已提示 */
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
.profile-page {
  min-height: 100vh;
  padding: 24rpx;
  background: #faf6f0;
}

.card {
  background: #fff;
  border-radius: 20rpx;
  padding: 16rpx 28rpx;
  display: flex;
  flex-direction: column;
}

.row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 26rpx 0;
  border-bottom: 1px solid #f5f0eb;
}

.label {
  width: 150rpx;
  font-size: 28rpx;
  color: #7a716d;
  flex-shrink: 0;
}

.avatar-btn {
  background: transparent;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  line-height: 1;
}

.avatar-btn::after {
  border: none;
}

.avatar {
  width: 110rpx;
  height: 110rpx;
  border-radius: 50%;
  background: #f0ebe6;
}

.avatar-tip {
  font-size: 22rpx;
  color: #b9b1ac;
}

.input {
  flex: 1;
  font-size: 28rpx;
  color: #5a5350;
}

.save-btn {
  margin-top: 48rpx;
  border-radius: 999rpx;
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  border: none;
  font-size: 30rpx;
  font-weight: 600;
}

.tip {
  margin-top: 16rpx;
  text-align: center;
  font-size: 22rpx;
  color: #b9b1ac;
}
</style>