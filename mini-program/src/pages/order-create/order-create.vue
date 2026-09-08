<template>
  <view class="create-page">
    <!-- 规则提示 -->
    <view class="notice-card">
      <view class="notice-line">🧶 每只猫咪都不同，制作价格以店长报价为准</view>
      <view class="notice-line">💰 付款分三阶段：排队定金(下单时) → 制作定金(开始制作时) → 尾款(寄出前)</view>
      <view class="notice-line warn">⚠️ 定金不退，请考虑好再下单</view>
    </view>

    <!-- 表单 -->
    <view class="form-card">
      <view class="field">
        <text class="label">猫咪名字</text>
        <input class="input" :value="catName" placeholder="给你的猫咪起个名字" maxlength="32" @input="(e: any) => (catName = e.detail.value)" />
      </view>

      <view class="field">
        <view class="label-row">
          <text class="label">猫咪图片</text>
          <text class="label-tip">最多 12 张 · 建议先看供图tips</text>
        </view>
        <view class="image-grid">
          <view v-for="(img, i) in images" :key="img" class="image-item">
            <image :src="img" mode="aspectFill" class="image-thumb" @click="previewImage(i)" />
            <view class="image-remove" @click.stop="removeImage(i)">×</view>
          </view>
          <view v-if="images.length < 12" class="image-add" @click="chooseImages">
            <text class="add-icon">+</text>
            <text class="add-text">{{ uploading ? '上传中…' : '添加' }}</text>
          </view>
        </view>
      </view>

      <view class="field" @click="chooseAddress">
        <text class="label">邮寄地址</text>
        <view v-if="selectedAddress" class="address-box">
          <text class="address-main">{{ selectedAddress.receiver }} {{ selectedAddress.phone }}</text>
          <text class="address-detail">{{ selectedAddress.region }} {{ selectedAddress.detail }}</text>
        </view>
        <view v-else class="address-box empty">
          <text>点击选择或前往「我的-我的地址」添加</text>
        </view>
      </view>

      <view class="field" @click="chooseCoupon">
        <text class="label">优惠券</text>
        <view class="address-box">
          <text :class="selectedCoupon ? 'coupon-value' : ''">
            {{ selectedCoupon ? `${selectedCoupon.title} -¥${selectedCoupon.amount}` : availableCoupons.length ? '有可用优惠券,点击选择' : '暂无可用优惠券' }}
          </text>
        </view>
      </view>

      <view class="field">
        <text class="label">特殊要求(选填)</text>
        <textarea class="textarea" :value="requirement" placeholder="毛色/姿态/配饰等特殊要求" maxlength="500" @input="(e: any) => (requirement = e.detail.value)" />
      </view>
    </view>

    <button class="submit-btn" :loading="submitting" :disabled="submitting" @click="submit">
      提交订单
    </button>
    <view class="submit-tip">提交后店长会尽快报价,届时支付排队定金即可锁定排队名额</view>

    <view class="bottom-space" />
    <app-tabbar current="create" />
  </view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import { getMyCoupons, type CouponItem } from '@/api/auth'
import { createOrder, getAddresses, uploadUserImage, type AddressItem } from '@/api/order'
import AppTabbar from '@/components/app-tabbar.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const catName = ref('')
const images = ref<string[]>([])
const requirement = ref('')
const addresses = ref<AddressItem[]>([])
const selectedAddress = ref<AddressItem | null>(null)
const coupons = ref<CouponItem[]>([])
const selectedCoupon = ref<CouponItem | null>(null)
const uploading = ref(false)
const submitting = ref(false)

onLoad(() => {
  ensureLogin()
})

onShow(async () => {
  if (!userStore.isLoggedIn) await ensureLogin()
  await Promise.all([loadAddresses(), loadCoupons()])
})

async function ensureLogin() {
  if (userStore.isLoggedIn) return
  if (!uni.getStorageSync('access_token')) {
    try {
      await userStore.wxLogin()
    } catch {
      uni.showToast({ title: '登录失败,请重试', icon: 'none' })
    }
  } else {
    try {
      await userStore.fetchUser()
    } catch {
      /* token 失效已清理 */
    }
  }
}

async function loadAddresses() {
  if (!userStore.isLoggedIn) return
  try {
    addresses.value = await getAddresses()
    if (!selectedAddress.value) {
      selectedAddress.value = addresses.value.find((a) => a.is_default) || addresses.value[0] || null
    }
  } catch {
    addresses.value = []
  }
}

async function loadCoupons() {
  if (!userStore.isLoggedIn) return
  try {
    coupons.value = (await getMyCoupons()).filter((c) => c.status === 'unused')
  } catch {
    coupons.value = []
  }
}

const availableCoupons = computed(() => coupons.value)

function chooseImages() {
  if (uploading.value) return
  const remain = 12 - images.value.length
  uni.chooseImage({
    count: Math.min(remain, 9),
    sizeType: ['compressed'],
    success: async (res) => {
      uploading.value = true
      try {
        for (const path of res.tempFilePaths) {
          const { url } = await uploadUserImage(path)
          images.value.push(url)
        }
      } catch {
        /* 错误已提示 */
      } finally {
        uploading.value = false
      }
    },
  })
}

function removeImage(index: number) {
  images.value.splice(index, 1)
}

function previewImage(index: number) {
  uni.previewImage({ urls: images.value, current: index })
}

function chooseAddress() {
  if (addresses.value.length === 0) {
    uni.showModal({
      title: '还没有地址',
      content: '前往「我的 - 我的地址」添加邮寄地址?',
      success: (res) => {
        if (res.confirm) uni.navigateTo({ url: '/pages/addresses/addresses' })
      },
    })
    return
  }
  uni.showActionSheet({
    itemList: addresses.value.map((a) => `${a.receiver} ${a.phone} (${a.region})`),
    success: (res) => {
      selectedAddress.value = addresses.value[res.tapIndex] || null
    },
  })
}

function chooseCoupon() {
  if (coupons.value.length === 0) return
  const options = [...coupons.value.map((c) => `${c.title} -¥${Number(c.amount)}`), '不使用优惠券']
  uni.showActionSheet({
    itemList: options,
    success: (res) => {
      selectedCoupon.value = res.tapIndex < coupons.value.length ? coupons.value[res.tapIndex] : null
    },
  })
}

async function submit() {
  if (!catName.value.trim()) {
    uni.showToast({ title: '请填写猫咪名字', icon: 'none' })
    return
  }
  if (images.value.length === 0) {
    uni.showToast({ title: '请至少上传一张猫咪图片', icon: 'none' })
    return
  }
  if (!selectedAddress.value) {
    uni.showToast({ title: '请选择邮寄地址', icon: 'none' })
    return
  }
  if (!userStore.isLoggedIn) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    const referrer = uni.getStorageSync('referrer_id') as number
    await createOrder({
      cat_name: catName.value.trim(),
      images: images.value,
      address_id: selectedAddress.value.id,
      requirement: requirement.value,
      coupon_id: selectedCoupon.value?.id,
      referrer_user_id: referrer || undefined,
    })
    uni.showToast({ title: '下单成功', icon: 'success' })
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/orders/orders' })
    }, 800)
  } catch {
    /* 错误已提示 */
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.create-page {
  min-height: 100vh;
  padding: 24rpx;
  padding-bottom: 360rpx; /* 预留凸起 tabbar 空间 */
  background: #faf6f0;
}

.notice-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  border-left: 8rpx solid #c9a9a6;
}

.notice-line {
  font-size: 24rpx;
  color: #5a5350;
  line-height: 1.6;
}

.notice-line.warn {
  color: #c0392b;
}

.form-card {
  margin-top: 24rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.label {
  font-size: 28rpx;
  font-weight: 600;
  color: #5a5350;
}

.label-tip {
  font-size: 22rpx;
  color: #b9b1ac;
}

.input {
  background: #faf6f0;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 28rpx;
  color: #5a5350;
}

.textarea {
  background: #faf6f0;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 26rpx;
  color: #5a5350;
  width: 100%;
  min-height: 140rpx;
  box-sizing: border-box;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14rpx;
}

.image-item {
  position: relative;
}

.image-thumb {
  width: 100%;
  height: 150rpx;
  border-radius: 12rpx;
  display: block;
  background: #f0ebe6;
}

.image-remove {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-add {
  height: 150rpx;
  border: 2rpx dashed #d9cfc9;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
}

.add-icon {
  font-size: 44rpx;
  color: #b9b1ac;
  line-height: 1;
}

.add-text {
  font-size: 22rpx;
  color: #b9b1ac;
}

.address-box {
  background: #faf6f0;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  font-size: 26rpx;
  color: #5a5350;
}

.address-box.empty {
  color: #b9b1ac;
}

.address-main {
  font-weight: 600;
}

.address-detail {
  font-size: 24rpx;
  color: #7a716d;
}

.coupon-value {
  color: #a98b84;
  font-weight: 600;
}

.submit-btn {
  margin-top: 40rpx;
  border-radius: 999rpx;
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  border: none;
  font-size: 32rpx;
  font-weight: 600;
}

.submit-tip {
  margin-top: 16rpx;
  text-align: center;
  font-size: 22rpx;
  color: #b9b1ac;
  line-height: 1.6;
}

.bottom-space {
  height: 60rpx;
}
</style>