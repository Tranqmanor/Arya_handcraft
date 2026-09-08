<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getFinance, type FinanceStats } from '@/api/admin'

const stats = ref<FinanceStats | null>(null)
const loading = ref(false)

const statusLabel: Record<string, string> = {
  pending_price: '待定价',
  pending_deposit: '待付排队定金',
  queued: '排队中',
  pending_making: '待付制作定金',
  making: '制作中',
  pending_final: '待付尾款',
  ready_to_ship: '待寄出',
  shipped: '已寄出',
  completed: '已完成',
  refund_requested: '退款申请中',
  refunded: '已退款',
  cancelled: '已关闭',
}

async function load() {
  loading.value = true
  try {
    stats.value = await getFinance()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div v-loading="loading">
    <div class="bar">
      <h3>账目统计</h3>
      <el-button @click="load">刷新</el-button>
    </div>

    <template v-if="stats">
      <!-- 收支总览卡片 -->
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card shadow="never">
            <div class="kpi-label">累计已收</div>
            <div class="kpi-value">¥{{ stats.received.total }}</div>
            <div class="kpi-sub">定金 {{ stats.received.deposit }} + 制作 {{ stats.received.making }} + 尾款 {{ stats.received.final }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="never">
            <div class="kpi-label">累计退款</div>
            <div class="kpi-value danger">¥{{ stats.refunded_total }}</div>
            <div class="kpi-sub">已退款订单合计</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="never">
            <div class="kpi-label">净收入</div>
            <div class="kpi-value success">¥{{ stats.net_total }}</div>
            <div class="kpi-sub">已收 − 已退</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="never">
            <div class="kpi-label">待收金额</div>
            <div class="kpi-value warn">¥{{ stats.pending_amount }}</div>
            <div class="kpi-sub">各阶段未到账款项</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 订单状态分布 -->
      <el-card shadow="never" class="mt">
        <template #header>订单状态分布</template>
        <div class="status-grid">
          <div v-for="(count, status) in stats.order_count_by_status" :key="status" class="status-cell">
            <div class="status-count">{{ count }}</div>
            <div class="status-name">{{ statusLabel[status] || status }}</div>
          </div>
          <div v-if="!Object.keys(stats.order_count_by_status).length" class="empty-tip">暂无订单</div>
        </div>
      </el-card>

      <!-- 月度流水 -->
      <el-card shadow="never" class="mt">
        <template #header>月度流水</template>
        <el-table :data="stats.monthly" border>
          <el-table-column prop="month" label="月份" width="120" />
          <el-table-column label="收入(元)" width="140">
            <template #default="{ row }">
              <span class="success">+{{ row.income }}</span>
            </template>
          </el-table-column>
          <el-table-column label="退款(元)" width="140">
            <template #default="{ row }">
              <span class="danger">-{{ row.refund }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="net" label="净额(元)" />
        </el-table>
        <div v-if="!stats.monthly.length" class="empty-tip">暂无流水记录</div>
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.mt {
  margin-top: 16px;
}
.kpi-label {
  color: #b9b1ac;
  font-size: 13px;
}
.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #5a5350;
  margin: 6px 0;
}
.kpi-value.danger {
  color: #c0392b;
}
.kpi-value.success {
  color: #6a9955;
}
.kpi-value.warn {
  color: #d35400;
}
.kpi-sub {
  color: #b9b1ac;
  font-size: 12px;
}
.status-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.status-cell {
  background: #faf6f0;
  border-radius: 8px;
  padding: 12px 20px;
  text-align: center;
  min-width: 100px;
}
.status-count {
  font-size: 22px;
  font-weight: 700;
  color: #a98b84;
}
.status-name {
  font-size: 12px;
  color: #7a716d;
  margin-top: 2px;
}
.empty-tip {
  color: #b9b1ac;
  text-align: center;
  padding: 24px 0;
  font-size: 13px;
}
.success {
  color: #6a9955;
}
.danger {
  color: #c0392b;
}
</style>