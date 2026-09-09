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
      <div v-for="o in displayOrders" :key="o.id" class="order-card" @click="openDetail(o)">
        <div class="card-body">
          <div class="cat-photo">
            <img v-if="o.catPhotos && o.catPhotos.length" :src="o.catPhotos[0]" alt="" />
            <span v-else class="photo-ph">🐾</span>
          </div>
          <div class="card-main">
            <div class="card-head">
              <span class="cat">{{ o.catName || o.wechatName || o.customerName || '订单' }}</span>
              <span class="status" :style="{ color: colorOf(o) }">{{ labelOf(o) }}</span>
            </div>
            <div class="card-sub">
              <span>{{ o.wechatName || o.customerName }}</span>
              <span class="sub-right">
                <em v-if="(o.catCount || 0) > 2" class="cnt">{{ o.catCount }}只猫</em>
                <span v-if="queueIndexOf(orders, o.id) > 0">排队 #{{ queueIndexOf(orders, o.id) }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单详情(只读) -->
    <div v-if="detailOrder" class="detail-overlay" @click.self="detailOrder = null">
      <div class="detail-panel">
        <div class="detail-title">
          <template v-if="detailOrder.catName">{{ detailOrder.catName }} · </template>{{ detailOrder.wechatName || detailOrder.customerName || '订单' }}
        </div>

        <div v-if="detailOrder.catPhotos && detailOrder.catPhotos.length" class="detail-photos">
          <img v-for="(p, i) in detailOrder.catPhotos" :key="i" :src="p" alt="" />
        </div>

        <div class="d-row"><span>排队编号</span><b>{{ queueIndexOf(orders, detailOrder.id) || '—' }}</b></div>
        <div class="d-row"><span>客户微信名</span><b>{{ detailOrder.wechatName || '—' }}</b></div>
        <div v-if="detailOrder.customerName" class="d-row"><span>客户姓名</span><b>{{ detailOrder.customerName }}</b></div>
        <div v-if="detailOrder.catName" class="d-row"><span>猫咪名字</span><b>{{ detailOrder.catName }}</b></div>
        <div class="d-row"><span>猫咪数量</span><b>{{ detailOrder.catCount || 1 }}</b></div>
        <div class="d-row"><span>下单时间</span><b>{{ fmtTime(detailOrder.orderTime || detailOrder.createdAt) }}</b></div>
        <div class="d-row"><span>付款状态</span><b :style="{ color: colorOf(detailOrder) }">{{ labelOf(detailOrder) }}</b></div>
        <div class="d-row"><span>联系电话</span><b>{{ detailOrder.phone || '—' }}</b></div>
        <div class="d-row"><span>邮寄地址</span><b>{{ detailOrder.address || '—' }}</b></div>
        <div v-if="detailOrder.note" class="d-row"><span>备注</span><b>{{ detailOrder.note }}</b></div>

        <div class="amounts">
          <div class="amount-row"><span>定金</span><b>¥{{ detailOrder.depositDue }}{{ detailOrder.depositPaid ? ' ✓' : '' }}</b></div>
          <div class="amount-row"><span>尾款</span><b>¥{{ detailOrder.finalDue }}{{ detailOrder.finalPaid ? ' ✓' : '' }}</b></div>
          <div class="amount-row total"><span>总价</span><b>¥{{ detailOrder.depositDue + detailOrder.finalDue }}</b></div>
        </div>

        <div class="detail-actions">
          <button class="btn primary" @click="editFromDetail">✏️ 编辑</button>
          <button class="btn ghost" @click="detailOrder = null">关闭</button>
        </div>
      </div>
    </div>

    <!-- 录入/编辑表单 -->
    <div v-if="formVisible" class="form-overlay">
      <div class="form-panel">
        <div class="form-title">{{ editingId ? '编辑订单' : '新增订单' }}</div>

        <div class="field-row"><label>客户微信名</label><input v-model="form.wechatName" placeholder="必填(首页排队展示)" /></div>
        <div class="field-row"><label>客户姓名</label><input v-model="form.customerName" placeholder="选填" /></div>
        <div class="field-row"><label>猫咪名字</label><input v-model="form.catName" placeholder="选填(为空时首页排队不展示)" /></div>
        <div class="field-row">
          <label>猫咪数量</label>
          <el-input-number v-model="form.catCount" :min="1" :max="99" :step="1" style="width: 100%" />
        </div>
        <div class="field-row">
          <label>猫咪照片(可多张,一猫一张)</label>
          <div class="photo-grid">
            <div v-for="(p, i) in form.catPhotos" :key="i" class="photo-cell">
              <img :src="p" alt="" />
              <button class="photo-remove" @click.stop="form.catPhotos.splice(i, 1)">×</button>
            </div>
            <div class="photo-cell photo-add" @click="pickPhoto">＋<span>上传</span></div>
          </div>
          <input ref="fileInput" type="file" accept="image/*" multiple hidden @change="onPhotoPicked" />
        </div>
        <div class="field-row">
          <label>下单时间</label>
          <input v-model="form.orderTime" type="datetime-local" step="1" />
        </div>
        <div class="field-row"><label>联系电话</label><input v-model="form.phone" placeholder="选填" /></div>
        <div class="field-row"><label>邮寄地址</label><input v-model="form.address" placeholder="选填" /></div>
        <div class="field-row"><label>备注</label><input v-model="form.note" placeholder="选填" /></div>

        <div class="field-row">
          <label>订单总价(元)</label>
          <input v-model.number="form.totalPrice" type="number" min="0" placeholder="输入总价,尾款自动 = 总价 − 定金" />
        </div>
        <div class="amount-grid">
          <div class="amount-cell">
            <label>定金(元,手动输入)</label>
            <input v-model.number="form.deposit" type="number" min="0" placeholder="定金" />
          </div>
          <div class="amount-cell">
            <label>尾款(自动计算)</label>
            <div class="ro-box">¥{{ finalDue }}</div>
          </div>
        </div>

        <div class="field-row">
          <label>付款状态(单选,再点一次可取消)</label>
          <div class="pay-btns">
            <button :class="['pay-btn', { on: payStatus === 'deposit' }]" @click="pickPay('deposit')">定金已支付</button>
            <button :class="['pay-btn', { on: payStatus === 'final' }]" @click="pickPay('final')">尾款已支付</button>
          </div>
        </div>

        <div class="form-actions">
          <button class="btn ghost" @click="formVisible = false">取消</button>
          <button class="btn primary" @click="save">保存</button>
        </div>
        <button v-if="editingId" class="btn del" @click="remove">删除该订单</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { createLocalOrder, queueIndexOf, timeMs } from '@/local/store'
import { compressImageToDataUrl, compressFromDataUrl } from '@/local/img'
import { hasNativeFilePicker, pickNativeFile, dataUrlToText } from '@/local/native-file'
import { useAppStore } from '@/stores/app'
import { downloadCsv, ordersToCsv, ordersFromCsv } from '@/local/csv'
import { PAYMENT_COLOR, PAYMENT_LABEL, paymentStatusOf, type LocalOrder } from '@/local/types'

const store = useAppStore()
const orders = computed(() => store.orders)
const formVisible = ref(false)
const editingId = ref<string | null>(null)
/** 只读详情弹层当前订单 */
const detailOrder = ref<LocalOrder | null>(null)

const emit = defineEmits<{ back: [] }>()

const form = reactive({
  wechatName: '',
  customerName: '',
  catName: '',
  catCount: 1,
  catPhotos: [] as string[],
  orderTime: '' as string,
  phone: '',
  address: '',
  note: '',
  totalPrice: 0,
  deposit: 0,
})

/** 付款状态单选:未付 / 定金 / 尾款(保存时映射两布尔) */
const payStatus = ref<'none' | 'deposit' | 'final'>('none')

function pickPay(s: 'deposit' | 'final') {
  payStatus.value = payStatus.value === s ? 'none' : s
}

// —— 金额:定金手动输入,尾款 = 总价 − 定金 ——
const finalDue = computed(() => {
  const t = Number(form.totalPrice) || 0
  const d = Number(form.deposit) || 0
  return Math.max(0, t - d)
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

const fileInput = ref<HTMLInputElement | null>(null)

/** 选照片:App 壳走原生桥(每次一张追加);浏览器 input 支持多选 */
async function pickPhoto() {
  if (hasNativeFilePicker()) {
    try {
      const f = await pickNativeFile('image')
      if (f) form.catPhotos.push(await compressFromDataUrl(f.dataUrl))
    } catch {
      ElMessage.error('照片读取失败,请换一张试试')
    }
    return
  }
  fileInput.value?.click()
}

async function onPhotoPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  if (files.length === 0) return
  try {
    for (const f of files) {
      form.catPhotos.push(await compressImageToDataUrl(f))
    }
  } catch {
    ElMessage.error('部分照片读取失败')
  }
  input.value = '' // 允许连续选同一文件
}
// —— CSV 导入 ——
const importInput = ref<HTMLInputElement | null>(null)

function importCsv() {
  if (hasNativeFilePicker()) {
    // App 壳:原生 SAF 选择器(无需存储权限)
    void (async () => {
      const f = await pickNativeFile('csv')
      if (!f) return
      doImportText(dataUrlToText(f.dataUrl))
    })()
    return
  }
  importInput.value?.click()
}

async function onImportFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  try {
    doImportText(await file.text())
  } catch {
    ElMessage.error('文件读取失败')
  }
}

async function doImportText(text: string) {
  const parsed = ordersFromCsv(text)
  if (parsed.length === 0) {
    ElMessage.error('未识别到订单:请使用本 App 导出的 CSV(需含「付款状态」等列)')
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

function goBack() {
  emit('back')
}

function exportCsv() {
  if (orders.value.length === 0) {
    ElMessage.warning('暂无订单可导出')
    return
  }
  const d = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  downloadCsv(
    `arya订单_${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}.csv`,
    ordersToCsv(displayOrders.value),
  )
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    wechatName: '',
    customerName: '',
    catName: '',
    catCount: 1,
    catPhotos: [] as string[],
    orderTime: '',
    phone: '',
    address: '',
    note: '',
    totalPrice: 0,
    deposit: 0,
  })
  payStatus.value = 'none'
  formVisible.value = true
}

function openDetail(o: LocalOrder) {
  detailOrder.value = o
}

/** 详情 → 编辑:先关详情,再把该单载入编辑弹层 */
function editFromDetail() {
  const o = detailOrder.value
  detailOrder.value = null
  if (o) openEdit(o)
}

function fmtTime(iso: string) {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function openEdit(o: LocalOrder) {
  editingId.value = o.id
  Object.assign(form, {
    wechatName: o.wechatName || '',
    customerName: o.customerName,
    catName: o.catName || '',
    catCount: o.catCount && o.catCount > 0 ? o.catCount : 1,
    catPhotos: [...(o.catPhotos || [])],
    orderTime: o.orderTime || o.createdAt,
    phone: o.phone || '',
    address: o.address || '',
    note: o.note || '',
    totalPrice: o.totalPrice ?? o.depositDue + o.finalDue,
    deposit: o.depositDue,
  })
  payStatus.value = o.finalPaid ? 'final' : o.depositPaid ? 'deposit' : 'none'
  formVisible.value = true
}

function save() {
  if (!form.wechatName.trim()) {
    ElMessage.warning('请填写客户微信名')
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
  const deposit = Math.max(0, Number(form.deposit) || 0)
  if (deposit > total) {
    ElMessage.warning('定金不能大于订单总价')
    return
  }
  const data = {
    wechatName: form.wechatName.trim(),
    customerName: form.customerName.trim(),
    catName: form.catName.trim() || undefined,
    catCount: Number(form.catCount) > 1 ? Number(form.catCount) : undefined,
    catPhotos: form.catPhotos.length ? [...form.catPhotos] : undefined,
    orderTime: form.orderTime,
    phone: form.phone.trim(),
    address: form.address.trim(),
    note: form.note.trim(),
    depositDue: deposit,
    finalDue: Math.max(0, total - deposit),
    depositPaid: payStatus.value !== 'none',
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
    await ElMessageBox.confirm(`确定删除「${form.catName || form.wechatName}」这个订单?`, '删除确认', {
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

// —— 账单钻取跳转:自动打开目标订单详情(只读) ——
function tryFocusPending() {
  const id = store.focusOrderId
  if (!id) return
  store.focusOrderId = null
  const o = orders.value.find((x) => x.id === id)
  if (o) openDetail(o)
}
onMounted(tryFocusPending)
watch(() => store.focusOrderId, tryFocusPending)
</script>

<style scoped>
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
.sub-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cnt {
  font-style: normal;
  background: #f5efe8;
  color: #a98b84;
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 11px;
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

/* 多张照片网格 */
.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.photo-cell {
  position: relative;
  width: 84px;
  height: 84px;
  border-radius: 12px;
  overflow: hidden;
  background: #faf6f0;
}
.photo-cell img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.photo-add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border: 1px dashed #e0d6cd;
  color: #b9b1ac;
  font-size: 22px;
  cursor: pointer;
}
.photo-add span {
  font-size: 11px;
}
.photo-remove {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
}

.amount-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

/* 只读详情弹层 */
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
.detail-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}
</style>