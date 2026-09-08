<template>
  <view class="addr-page">
    <view v-if="loading" class="state-tip">加载中...</view>

    <!-- 编辑/新增表单 -->
    <view v-if="editing" class="form-card">
      <view class="form-title">{{ form.id ? '编辑地址' : '新增地址' }}</view>
      <view class="field">
        <text class="label">收件人</text>
        <input class="input" :value="form.receiver" placeholder="姓名" @input="(e: any) => (form.receiver = e.detail.value)" />
      </view>
      <view class="field">
        <text class="label">手机号</text>
        <input class="input" type="number" :value="form.phone" placeholder="手机号码" maxlength="11" @input="(e: any) => (form.phone = e.detail.value)" />
      </view>
      <view class="field">
        <text class="label">所在地区</text>
        <picker mode="region" @change="onRegionChange">
          <view class="input picker">{{ form.region || '选择省 / 市 / 区' }}</view>
        </picker>
      </view>
      <view class="field">
        <text class="label">详细地址</text>
        <textarea class="textarea" :value="form.detail" placeholder="街道、楼栋、门牌号" maxlength="200" @input="(e: any) => (form.detail = e.detail.value)" />
      </view>
      <view class="default-row">
        <text>设为默认地址</text>
        <switch :checked="form.is_default" color="#c9a9a6" @change="(e: any) => (form.is_default = e.detail.value)" />
      </view>
      <view class="form-actions">
        <button class="btn ghost" @click="editing = null">取消</button>
        <button class="btn primary" :loading="saving" @click="save">保存</button>
      </view>
    </view>

    <!-- 列表 -->
    <template v-else>
      <view v-if="addresses.length === 0" class="empty">
        <text class="empty-icon">📍</text>
        <text class="empty-text">还没有地址,添加一个吧</text>
      </view>

      <view v-else class="addr-list">
        <view v-for="a in addresses" :key="a.id" class="addr-card" @click="selectMode && onSelect(a)">
          <view class="addr-top">
            <text class="receiver">{{ a.receiver }} {{ a.phone }}</text>
            <text v-if="a.is_default" class="default-tag">默认</text>
          </view>
          <text class="addr-detail">{{ a.region }} {{ a.detail }}</text>
          <view class="addr-actions" v-if="!selectMode">
            <text class="link" @click.stop="setDefault(a)">{{ a.is_default ? '' : '设为默认' }}</text>
            <text class="link" @click.stop="startEdit(a)">编辑</text>
            <text class="link danger" @click.stop="onDelete(a)">删除</text>
          </view>
          <text v-if="selectMode" class="select-hint">点击卡片选用此地址</text>
        </view>
      </view>

      <button
        v-if="addresses.length < 6"
        class="add-btn"
        @click="startEdit(null)"
      >
        + 新增地址({{ addresses.length }}/6)
      </button>
      <view v-else class="limit-tip">最多保存 6 个地址</view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { createAddress, getAddresses, removeAddress, updateAddress, type AddressItem } from '@/api/order'

const addresses = ref<AddressItem[]>([])
const loading = ref(true)
const saving = ref(false)
const editing = ref<Partial<AddressItem> | null>(null)
const selectMode = ref(false)

const form = ref({
  id: 0,
  receiver: '',
  phone: '',
  region: '',
  detail: '',
  is_default: false,
})

onLoad((options) => {
  selectMode.value = (options as { mode?: string } | undefined)?.mode === 'select'
})

onShow(load)

async function load() {
  loading.value = true
  try {
    addresses.value = await getAddresses()
  } catch {
    addresses.value = []
  } finally {
    loading.value = false
  }
}

function startEdit(address: AddressItem | null) {
  editing.value = address || {}
  form.value = address
    ? { id: address.id, receiver: address.receiver, phone: address.phone, region: address.region, detail: address.detail, is_default: address.is_default }
    : { id: 0, receiver: '', phone: '', region: '', detail: '', is_default: addresses.value.length === 0 }
}

function onRegionChange(e: any) {
  form.value.region = (e.detail.value || []).join(' ')
}

async function save() {
  if (!form.value.receiver.trim() || !form.value.phone.trim()) {
    uni.showToast({ title: '请填写收件人与手机号', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const payload = {
      receiver: form.value.receiver.trim(),
      phone: form.value.phone.trim(),
      region: form.value.region,
      detail: form.value.detail,
      is_default: form.value.is_default,
    }
    if (form.value.id) {
      await updateAddress(form.value.id, payload)
    } else {
      await createAddress(payload)
    }
    uni.showToast({ title: '已保存', icon: 'success' })
    editing.value = null
    await load()
  } catch {
    /* 已提示 */
  } finally {
    saving.value = false
  }
}

async function setDefault(address: AddressItem) {
  try {
    await updateAddress(address.id, {
      receiver: address.receiver,
      phone: address.phone,
      region: address.region,
      detail: address.detail,
      is_default: true,
    })
    await load()
  } catch {
    /* 已提示 */
  }
}

function onDelete(address: AddressItem) {
  uni.showModal({
    title: '删除地址',
    content: `确定删除「${address.receiver}」的地址?`,
    success: async (res) => {
      if (!res.confirm) return
      try {
        await removeAddress(address.id)
        await load()
      } catch {
        /* 已提示 */
      }
    },
  })
}

function onSelect(address: AddressItem) {
  uni.$emit('address:selected', address)
  uni.navigateBack()
}
</script>

<style scoped lang="scss">
.addr-page {
  min-height: 100vh;
  padding: 24rpx;
  background: #faf6f0;
}

.state-tip {
  display: flex;
  justify-content: center;
  padding-top: 40vh;
  color: #b9b1ac;
  font-size: 28rpx;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding-top: 28vh;
}

.empty-icon {
  font-size: 72rpx;
}

.empty-text {
  color: #b9b1ac;
  font-size: 28rpx;
}

.addr-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.addr-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(90, 83, 80, 0.06);
}

.addr-top {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.receiver {
  font-size: 30rpx;
  font-weight: 600;
  color: #5a5350;
}

.default-tag {
  font-size: 20rpx;
  color: #fff;
  background: #c9a9a6;
  border-radius: 999rpx;
  padding: 2rpx 14rpx;
}

.addr-detail {
  font-size: 26rpx;
  color: #7a716d;
  line-height: 1.6;
}

.addr-actions {
  display: flex;
  gap: 32rpx;
  margin-top: 6rpx;
}

.link {
  font-size: 24rpx;
  color: #a98b84;
}

.link.danger {
  color: #c0392b;
}

.select-hint {
  font-size: 22rpx;
  color: #b9b1ac;
}

.add-btn {
  margin-top: 28rpx;
  border-radius: 999rpx;
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  border: none;
  font-size: 28rpx;
}

.limit-tip {
  margin-top: 28rpx;
  text-align: center;
  color: #b9b1ac;
  font-size: 24rpx;
}

.form-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.form-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #5a5350;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.label {
  font-size: 26rpx;
  color: #7a716d;
}

.input {
  background: #faf6f0;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 28rpx;
  color: #5a5350;
}

.picker {
  color: #5a5350;
}

.textarea {
  background: #faf6f0;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 26rpx;
  color: #5a5350;
  width: 100%;
  min-height: 120rpx;
  box-sizing: border-box;
}

.default-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 26rpx;
  color: #5a5350;
}

.form-actions {
  display: flex;
  gap: 20rpx;
}

.btn {
  flex: 1;
  border-radius: 999rpx;
  font-size: 28rpx;
  line-height: 2.6;
}

.btn.primary {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  border: none;
}

.btn.ghost {
  background: #fff;
  color: #7a716d;
  border: 1px solid #e5ded8;
}
</style>