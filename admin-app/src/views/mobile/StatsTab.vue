<template>
  <div class="tab-page">
    <div class="page-title">📊 账单统计</div>

    <!-- 总收入 = 已完成订单总价之和 + 已支付定金订单的定金之和 -->
    <div class="total-card">
      <div class="total-label">总收入金额</div>
      <div class="total-value">¥{{ total }}</div>
    </div>

    <!-- 三类钻取 -->
    <div class="stage-list">
      <div v-for="v in VIEWS" :key="v.key" class="stage-card" @click="openView(v.key)">
        <div class="stage-left">
          <span class="stage-name">{{ v.name }}</span>
          <span class="stage-count">{{ rowsOf(v.key).length }} 位客户</span>
        </div>
        <div class="stage-right">
          <span class="stage-amount">¥{{ amountOf(v.key) }}</span>
          <span class="arrow">›</span>
        </div>
      </div>
    </div>

    <!-- 钻取列表弹层:左微信名,右金额,点击进订单详情 -->
    <div v-if="activeView" class="stage-overlay" @click.self="activeView = null">
      <div class="stage-panel">
        <div class="panel-title">
          {{ activeViewName }} · 共 {{ currentRows.length }} 单 · ¥{{ amountOf(activeView) }}
        </div>
        <div v-if="currentRows.length === 0" class="empty-tip">暂无记录</div>
        <div v-for="c in currentRows" :key="c.orderId" class="customer-row" @click="goDetail(c.orderId)">
          <span>{{ c.customerName }}</span>
          <span class="row-right"><b>¥{{ c.amount }}</b><span class="arrow">›</span></span>
        </div>
        <button class="close-btn" @click="activeView = null">关闭</button>
      </div>
    </div>

    <!-- 订单只读详情(同首页排队详情,层叠在钻取之上) -->
    <div v-if="detailOrder" class="detail-overlay" @click.self="detailOrder = null">
      <div class="detail-panel">
        <div class="detail-title">
          <template v-if="detailOrder.catName">{{ detailOrder.catName }} · </template>{{ detailOrder.wechatName || detailOrder.customerName || '订单' }}
        </div>

        <div v-if="detailOrder.catPhotos && detailOrder.catPhotos.length" class="detail-photos">
          <img v-for="(p, i) in detailOrder.catPhotos" :key="i" :src="p" alt="" />
        </div>

        <div class="d-row"><span>排队编号</span><b>{{ queueIndexOf(store.orders, detailOrder.id) || '—' }}</b></div>
        <div class="d-row"><span>客户微信名</span><b>{{ detailOrder.wechatName || '—' }}</b></div>
        <div v-if="detailOrder.customerName" class="d-row"><span>客户姓名</span><b>{{ detailOrder.customerName }}</b></div>
        <div v-if="detailOrder.catName" class="d-row"><span>猫咪名字</span><b>{{ detailOrder.catName }}</b></div>
        <div v-if="(detailOrder.catCount || 0) > 1" class="d-row"><span>猫咪数量</span><b>{{ detailOrder.catCount }}</b></div>
        <div class="d-row"><span>下单时间</span><b>{{ fmtTime(detailOrder.orderTime || detailOrder.createdAt) }}</b></div>
        <div class="d-row"><span>付款状态</span><b :style="{ color: statusColor(detailOrder) }">{{ statusLabel(detailOrder) }}</b></div>
        <div class="d-row"><span>联系电话</span><b>{{ detailOrder.phone || '—' }}</b></div>
        <div class="d-row"><span>邮寄地址</span><b>{{ detailOrder.address || '—' }}</b></div>
        <div v-if="detailOrder.requirement" class="d-row"><span>特殊要求</span><b>{{ detailOrder.requirement }}</b></div>
        <div v-if="detailOrder.note" class="d-row"><span>备注</span><b>{{ detailOrder.note }}</b></div>

        <div class="amounts">
          <div class="amount-row"><span>定金</span><b>¥{{ detailOrder.depositDue }}{{ detailOrder.depositPaid ? ' ✓' : '' }}</b></div>
          <div class="amount-row"><span>尾款</span><b>¥{{ detailOrder.finalDue }}{{ detailOrder.finalPaid ? ' ✓' : '' }}</b></div>
          <div class="amount-row total"><span>总价</span><b>¥{{ detailOrder.depositDue + detailOrder.finalDue }}</b></div>
        </div>

        <button class="close-btn" @click="detailOrder = null">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { billRows, billTotal, totalReceived, type BillView } from '@/local/bills'
import { queueIndexOf } from '@/local/store'
import { PAYMENT_COLOR, PAYMENT_LABEL, paymentStatusOf, type LocalOrder } from '@/local/types'
import { useAppStore } from '@/stores/app'

const store = useAppStore()

const VIEWS: { key: BillView; name: string }[] = [
  { key: 'completed', name: '已完成订单' },
  { key: 'deposit', name: '已支付定金' },
  { key: 'unpaid_final', name: '未支付尾款' },
]

const activeView = ref<BillView | null>(null)

const total = computed(() => totalReceived(store.orders))

function rowsOf(view: BillView) {
  return billRows(store.orders, view)
}

function amountOf(view: BillView) {
  return billTotal(store.orders, view)
}

const activeViewName = computed(() =>
  activeView.value ? VIEWS.find((v) => v.key === activeView.value)?.name || '' : '',
)

const currentRows = computed(() => (activeView.value ? rowsOf(activeView.value) : []))

function openView(view: BillView) {
  activeView.value = view
}

// —— 订单只读详情(层叠在钻取列表之上,关闭后仍在账单页) ——
const detailOrder = ref<LocalOrder | null>(null)

function goDetail(orderId: string) {
  const o = store.orders.find((x) => x.id === orderId)
  if (o) detailOrder.value = o
}

function statusLabel(o: LocalOrder) {
  return PAYMENT_LABEL[paymentStatusOf(o)]
}

function statusColor(o: LocalOrder) {
  return PAYMENT_COLOR[paymentStatusOf(o)]
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

.total-card {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  border-radius: 16px;
  padding: 24px;
  color: #fff;
  margin-bottom: 16px;
}
.total-label {
  font-size: 13px;
  opacity: 0.85;
}
.total-value {
  font-size: 32px;
  font-weight: 700;
  margin-top: 6px;
}

.stage-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stage-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(90, 83, 80, 0.06);
  cursor: pointer;
}
.stage-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stage-name {
  font-size: 15px;
  font-weight: 600;
  color: #5a5350;
}
.stage-count {
  font-size: 12px;
  color: #b9b1ac;
}
.stage-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.stage-amount {
  font-size: 18px;
  font-weight: 700;
  color: #a98b84;
}
.arrow {
  color: #d9cfc9;
  font-size: 20px;
}

/* 钻取弹层 */
.stage-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 50;
  display: flex;
  align-items: flex-end;
}
.stage-panel {
  width: 100%;
  background: #fff;
  border-radius: 16px 16px 0 0;
  padding: 20px 18px calc(20px + env(safe-area-inset-bottom));
  max-height: 70vh;
  overflow-y: auto;
}
.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 14px;
  text-align: center;
}
.customer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 13px 8px;
  border-bottom: 1px solid #f5f0eb;
  font-size: 15px;
  color: #5a5350;
  cursor: pointer;
}
.customer-row:last-of-type {
  border-bottom: none;
}
.row-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.row-right b {
  color: #a98b84;
  font-size: 15px;
}
.arrow {
  color: #d9cfc9;
}
.empty-tip {
  color: #b9b1ac;
  text-align: center;
  padding: 24px 0;
}
.close-btn {
  margin-top: 16px;
  width: 100%;
  padding: 12px;
  border: 1px solid #e5ded8;
  border-radius: 10px;
  background: #fff;
  color: #7a716d;
  font-size: 15px;
  cursor: pointer;
}

/* 只读详情弹层(层叠在钻取列表 z-50 之上) */
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 60;
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
.detail-photos {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-bottom: 14px;
}
.detail-photos img {
  width: 92px;
  height: 92px;
  border-radius: 14px;
  object-fit: cover;
  display: block;
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
  width: 78px;
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
.amount-row.total {
  border-top: 1px dashed #e5ded8;
  margin-top: 4px;
  padding-top: 8px;
  font-weight: 700;
}
</style>