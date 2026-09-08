<template>
  <div class="tab-page">
    <div class="page-title">📊 账单统计</div>

    <!-- 总收入卡 -->
    <div class="total-card">
      <div class="total-label">总收入金额</div>
      <div class="total-value">¥{{ summary.totalReceived }}</div>
    </div>

    <!-- 三类钻取 -->
    <div class="stage-list">
      <div class="stage-card" @click="openStage('final')">
        <div class="stage-left">
          <span class="stage-name">尾款已支付</span>
          <span class="stage-count">{{ customersByStage('final').length }} 位客户</span>
        </div>
        <div class="stage-right">
          <span class="stage-amount">¥{{ summary.finalReceived }}</span>
          <span class="arrow">›</span>
        </div>
      </div>
      <div class="stage-card" @click="openStage('making')">
        <div class="stage-left">
          <span class="stage-name">制作定金已支付</span>
          <span class="stage-count">{{ customersByStage('making').length }} 位客户</span>
        </div>
        <div class="stage-right">
          <span class="stage-amount">¥{{ summary.makingReceived }}</span>
          <span class="arrow">›</span>
        </div>
      </div>
      <div class="stage-card" @click="openStage('deposit')">
        <div class="stage-left">
          <span class="stage-name">排队定金已支付</span>
          <span class="stage-count">{{ customersByStage('deposit').length }} 位客户</span>
        </div>
        <div class="stage-right">
          <span class="stage-amount">¥{{ summary.depositReceived }}</span>
          <span class="arrow">›</span>
        </div>
      </div>
    </div>

    <!-- 钻取列表弹层 -->
    <div v-if="activeStage" class="stage-overlay" @click.self="activeStage = null">
      <div class="stage-panel">
        <div class="panel-title">{{ stageTitle }} · 共 {{ currentCustomers.length }} 位 · ¥{{ currentAmount }}</div>
        <div v-if="currentCustomers.length === 0" class="empty-tip">暂无记录</div>
        <div v-for="c in currentCustomers" :key="c.orderId" class="customer-row" @click="goDetail()">
          <span>{{ c.customerName }}</span>
          <span class="arrow">›</span>
        </div>
        <button class="close-btn" @click="activeStage = null">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { customersWith, summarize } from '@/local/bills'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const activeStage = ref<'deposit' | 'making' | 'final' | null>(null)

const summary = computed(() => summarize(store.orders))

function customersByStage(stage: 'deposit' | 'making' | 'final') {
  return customersWith(store.orders, stage)
}

const stageTitle = computed(() => {
  const map = { deposit: '排队定金已支付', making: '制作定金已支付', final: '尾款已支付' }
  return activeStage.value ? map[activeStage.value] : ''
})

const currentCustomers = computed(() =>
  activeStage.value ? customersByStage(activeStage.value) : [],
)

const currentAmount = computed(() => {
  if (!activeStage.value) return 0
  return {
    deposit: summary.value.depositReceived,
    making: summary.value.makingReceived,
    final: summary.value.finalReceived,
  }[activeStage.value]
})

function openStage(stage: 'deposit' | 'making' | 'final') {
  activeStage.value = stage
}

function goDetail() {
  // 切到管理 Tab 的订单列表,由用户在列表中定位该单
  store.goto('manage', 'orders')
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