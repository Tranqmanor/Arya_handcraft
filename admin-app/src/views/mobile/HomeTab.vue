<template>
  <div class="tab-page">
    <div class="page-title">📋 当前排队</div>

    <div v-if="queued.length === 0" class="empty-tip">
      暂无排队订单<br />
      <span class="sub">在「管理 → 订单信息」中录入并标记排队定金已付</span>
    </div>

    <div v-else class="queue-list">
      <div
        v-for="(o, idx) in queued"
        :key="o.id"
        class="queue-card"
        @click="openDetail(o)"
      >
        <div class="queue-no">#{{ idx + 1 }}</div>
        <div class="queue-main">
          <div class="row1">
            <span class="customer">{{ o.wechatName || o.customerName }}</span>
            <span class="status" :style="{ color: statusColor(o) }">{{ statusLabel(o) }}</span>
          </div>
          <div class="row2">
            <span class="cat">🐱 {{ o.catName }}</span>
          </div>
        </div>
        <span class="arrow">›</span>
      </div>
    </div>

    <!-- 订单详情弹层 -->
    <div v-if="detailOrder" class="detail-overlay" @click.self="detailOrder = null">
      <div class="detail-panel">
        <div class="detail-title">{{ detailOrder.catName }} · {{ detailOrder.wechatName || detailOrder.customerName }}</div>

        <div class="d-row"><span>排队编号</span><b>#{{ queueNo(detailOrder.id) }}</b></div>
        <div class="d-row"><span>客户微信名</span><b>{{ detailOrder.wechatName || '—' }}</b></div>
        <div class="d-row"><span>下单时间</span><b>{{ fmtTime(detailOrder.orderTime || detailOrder.createdAt) }}</b></div>
        <div class="d-row"><span>付款状态</span><b :style="{ color: statusColor(detailOrder) }">{{ statusLabel(detailOrder) }}</b></div>
        <div class="d-row"><span>联系电话</span><b>{{ detailOrder.phone || '—' }}</b></div>
        <div class="d-row"><span>邮寄地址</span><b>{{ detailOrder.address || '—' }}</b></div>
        <div v-if="detailOrder.requirement" class="d-row"><span>特殊要求</span><b>{{ detailOrder.requirement }}</b></div>
        <div v-if="detailOrder.note" class="d-row"><span>备注</span><b>{{ detailOrder.note }}</b></div>

        <div class="amounts">
          <div class="amount-row"><span>排队定金</span><b>¥{{ detailOrder.depositDue }}{{ detailOrder.depositPaid ? ' ✓' : '' }}</b></div>
          <div class="amount-row"><span>制作定金</span><b>¥{{ detailOrder.makingDue }}{{ detailOrder.makingPaid ? ' ✓' : '' }}</b></div>
          <div class="amount-row"><span>尾款</span><b>¥{{ detailOrder.finalDue }}{{ detailOrder.finalPaid ? ' ✓' : '' }}</b></div>
        </div>

        <button class="close-btn" @click="detailOrder = null">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { PAYMENT_COLOR, PAYMENT_LABEL, paymentStatusOf, type LocalOrder } from '@/local/types'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const detailOrder = ref<LocalOrder | null>(null)

const queued = computed(() => store.queued)

function statusLabel(o: LocalOrder) {
  return PAYMENT_LABEL[paymentStatusOf(o)]
}

function statusColor(o: LocalOrder) {
  return PAYMENT_COLOR[paymentStatusOf(o)]
}

function queueNo(id: string) {
  return queued.value.findIndex((o) => o.id === id) + 1
}

function openDetail(o: LocalOrder) {
  detailOrder.value = o
}

function fmtTime(iso: string) {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<style scoped>
.tab-page {
  padding: 16px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 12px;
}
.empty-tip {
  color: #b9b1ac;
  text-align: center;
  padding: 48px 0;
  line-height: 1.8;
}
.empty-tip .sub {
  font-size: 12px;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.queue-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 8px rgba(90, 83, 80, 0.06);
  cursor: pointer;
}
.queue-no {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0e8e4;
  color: #a98b84;
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.queue-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.row1 {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.customer {
  font-size: 15px;
  font-weight: 600;
  color: #5a5350;
}
.status {
  font-size: 12px;
  font-weight: 600;
}
.row2 {
  font-size: 13px;
  color: #7a716d;
}
.arrow {
  color: #d9cfc9;
  font-size: 20px;
}

/* 详情弹层 */
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 50;
  display: flex;
  align-items: flex-end;
}
.detail-panel {
  width: 100%;
  background: #fff;
  border-radius: 16px 16px 0 0;
  padding: 20px 18px calc(20px + env(safe-area-inset-bottom));
  max-height: 82vh;
  overflow-y: auto;
}
.detail-title {
  font-size: 17px;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 14px;
  text-align: center;
}
.d-row {
  display: flex;
  gap: 12px;
  font-size: 14px;
  padding: 7px 0;
  border-bottom: 1px solid #f5f0eb;
}
.d-row span {
  color: #b9b1ac;
  width: 70px;
  flex-shrink: 0;
}
.d-row b {
  color: #5a5350;
  font-weight: 500;
  word-break: break-all;
}
.amounts {
  margin-top: 12px;
  background: #faf6f0;
  border-radius: 10px;
  padding: 10px 14px;
}
.amount-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #5a5350;
  padding: 5px 0;
}
.close-btn {
  margin-top: 16px;
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: #fff;
  color: #7a716d;
  border: 1px solid #e5ded8;
  font-size: 15px;
  cursor: pointer;
}
</style>