<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  cancelAdminOrder,
  confirmOrderPayment,
  finishOrderMaking,
  getAdminOrder,
  listAdminOrders,
  reopenOrder,
  refundOrder,
  setOrderCover,
  setOrderMakingPhotos,
  setOrderPrice,
  shipOrder,
  startOrderMaking,
  uploadImage,
  type AdminOrder,
} from '@/api/admin'

const orders = ref<AdminOrder[]>([])
const loading = ref(false)
const statusFilter = ref('')
const searchQuery = ref('')

const detailVisible = ref(false)
const detail = ref<AdminOrder | null>(null)

const statusOptions = [
  { label: '全部', value: '' },
  { label: '待定价', value: 'pending_price' },
  { label: '待付排队定金', value: 'pending_deposit' },
  { label: '排队中', value: 'queued' },
  { label: '待付制作定金', value: 'pending_making' },
  { label: '制作中', value: 'making' },
  { label: '待付尾款', value: 'pending_final' },
  { label: '待寄出', value: 'ready_to_ship' },
  { label: '已寄出', value: 'shipped' },
  { label: '已完成', value: 'completed' },
  { label: '退款申请中', value: 'refund_requested' },
  { label: '已退款', value: 'refunded' },
  { label: '已关闭', value: 'cancelled' },
]

const statusTagType: Record<string, string> = {
  pending_price: 'warning',
  pending_deposit: 'warning',
  queued: 'info',
  pending_making: 'warning',
  making: 'primary',
  pending_final: 'warning',
  ready_to_ship: 'primary',
  shipped: 'success',
  completed: 'success',
  refund_requested: 'danger',
  refunded: 'danger',
  cancelled: 'info',
}

async function load() {
  loading.value = true
  try {
    orders.value = await listAdminOrders({
      status: statusFilter.value || undefined,
      q: searchQuery.value || undefined,
    })
  } finally {
    loading.value = false
  }
}

function openDetail(row: AdminOrder) {
  detail.value = row
  detailVisible.value = true
}

async function refreshDetail(id: number) {
  return getAdminOrder(id)
}

async function onSetPrice() {
  if (!detail.value) return
  const { value } = await ElMessageBox.prompt('输入订单总价(元,整数)', '定价', {
    inputValue: detail.value.total_price ? String(detail.value.total_price) : '',
    inputPattern: /^[1-9]\d*$/,
    inputErrorMessage: '请输入正整数',
  })
  await setOrderPrice(detail.value.id, { total_price: Number(value) })
  ElMessage.success('已定价,等待客户支付排队定金')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onConfirmPayment(stage: 'deposit' | 'making' | 'final') {
  if (!detail.value) return
  const stageName = { deposit: '排队定金', making: '制作定金', final: '尾款' }[stage]
  const dueKey = { deposit: 'deposit_due', making: 'making_due', final: 'final_due' }[stage]
  const { value } = await ElMessageBox.prompt(
    `确认收到「${stageName}」的到账金额(元)`,
    '确认到账',
    {
      inputValue: String((detail.value as Record<string, unknown>)[dueKey] ?? ''),
      inputPattern: /^\d+$/,
      inputErrorMessage: '请输入非负整数',
    },
  )
  await confirmOrderPayment(detail.value.id, { stage, amount: Number(value) })
  ElMessage.success('已确认到账')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onStartMaking() {
  if (!detail.value) return
  await ElMessageBox.confirm('开始制作该订单?客户将收到支付制作定金的提醒', '开始制作')
  await startOrderMaking(detail.value.id)
  ElMessage.success('已通知客户支付制作定金')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onFinishMaking() {
  if (!detail.value) return
  await ElMessageBox.confirm('制作完成?客户将收到支付尾款的提醒', '制作完成')
  await finishOrderMaking(detail.value.id)
  ElMessage.success('已通知客户支付尾款')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onShip() {
  if (!detail.value) return
  const { value: company } = await ElMessageBox.prompt('快递公司', '寄出', {
    inputValue: detail.value.shipping_company || '',
  })
  const { value: no } = await ElMessageBox.prompt('快递单号', '寄出', {
    inputValue: detail.value.tracking_no || '',
  })
  await shipOrder(detail.value.id, { shipping_company: company.trim(), tracking_no: no.trim() })
  ElMessage.success('已寄出')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onRefund() {
  if (!detail.value) return
  const { value } = await ElMessageBox.prompt('退款金额(元)', '处理退款', {
    inputPattern: /^\d+$/,
    inputErrorMessage: '请输入非负整数',
  })
  const { value: reason } = await ElMessageBox.prompt('退款原因(选填)', '处理退款', {
    inputValue: detail.value.refund_reason || '',
  })
  await refundOrder(detail.value.id, { amount: Number(value), reason })
  ElMessage.success('已退款(优惠券已自动返还)')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onCancel() {
  if (!detail.value) return
  await ElMessageBox.confirm('关闭该订单?', '关闭订单')
  await cancelAdminOrder(detail.value.id, '管理员关闭')
  ElMessage.success('已关闭')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onReopen() {
  if (!detail.value) return
  await ElMessageBox.confirm('重开该订单?', '重开')
  await reopenOrder(detail.value.id)
  ElMessage.success('已重开')
  detail.value = await refreshDetail(detail.value.id)
  await load()
}

async function onSetCover(url: string) {
  if (!detail.value) return
  await setOrderCover(detail.value.id, url)
  ElMessage.success('已设为展示封面(将出现在首页作品画廊)')
  detail.value = await refreshDetail(detail.value.id)
}

async function onUploadMakingPhoto() {
  if (!detail.value) return
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/jpeg,image/png,image/webp,image/gif'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file || !detail.value) return
    const { url } = await uploadImage(file)
    const photos = [...(detail.value.making_photos || []), url].slice(0, 3)
    await setOrderMakingPhotos(detail.value.id, photos)
    ElMessage.success('进度图已上传')
    detail.value = await refreshDetail(detail.value.id)
  }
  input.click()
}

async function onRemoveMakingPhoto(url: string) {
  if (!detail.value) return
  const photos = (detail.value.making_photos || []).filter((p) => p !== url)
  await setOrderMakingPhotos(detail.value.id, photos)
  detail.value = await refreshDetail(detail.value.id)
}

function fmtTime(iso: string) {
  return new Date(iso).toLocaleString()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="bar">
      <h3>订单管理</h3>
      <div class="filters">
        <el-select v-model="statusFilter" style="width: 180px" placeholder="状态筛选" @change="load">
          <el-option v-for="o in statusOptions" :key="o.value" :label="o.label" :value="o.value" />
        </el-select>
        <el-input
          v-model="searchQuery"
          placeholder="单号/猫咪名/客户昵称"
          style="width: 220px"
          clearable
          @keyup.enter="load"
          @clear="load"
        />
        <el-button @click="load">搜索</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="orders" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="order_no" label="订单编号" width="200" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="(statusTagType[row.status] as any) || 'info'">{{ row.status_label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="cat_name" label="猫咪" width="100" />
      <el-table-column label="客户" min-width="120">
        <template #default="{ row }">
          <div>{{ row.user_nickname || '未命名' }}</div>
          <div class="sub">{{ row.user_phone || '' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="排队号" width="80">
        <template #default="{ row }">
          <span v-if="row.queue_no > 0">#{{ row.queue_no }}</span>
          <span v-else class="sub">—</span>
        </template>
      </el-table-column>
      <el-table-column label="总价/已收" width="130">
        <template #default="{ row }">
          <div>{{ row.total_price != null ? `¥${row.total_price}` : '待定价' }}</div>
          <div class="sub">已收 ¥{{ row.paid_deposit + row.paid_making + row.paid_final }}</div>
        </template>
      </el-table-column>
      <el-table-column label="地址" min-width="180">
        <template #default="{ row }">
          <div>{{ row.address?.receiver }} {{ row.address?.phone }}</div>
          <div class="sub">{{ row.address?.region }} {{ row.address?.detail }}</div>
        </template>
      </el-table-column>
      <el-table-column label="下单时间" width="160">
        <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 订单详情抽屉 -->
    <el-drawer v-model="detailVisible" title="订单详情" size="560px">
      <template v-if="detail">
        <div class="d-head">
          <el-tag :type="(statusTagType[detail.status] as any) || 'info'">{{ detail.status_label }}</el-tag>
          <span class="d-no">{{ detail.order_no }}</span>
          <el-tag v-if="detail.queue_no > 0" type="info" effect="plain">排队 #{{ detail.queue_no }}</el-tag>
        </div>

        <div class="d-section">
          <div class="d-title">基本信息</div>
          <div class="d-row"><span>猫咪</span><b>{{ detail.cat_name }}</b></div>
          <div class="d-row"><span>客户</span><b>{{ detail.user_nickname || '未命名' }} {{ detail.user_phone ? `(${detail.user_phone})` : '' }}</b></div>
          <div class="d-row"><span>推荐人ID</span><b>{{ detail.referrer_user_id || '—' }}</b></div>
          <div class="d-row"><span>下单时间</span><b>{{ fmtTime(detail.created_at) }}</b></div>
          <div v-if="detail.requirement" class="d-row"><span>特殊要求</span><b>{{ detail.requirement }}</b></div>
          <div class="d-row"><span>收货地址</span><b>{{ detail.address?.receiver }} {{ detail.address?.phone }},{{ detail.address?.region }} {{ detail.address?.detail }}</b></div>
        </div>

        <div class="d-section">
          <div class="d-title">金额(元)</div>
          <div v-if="detail.total_price == null" class="d-empty">待定价</div>
          <template v-else>
            <div class="d-row"><span>总价{{ detail.coupon_amount ? `(券抵 ¥${detail.coupon_amount})` : '' }}</span><b>¥{{ detail.total_price }}</b></div>
            <div class="d-row"><span>排队定金</span><b>应付 {{ detail.deposit_due }} · 已收 {{ detail.paid_deposit }}</b></div>
            <div class="d-row"><span>制作定金</span><b>应付 {{ detail.making_due }} · 已收 {{ detail.paid_making }}</b></div>
            <div class="d-row"><span>尾款</span><b>应付 {{ detail.final_due }} · 已收 {{ detail.paid_final }}</b></div>
          </template>
        </div>

        <div class="d-section">
          <div class="d-title">客户图片(点击设为展示封面)</div>
          <div class="img-grid">
            <div v-for="img in detail.images" :key="img" class="img-cell" :class="{ cover: img === detail.cover_image_url }">
              <img :src="img" @click="onSetCover(img)" />
              <span v-if="img === detail.cover_image_url" class="cover-tag">封面</span>
            </div>
          </div>
        </div>

        <div class="d-section">
          <div class="d-title">制作进度照片({{ (detail.making_photos || []).length }}/3)</div>
          <div class="img-grid">
            <div v-for="p in detail.making_photos" :key="p" class="img-cell">
              <img :src="p" />
              <span class="rm" @click="onRemoveMakingPhoto(p)">×</span>
            </div>
            <div v-if="(detail.making_photos || []).length < 3" class="img-add" @click="onUploadMakingPhoto">+ 上传</div>
          </div>
        </div>

        <div v-if="detail.tracking_no" class="d-section">
          <div class="d-title">物流</div>
          <div class="d-row"><span>快递</span><b>{{ detail.shipping_company }} {{ detail.tracking_no }}</b></div>
        </div>

        <div v-if="detail.status === 'refunded'" class="d-section">
          <div class="d-title">退款</div>
          <div class="d-row"><span>金额</span><b>¥{{ detail.refund_amount }}</b></div>
          <div v-if="detail.refund_reason" class="d-row"><span>原因</span><b>{{ detail.refund_reason }}</b></div>
        </div>

        <!-- 状态操作区 -->
        <div class="d-actions">
          <el-button v-if="detail.status === 'pending_price'" type="primary" @click="onSetPrice">定价</el-button>
          <el-button v-if="detail.status === 'pending_deposit'" type="success" @click="onConfirmPayment('deposit')">
            确认收到排队定金
          </el-button>
          <el-button v-if="detail.status === 'queued'" type="primary" @click="onStartMaking">开始制作</el-button>
          <el-button v-if="detail.status === 'pending_making'" type="success" @click="onConfirmPayment('making')">
            确认收到制作定金
          </el-button>
          <el-button v-if="detail.status === 'making'" type="primary" @click="onFinishMaking">制作完成</el-button>
          <el-button v-if="detail.status === 'pending_final'" type="success" @click="onConfirmPayment('final')">
            确认收到尾款
          </el-button>
          <el-button v-if="detail.status === 'ready_to_ship'" type="primary" @click="onShip">寄出(填物流)</el-button>
          <el-button v-if="detail.status === 'refund_requested'" type="danger" @click="onRefund">处理退款</el-button>
          <el-button
            v-if="!['shipped', 'completed', 'refunded', 'cancelled'].includes(detail.status)"
            type="warning"
            plain
            @click="onCancel"
          >
            关闭订单
          </el-button>
          <el-button v-if="detail.status === 'cancelled'" plain @click="onReopen">重开</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.filters {
  display: flex;
  gap: 8px;
}
.sub {
  color: #b9b1ac;
  font-size: 12px;
}

.d-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.d-no {
  color: #7a716d;
  font-size: 13px;
}
.d-section {
  margin-bottom: 20px;
}
.d-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #5a5350;
  border-left: 3px solid #c9a9a6;
  padding-left: 8px;
}
.d-row {
  display: flex;
  gap: 12px;
  font-size: 13px;
  padding: 4px 0;
}
.d-row span {
  color: #b9b1ac;
  width: 90px;
  flex-shrink: 0;
}
.d-empty {
  color: #b9b1ac;
  font-size: 13px;
}
.img-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.img-cell {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid transparent;
}
.img-cell.cover {
  border-color: #c9a9a6;
}
.img-cell img {
  width: 100%;
  height: 80px;
  object-fit: cover;
  display: block;
  cursor: pointer;
}
.cover-tag {
  position: absolute;
  left: 0;
  bottom: 0;
  background: #c9a9a6;
  color: #fff;
  font-size: 11px;
  padding: 1px 6px;
}
.rm {
  position: absolute;
  top: 2px;
  right: 4px;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.6);
}
.img-add {
  height: 80px;
  border: 1px dashed #d9cfc9;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b9b1ac;
  font-size: 13px;
  cursor: pointer;
}
.d-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 24px;
}
</style>