<template>
  <view class="detail-page">
    <view v-if="loading" class="state-tip">加载中...</view>

    <view v-else-if="order" class="detail">
      <!-- 状态头卡 -->
      <view class="status-card">
        <text class="status-label">{{ order.status_label }}</text>
        <text class="order-no">单号 {{ order.order_no }}</text>
        <view v-if="queueText" class="queue-badge">
          <text class="queue-num">{{ queueText }}</text>
        </view>
        <text class="created">下单于 {{ formatDate(order.created_at) }}</text>
      </view>

      <!-- 猫咪信息 -->
      <view class="section">
        <text class="sec-title">🐱 猫咪信息</text>
        <view class="info-row"><text class="info-label">名字</text><text>{{ order.cat_name }}</text></view>
        <view v-if="order.requirement" class="info-row">
          <text class="info-label">要求</text><text class="req">{{ order.requirement }}</text>
        </view>
        <view class="image-grid">
          <image v-for="(img, i) in order.images" :key="img" :src="img" class="thumb" mode="aspectFill" @click="previewImages(order.images, i)" />
        </view>
      </view>

      <!-- 付款进度 -->
      <view class="section">
        <text class="sec-title">💰 付款进度</text>
        <view v-if="!order.total_price" class="pay-wait">店长报价后此处将显示各阶段应付金额</view>
        <template v-else>
          <view class="pay-row">
            <text>排队定金</text>
            <text :class="order.paid_deposit >= order.deposit_due ? 'paid' : 'unpaid'">
              ¥{{ order.deposit_due }} {{ order.paid_deposit >= order.deposit_due ? '· 已付款' : '· 待付款' }}
            </text>
          </view>
          <view class="pay-row">
            <text>制作定金</text>
            <text :class="makingPaid ? 'paid' : makingDueReached ? 'unpaid' : 'grey'">
              ¥{{ order.making_due }} {{ makingPaid ? '· 已付款' : makingDueReached ? '· 待付款' : '· 未开始' }}
            </text>
          </view>
          <view class="pay-row">
            <text>尾款</text>
            <text :class="finalPaid ? 'paid' : finalDueReached ? 'unpaid' : 'grey'">
              ¥{{ order.final_due }} {{ finalPaid ? '· 已付款' : finalDueReached ? '· 待付款' : '· 未开始' }}
            </text>
          </view>
          <view v-if="order.coupon_amount > 0" class="pay-row coupon">
            <text>优惠券抵扣</text><text>-¥{{ order.coupon_amount }}</text>
          </view>
          <view v-if="currentStageHint" class="pay-hint">
            💡 {{ currentStageHint }}
          </view>
          <view class="pay-hint warn">⚠️ 定金不退;制作开始前取消订单,排队定金不予退还</view>
        </template>
      </view>

      <!-- 制作进度 -->
      <view v-if="order.making_photos && order.making_photos.length" class="section">
        <text class="sec-title">🪡 制作进度</text>
        <view class="image-grid">
          <image v-for="(img, i) in order.making_photos" :key="img" :src="img" class="thumb tall" mode="aspectFill" @click="previewImages(order.making_photos, i)" />
        </view>
      </view>

      <!-- 邮寄信息 -->
      <view class="section">
        <text class="sec-title">📍 邮寄信息</text>
        <view v-if="order.address && order.address.receiver" class="info-col">
          <text>{{ order.address.receiver }} {{ order.address.phone }}</text>
          <text class="sub">{{ order.address.region }} {{ order.address.detail }}</text>
        </view>
        <view v-else class="sub">未填写地址</view>
      </view>

      <!-- 物流 -->
      <view v-if="order.tracking_no" class="section">
        <text class="sec-title">🚚 物流信息</text>
        <view class="info-row">
          <text>{{ order.shipping_company }} {{ order.tracking_no }}</text>
          <text class="copy" @click="copyTracking">复制</text>
        </view>
      </view>

      <!-- 退款/关闭说明 -->
      <view v-if="order.status === 'refunded'" class="section">
        <text class="sec-title">↩️ 退款</text>
        <view class="info-col">
          <text>退款金额:¥{{ order.refund_amount }}</text>
          <text class="sub">{{ order.refund_reason }}</text>
        </view>
      </view>
      <view v-else-if="order.status === 'cancelled'" class="section">
        <text class="sec-title">🚫 订单已关闭</text>
        <view class="sub">{{ order.cancel_reason }}</view>
      </view>

      <!-- 操作按钮 -->
      <view class="actions">
        <button class="action-btn contact" open-type="contact">联系客服</button>
        <button
          v-if="order.status === 'pending_price' || order.status === 'pending_deposit'"
          class="action-btn danger"
          @click="onCancel"
        >
          取消订单
        </button>
        <button
          v-if="canRequestRefund"
          class="action-btn danger"
          @click="onRefundRequest"
        >
          申请退款
        </button>
        <button v-if="order.status === 'shipped'" class="action-btn primary" @click="onConfirmReceive">
          确认收货
        </button>
      </view>

      <view class="bottom-space" />
    </view>

    <view v-else class="state-tip">订单不存在</view>
  </view>
</template>

<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import { cancelOrder, confirmReceive, getOrderDetail, requestOrderRefund, type OrderDetail } from '@/api/order'

const order = ref<OrderDetail | null>(null)
const loading = ref(true)
let orderId = 0

onLoad((options) => {
  orderId = Number((options as { id?: string } | undefined)?.id || 0)
  loadDetail()
})

async function loadDetail() {
  if (!orderId) {
    loading.value = false
    return
  }
  try {
    order.value = await getOrderDetail(orderId)
  } catch {
    order.value = null
  } finally {
    loading.value = false
  }
}

const makingDueReached = computed(
  () => !!order.value && ['pending_making', 'making', 'pending_final', 'ready_to_ship', 'shipped', 'completed'].includes(order.value.status),
)
const finalDueReached = computed(
  () => !!order.value && ['pending_final', 'ready_to_ship', 'shipped', 'completed'].includes(order.value.status),
)
const makingPaid = computed(() => !!order.value && order.value.paid_making >= order.value.making_due && order.value.making_due >= 0 && order.value.status !== 'pending_making' && order.value.status !== 'queued')
const finalPaid = computed(() => !!order.value && ['ready_to_ship', 'shipped', 'completed'].includes(order.value.status))

const canRequestRefund = computed(
  () =>
    !!order.value &&
    ['queued', 'pending_making', 'making', 'pending_final', 'ready_to_ship'].includes(order.value.status),
)

const queueText = computed(() => {
  if (!order.value) return ''
  if (order.value.status === 'making') return '制作中'
  if (order.value.queue_no > 0) return `当前排队 #${order.value.queue_no}`
  return ''
})

const currentStageHint = computed(() => {
  if (!order.value) return ''
  switch (order.value.status) {
    case 'pending_deposit':
      return `请微信转账排队定金 ¥${order.value.deposit_due} 给店主,付款后由店主确认`
    case 'pending_making':
      return `轮到你的猫咪啦!请转账制作定金 ¥${order.value.making_due},付款后店主开始制作`
    case 'pending_final':
      return `制作完成!请转账尾款 ¥${order.value.final_due},付清后即安排寄出`
    case 'ready_to_ship':
      return '款项已付清,店主将尽快寄出'
    default:
      return ''
  }
})

function previewImages(urls: string[], current: number) {
  uni.previewImage({ urls, current })
}

function copyTracking() {
  if (!order.value) return
  uni.setClipboardData({
    data: `${order.value.shipping_company} ${order.value.tracking_no}`,
    success: () => uni.showToast({ title: '已复制', icon: 'success' }),
  })
}

function onCancel() {
  uni.showModal({
    title: '取消订单',
    content: '排队定金一旦支付不予退还,确定取消?',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await cancelOrder(orderId, '客户主动取消')
        uni.showToast({ title: '已取消', icon: 'success' })
        loadDetail()
      } catch {
        /* 已提示 */
      }
    },
  })
}

function onRefundRequest() {
  uni.showModal({
    title: '申请退款',
    content: '退款金额由店主核定,已支付定金不退。确定申请?',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await requestOrderRefund(orderId, '客户申请退款')
        uni.showToast({ title: '已提交申请', icon: 'success' })
        loadDetail()
      } catch {
        /* 已提示 */
      }
    },
  })
}

function onConfirmReceive() {
  uni.showModal({
    title: '确认收货',
    content: '确认已收到猫咪并验收无误?',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await confirmReceive(orderId)
        uni.showToast({ title: '已确认收货', icon: 'success' })
        loadDetail()
      } catch {
        /* 已提示 */
      }
    },
  })
}
</script>

<style scoped lang="scss">
.detail-page {
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

.detail {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.status-card {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  border-radius: 24rpx;
  padding: 36rpx;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.status-label {
  font-size: 40rpx;
  font-weight: 700;
}

.order-no {
  font-size: 24rpx;
  opacity: 0.85;
}

.queue-badge {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.22);
  border-radius: 12rpx;
  padding: 8rpx 20rpx;
}

.queue-num {
  font-size: 26rpx;
  font-weight: 600;
}

.created {
  font-size: 22rpx;
  opacity: 0.75;
}

.section {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.sec-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #5a5350;
}

.info-row {
  display: flex;
  gap: 20rpx;
  font-size: 26rpx;
  color: #5a5350;
  align-items: baseline;
}

.info-label {
  color: #b9b1ac;
  flex-shrink: 0;
}

.req {
  line-height: 1.6;
}

.info-col {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  font-size: 26rpx;
  color: #5a5350;
}

.sub {
  color: #b9b1ac;
  font-size: 24rpx;
  line-height: 1.6;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
}

.thumb {
  width: 100%;
  height: 140rpx;
  border-radius: 12rpx;
  display: block;
  background: #f0ebe6;
}

.thumb.tall {
  height: 220rpx;
}

.pay-row {
  display: flex;
  justify-content: space-between;
  font-size: 26rpx;
  color: #5a5350;
  padding: 10rpx 0;
  border-bottom: 1px solid #f5f0eb;
}

.pay-row.coupon {
  color: #a98b84;
}

.paid {
  color: #6a9955;
}

.unpaid {
  color: #d35400;
  font-weight: 600;
}

.grey {
  color: #b9b1ac;
}

.pay-hint {
  background: #faf6f0;
  border-radius: 12rpx;
  padding: 16rpx 20rpx;
  font-size: 24rpx;
  color: #5a5350;
  line-height: 1.6;
}

.pay-hint.warn {
  color: #c0392b;
}

.pay-wait {
  color: #b9b1ac;
  font-size: 26rpx;
}

.actions {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 200rpx;
  border-radius: 999rpx;
  font-size: 28rpx;
  line-height: 2.6;
}

.action-btn.contact {
  background: #fff;
  color: #a98b84;
  border: 1px solid #e5ded8;
}

.action-btn.primary {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  border: none;
}

.action-btn.danger {
  background: #fff;
  color: #c0392b;
  border: 1px solid #e8c4be;
}

.bottom-space {
  height: 60rpx;
}
</style>