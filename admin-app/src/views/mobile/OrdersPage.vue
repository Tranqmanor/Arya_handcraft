<template>
  <div class="orders-page">
    <div class="top-bar">
      <span class="back" @click="goBack">‹ 返回</span>
      <span class="title">订单信息</span>
      <span class="action" @click="exportCsv">导出 CSV</span>
    </div>

    <div class="btn-row">
      <button class="add-btn" @click="openCreate">+ 新增订单</button>
    </div>

    <div v-if="orders.length === 0" class="empty-tip">暂无订单,点击「新增订单」录入</div>

    <div class="order-list">
      <div v-for="o in displayOrders" :key="o.id" class="order-card" @click="openEdit(o)">
        <div class="card-head">
          <span class="cat">{{ o.catName }}</span>
          <span class="status" :style="{ color: colorOf(o) }">{{ labelOf(o) }}</span>
        </div>
        <div class="card-sub">
          <span>{{ o.customerName }}</span>
          <span v-if="queueIndexOf(orders, o.id) > 0">排队 #{{ queueIndexOf(orders, o.id) }}</span>
        </div>
      </div>
    </div>

    <!-- 录入/编辑表单 -->
    <div v-if="formVisible" class="form-overlay">
      <div class="form-panel">
        <div class="form-title">{{ editingId ? '编辑订单' : '新增订单' }}</div>

        <div class="field-row"><label>客户姓名</label><input v-model="form.customerName" placeholder="必填" /></div>
        <div class="field-row"><label>猫咪名字</label><input v-model="form.catName" placeholder="必填" /></div>
        <div class="field-row"><label>联系电话</label><input v-model="form.phone" placeholder="选填" /></div>
        <div class="field-row"><label>邮寄地址</label><input v-model="form.address" placeholder="选填" /></div>
        <div class="field-row"><label>备注</label><input v-model="form.note" placeholder="选填" /></div>

        <div class="amount-grid">
          <div class="amount-cell">
            <label>排队定金(元)</label>
            <input v-model.number="form.depositDue" type="number" min="0" />
          </div>
          <div class="amount-cell">
            <label>制作定金(元)</label>
            <input v-model.number="form.makingDue" type="number" min="0" />
          </div>
          <div class="amount-cell">
            <label>尾款(元)</label>
            <input v-model.number="form.finalDue" type="number" min="0" />
          </div>
        </div>

        <div class="field-row">
          <label>付款状态(点击切换已付)</label>
          <div class="pay-btns">
            <button :class="['pay-btn', { on: form.depositPaid }]" @click="form.depositPaid = !form.depositPaid">排队定金</button>
            <button :class="['pay-btn', { on: form.makingPaid }]" @click="form.makingPaid = !form.makingPaid">制作定金</button>
            <button :class="['pay-btn', { on: form.finalPaid }]" @click="form.finalPaid = !form.finalPaid">尾款</button>
          </div>
        </div>

        <div class="form-actions">
          <button class="btn ghost" @click="formVisible = false">取消</button>
          <button class="btn primary" @click="save">保存</button>
        </div>
        <button v-if="editingId" class="btn del" @click="remove()">删除该订单</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

import {
  createLocalOrder,
  deleteLocalOrder,
  loadOrders,
  queueIndexOf,
  saveOrders,
  updateLocalOrder,
} from '@/local/store'
import { downloadCsv, ordersToCsv } from '@/local/csv'
import { PAYMENT_COLOR, PAYMENT_LABEL, paymentStatusOf, type LocalOrder } from '@/local/types'

const orders = ref<LocalOrder[]>(loadOrders())
const formVisible = ref(false)
const editingId = ref<string | null>(null)

const emit = defineEmits<{ back: [] }>()

const form = reactive({
  customerName: '',
  catName: '',
  phone: '',
  address: '',
  note: '',
  depositDue: 0,
  makingDue: 0,
  finalDue: 0,
  depositPaid: false,
  makingPaid: false,
  finalPaid: false,
})

const displayOrders = computed(() =>
  [...orders.value].sort((a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt)),
)

function labelOf(o: LocalOrder) {
  return PAYMENT_LABEL[paymentStatusOf(o)]
}

function colorOf(o: LocalOrder) {
  return PAYMENT_COLOR[paymentStatusOf(o)]
}

function openCreate() {
  editingId.value = null
  Object.assign(form, emptyForm())
  formVisible.value = true
}

function openEdit(o: LocalOrder) {
  editingId.value = o.id
  Object.assign(form, {
    customerName: o.customerName,
    catName: o.catName,
    phone: o.phone || '',
    address: o.address || '',
    note: o.note || '',
    depositDue: o.depositDue,
    makingDue: o.makingDue,
    finalDue: o.finalDue,
    depositPaid: o.depositPaid,
    makingPaid: o.makingPaid,
    finalPaid: o.finalPaid,
  })
  formVisible.value = true
}

function save() {
  if (!form.customerName.trim() || !form.catName.trim()) {
    alert('客户姓名与猫咪名字为必填')
    return
  }
  const data = {
    customerName: form.customerName.trim(),
    catName: form.catName.trim(),
    phone: form.phone.trim(),
    address: form.address.trim(),
    note: form.note.trim(),
    depositDue: Number(form.depositDue) || 0,
    makingDue: Number(form.makingDue) || 0,
    finalDue: Number(form.finalDue) || 0,
    depositPaid: form.depositPaid,
    makingPaid: form.makingPaid,
    finalPaid: form.finalPaid,
  }
  if (editingId.value) {
    const existing = orders.value.find((x) => x.id === editingId.value)
    if (existing) {
      orders.value = updateLocalOrder(orders.value, { ...existing, ...data })
    }
  } else {
    orders.value = [...orders.value, createLocalOrder(data)]
  }
  saveOrders(orders.value)
  formVisible.value = false
}

function remove() {
  if (!editingId.value) return
  if (!confirm(`确定删除「${form.catName}」这个订单?`)) return
  orders.value = deleteLocalOrder(orders.value, editingId.value)
  saveOrders(orders.value)
  formVisible.value = false
}

function exportCsv() {
  downloadCsv(`订单列表_${new Date().toISOString().slice(0, 10)}.csv`, ordersToCsv(orders.value))
}

function goBack() {
  emit('back')
}

function emptyForm() {
  return {
    customerName: '',
    catName: '',
    phone: '',
    address: '',
    note: '',
    depositDue: 0,
    makingDue: 0,
    finalDue: 0,
    depositPaid: false,
    makingPaid: false,
    finalPaid: false,
  }
}
</script>

<style scoped>
.orders-page {
  padding: 16px;
}
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.back {
  color: #a98b84;
  cursor: pointer;
  font-size: 15px;
}
.title {
  font-weight: 600;
  color: #5a5350;
  font-size: 16px;
}
.action {
  color: #a98b84;
  cursor: pointer;
  font-size: 13px;
}
.btn-row {
  margin-bottom: 12px;
}
.add-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
}
.empty-tip {
  color: #b9b1ac;
  text-align: center;
  padding: 40px 0;
}
.order-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.order-card {
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 8px rgba(90, 83, 80, 0.06);
  cursor: pointer;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cat {
  font-size: 16px;
  font-weight: 600;
  color: #5a5350;
}
.status {
  font-size: 13px;
  font-weight: 600;
}
.card-sub {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 13px;
  color: #b9b1ac;
}

/* 表单 */
.form-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 50;
  display: flex;
  align-items: flex-end;
}
.form-panel {
  width: 100%;
  background: #fff;
  border-radius: 16px 16px 0 0;
  padding: 18px 16px calc(16px + env(safe-area-inset-bottom));
  max-height: 88vh;
  overflow-y: auto;
}
.form-title {
  font-size: 17px;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 12px;
  text-align: center;
}
.field-row {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field-row label {
  font-size: 12px;
  color: #7a716d;
}
.field-row input {
  padding: 10px 12px;
  border: 1px solid #f0ebe6;
  border-radius: 8px;
  font-size: 14px;
  background: #faf6f0;
}
.amount-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 10px;
}
.amount-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.amount-cell label {
  font-size: 12px;
  color: #7a716d;
}
.amount-cell input {
  padding: 10px 8px;
  border: 1px solid #f0ebe6;
  border-radius: 8px;
  font-size: 14px;
  background: #faf6f0;
}
.pay-btns {
  display: flex;
  gap: 8px;
}
.pay-btn {
  flex: 1;
  padding: 9px 0;
  border: 1px solid #e5ded8;
  border-radius: 8px;
  background: #fff;
  color: #7a716d;
  font-size: 13px;
  cursor: pointer;
}
.pay-btn.on {
  background: #c9a9a6;
  color: #fff;
  border-color: #c9a9a6;
}
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}
.btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
}
.btn.ghost {
  background: #fff;
  color: #7a716d;
  border: 1px solid #e5ded8;
}
.btn.primary {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  font-weight: 600;
}
.btn.del {
  margin-top: 10px;
  background: #fff;
  color: #c0392b;
  border: 1px solid #e8c4be;
}
</style>