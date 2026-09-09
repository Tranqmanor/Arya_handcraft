<template>
  <div class="orders-page">
    <div class="top-bar">
      <span class="back" @click="goBack">‹ 返回</span>
      <span class="title">订单信息</span>
      <span class="action" @click="importCsv">导入 CSV</span>
      <span class="action" @click="exportCsv">导出 CSV</span>
      <input ref="importInput" type="file" accept=".csv,text/csv" hidden @change="onImportFile" />
    </div>

    <div class="btn-row">
      <button class="add-btn" @click="openCreate">+ 新增订单</button>
    </div>

    <div v-if="orders.length === 0" class="empty-tip">暂无订单,点击「新增订单」录入</div>

    <div class="order-list">
      <div v-for="o in displayOrders" :key="o.id" class="order-card" @click="openEdit(o)">
        <div class="card-body">
          <div class="cat-photo">
            <img v-if="o.catPhoto" :src="o.catPhoto" alt="" />
            <span v-else class="photo-ph">🐾</span>
          </div>
          <div class="card-main">
            <div class="card-head">
              <span class="cat">{{ o.catName }}</span>
              <span class="status" :style="{ color: colorOf(o) }">{{ labelOf(o) }}</span>
            </div>
            <div class="card-sub">
              <span>{{ o.wechatName || o.customerName }}</span>
              <span v-if="queueIndexOf(orders, o.id) > 0">排队 #{{ queueIndexOf(orders, o.id) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 录入/编辑表单 -->
    <div v-if="formVisible" class="form-overlay">
      <div class="form-panel">
        <div class="form-title">{{ editingId ? '编辑订单' : '新增订单' }}</div>

        <div class="field-row"><label>客户微信名</label><input v-model="form.wechatName" placeholder="必填(首页排队展示)" /></div>
        <div class="field-row"><label>客户姓名</label><input v-model="form.customerName" placeholder="选填" /></div>
        <div class="field-row"><label>猫咪名字</label><input v-model="form.catName" placeholder="必填" /></div>
        <div class="field-row">
          <label>猫咪照片</label>
          <div class="photo-picker" @click="fileInput?.click()">
            <img v-if="form.catPhoto" :src="form.catPhoto" alt="" />
            <div v-else class="photo-empty">＋<span>上传照片</span></div>
            <button v-if="form.catPhoto" class="photo-remove" @click.stop="form.catPhoto = ''">×</button>
          </div>
          <input ref="fileInput" type="file" accept="image/*" hidden @change="onPhotoPicked" />
        </div>
        <div class="field-row">
          <label>下单时间</label>
          <el-date-picker
            v-model="form.orderTime"
            type="datetime"
            placeholder="选择下单时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            format="YYYY-MM-DD HH:mm"
            style="width: 100%"
          />
        </div>
        <div class="field-row"><label>联系电话</label><input v-model="form.phone" placeholder="选填" /></div>
        <div class="field-row"><label>邮寄地址</label><input v-model="form.address" placeholder="选填" /></div>
        <div class="field-row"><label>备注</label><input v-model="form.note" placeholder="选填" /></div>

        <div class="field-row">
          <label>订单总价(元)</label>
          <input v-model.number="form.totalPrice" type="number" min="0" placeholder="输入总价,自动计算各期款项" />
        </div>
        <div class="amount-grid">
          <div class="amount-cell">
            <label>排队定金</label>
            <div class="ro-box">¥{{ depositDue }}</div>
          </div>
          <div class="amount-cell">
            <label>制作定金</label>
            <div class="ro-box">¥{{ makingDue }}</div>
          </div>
          <div class="amount-cell">
            <label>尾款</label>
            <div class="ro-box">¥{{ finalDue }}</div>
          </div>
        </div>

        <div class="field-row">
          <label>付款状态(单选,再点一次可取消)</label>
          <div class="pay-btns">
            <button :class="['pay-btn', { on: payStatus === 'deposit' }]" @click="pickPay('deposit')">排队定金已付</button>
            <button :class="['pay-btn', { on: payStatus === 'making' }]" @click="pickPay('making')">制作定金已付</button>
            <button :class="['pay-btn', { on: payStatus === 'final' }]" @click="pickPay('final')">尾款已付</button>
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
import { ElMessage, ElMessageBox } from 'element-plus'

import { createLocalOrder, queueIndexOf, timeMs } from '@/local/store'
import { compressImageToDataUrl } from '@/local/img'
import { useAppStore } from '@/stores/app'
import { downloadCsv, ordersToCsv, ordersFromCsv } from '@/local/csv'
import { PAYMENT_COLOR, PAYMENT_LABEL, paymentStatusOf, type LocalOrder } from '@/local/types'

const store = useAppStore()
const orders = computed(() => store.orders)
const formVisible = ref(false)
const editingId = ref<string | null>(null)

const emit = defineEmits<{ back: [] }>()

const form = reactive({
  wechatName: '',
  customerName: '',
  catName: '',
  catPhoto: '',
  orderTime: '' as string,
  phone: '',
  address: '',
  note: '',
  totalPrice: 0,
})

const fileInput = ref<HTMLInputElement | null>(null)

async function onPhotoPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    form.catPhoto = await compressImageToDataUrl(file)
  } catch {
    ElMessage.error('照片读取失败,请换一张试试')
  }
  input.value = '' // 允许连续选同一文件
}

// —— CSV 导入 ——
const importInput = ref<HTMLInputElement | null>(null)

function importCsv() {
  importInput.value?.click()
}

async function onImportFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  let text = ''
  try {
    text = await file.text()
  } catch {
    ElMessage.error('文件读取失败')
    return
  }
  const parsed = ordersFromCsv(text)
  if (parsed.length === 0) {
    ElMessage.error('未识别到订单:请使用本 App 导出的 CSV(列名需一致,且含「猫咪名字」「付款状态」列)')
    return
  }
  try {
    await ElMessageBox.confirm(
      `识别到 ${parsed.length} 条订单,将作为新订单追加导入(猫咪照片不随 CSV 保存)。`,
      '导入 CSV',
      { confirmButtonText: '导入', cancelButtonText: '取消', type: 'info' },
    )
  } catch {
    return // 用户取消
  }
  store.addOrders(parsed)
  ElMessage.success(`已导入 ${parsed.length} 条订单`)
}

/** 付款状态单选:未付 / 排队定金 / 制作定金 / 尾款(递进,保存时映射三布尔) */
const payStatus = ref<'none' | 'deposit' | 'making' | 'final'>('none')

function pickPay(s: 'deposit' | 'making' | 'final') {
  payStatus.value = payStatus.value === s ? 'none' : s
}

// —— 自动计算:排队定金固定 300;总价≥1000 时制作定金 = floor10(总价×30% − 300),否则 0;尾款 = 余额 ——
const depositDue = computed(() => 300)
const makingDue = computed(() => {
  const t = Number(form.totalPrice) || 0
  if (t < 1000) return 0
  return Math.floor((t * 0.3 - 300) / 10) * 10
})
const finalDue = computed(() => {
  const t = Number(form.totalPrice) || 0
  return Math.max(0, t - depositDue.value - makingDue.value)
})

const displayOrders = computed(() =>
  [...orders.value].sort((a, b) => timeMs(b) - timeMs(a)),
)

function labelOf(o: LocalOrder) {
  return PAYMENT_LABEL[paymentStatusOf(o)]
}

function colorOf(o: LocalOrder) {
  return PAYMENT_COLOR[paymentStatusOf(o)]
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    wechatName: '',
    customerName: '',
    catName: '',
    catPhoto: '',
    orderTime: '',
    phone: '',
    address: '',
    note: '',
    totalPrice: 0,
  })
  payStatus.value = 'none'
  formVisible.value = true
}

function openEdit(o: LocalOrder) {
  editingId.value = o.id
  Object.assign(form, {
    wechatName: o.wechatName || '',
    customerName: o.customerName,
    catName: o.catName,
    catPhoto: o.catPhoto || '',
    orderTime: o.orderTime || o.createdAt,
    phone: o.phone || '',
    address: o.address || '',
    note: o.note || '',
    totalPrice: o.totalPrice ?? o.depositDue + o.makingDue + o.finalDue,
  })
  payStatus.value = o.finalPaid ? 'final' : o.makingPaid ? 'making' : o.depositPaid ? 'deposit' : 'none'
  formVisible.value = true
}

function save() {
  if (!form.wechatName.trim()) {
    ElMessage.warning('请填写客户微信名')
    return
  }
  if (!form.catName.trim()) {
    ElMessage.warning('请填写猫咪名字')
    return
  }
  if (!form.orderTime) {
    ElMessage.warning('请选择下单时间')
    return
  }
  const total = Number(form.totalPrice) || 0
  if (total <= 0) {
    ElMessage.warning('请填写订单总价')
    return
  }
  const data = {
    wechatName: form.wechatName.trim(),
    customerName: form.customerName.trim(),
    catName: form.catName.trim(),
    catPhoto: form.catPhoto || undefined,
    orderTime: form.orderTime,
    phone: form.phone.trim(),
    address: form.address.trim(),
    note: form.note.trim(),
    depositDue: depositDue.value,
    makingDue: makingDue.value,
    finalDue: finalDue.value,
    // 单选状态 → 递进布尔(付款按顺序发生)
    depositPaid: payStatus.value !== 'none',
    makingPaid: payStatus.value === 'making' || payStatus.value === 'final',
    finalPaid: payStatus.value === 'final',
  }
  // 先关闭弹层再落库(本地存储为同步瞬时操作,保证点击立即有响应)
  formVisible.value = false
  if (editingId.value) {
    const existing = orders.value.find((x) => x.id === editingId.value)
    if (existing) {
      store.updateOrder({ ...existing, ...data, totalPrice: total })
    }
  } else {
    store.addOrder(createLocalOrder({ ...data, totalPrice: total }))
  }
  ElMessage.success('已保存')
}

async function remove() {
  if (!editingId.value) return
  try {
    await ElMessageBox.confirm(`确定删除「${form.catName}」这个订单?`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  store.removeOrder(editingId.value)
  formVisible.value = false
  ElMessage.success('已删除')
}

function exportCsv() {
  downloadCsv(`订单列表_${new Date().toISOString().slice(0, 10)}.csv`, ordersToCsv(orders.value))
}

function goBack() {
  emit('back')
}
</script>

<style scoped>
.orders-page {
  padding: 16px;
}
.top-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.back {
  color: #a98b84;
  cursor: pointer;
  font-size: 15px;
}
.title {
  flex: 1;
  text-align: center;
  font-weight: 600;
  color: #5a5350;
  font-size: 16px;
}
.action {
  color: #a98b84;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
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
.card-body {
  display: flex;
  align-items: center;
  gap: 12px;
}
.card-main {
  flex: 1;
  min-width: 0;
}
/* 圆角正方形猫咪照片 */
.cat-photo {
  width: 54px;
  height: 54px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5efe8;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cat-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.photo-ph {
  font-size: 22px;
  opacity: 0.6;
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

/* 表单内照片选择器 */
.photo-picker {
  position: relative;
  width: 92px;
  height: 92px;
  border-radius: 14px;
  overflow: hidden;
  background: #faf6f0;
  border: 1px dashed #e0d6cd;
  cursor: pointer;
}
.photo-picker img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.photo-empty {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: #b9b1ac;
  font-size: 24px;
}
.photo-empty span {
  font-size: 11px;
}
.photo-remove {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
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

/* 自动计算的只读金额框 */
.ro-box {
  padding: 10px 8px;
  border: 1px dashed #e5ded8;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  color: #a98b84;
  font-weight: 600;
  text-align: center;
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