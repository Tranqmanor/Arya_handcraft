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
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { billRows, billTotal, totalReceived, type BillView } from '@/local/bills'
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

function goDetail(orderId: string) {
  // 跳到订单页并自动打开该订单详情
  activeView.value = null
  store.focusOrder(orderId)
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
</style>