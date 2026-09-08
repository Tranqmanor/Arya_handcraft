<template>
  <view class="orders-page">
    <view v-if="loading" class="state-tip">加载中...</view>

    <view v-else-if="orders.length === 0" class="empty">
      <text class="empty-icon">📦</text>
      <text class="empty-text">还没有订单</text>
      <button class="primary-btn" @click="goCreate">立即下单</button>
    </view>

    <view v-else class="order-list">
      <view v-for="o in orders" :key="o.id" class="order-card" @click="goDetail(o.id)">
        <view class="card-head">
          <text class="order-no">{{ o.order_no }}</text>
          <text class="status" :class="'s-' + o.status">{{ o.status_label }}</text>
        </view>
        <view class="card-body">
          <text class="cat">🐱 {{ o.cat_name }}</text>
          <text v-if="o.status === 'making'" class="queue making">制作中</text>
          <text v-else-if="o.queue_no > 0" class="queue">当前排队 #{{ o.queue_no }}</text>
        </view>
        <view class="card-amount">
          <text class="amount">总价 {{ o.total_price ? `¥${o.total_price}` : '待报价' }}</text>
          <text class="paid">已付 ¥{{ o.paid_deposit + o.paid_making + o.paid_final }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { getMyOrders, type OrderListItem } from '@/api/order'

const orders = ref<OrderListItem[]>([])
const loading = ref(true)

onShow(async () => {
  loading.value = true
  try {
    orders.value = await getMyOrders()
  } catch {
    orders.value = []
  } finally {
    loading.value = false
  }
})

function goCreate() {
  uni.redirectTo({ url: '/pages/order-create/order-create' })
}

function goDetail(id: number) {
  uni.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` })
}
</script>

<style scoped lang="scss">
.orders-page {
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
  gap: 20rpx;
  padding-top: 30vh;
}

.empty-icon {
  font-size: 80rpx;
}

.empty-text {
  color: #b9b1ac;
  font-size: 28rpx;
}

.primary-btn {
  margin-top: 16rpx;
  width: 360rpx;
  border-radius: 999rpx;
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  border: none;
  font-size: 30rpx;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.order-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  box-shadow: 0 4rpx 16rpx rgba(90, 83, 80, 0.06);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-no {
  font-size: 24rpx;
  color: #b9b1ac;
}

.status {
  font-size: 26rpx;
  font-weight: 600;
  color: #a98b84;
}

.s-completed,
.s-shipped {
  color: #6a9955;
}

.s-cancelled,
.s-refunded {
  color: #b9b1ac;
}

.s-refund_requested {
  color: #d35400;
}

.s-making {
  color: #2980b9;
}

.card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cat {
  font-size: 32rpx;
  font-weight: 600;
  color: #5a5350;
}

.queue {
  font-size: 24rpx;
  color: #a98b84;
}

.queue.making {
  color: #2980b9;
}

.card-amount {
  display: flex;
  justify-content: space-between;
  font-size: 26rpx;
  color: #5a5350;
}

.paid {
  color: #b9b1ac;
  font-size: 24rpx;
}
</style>