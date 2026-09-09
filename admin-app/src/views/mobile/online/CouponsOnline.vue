<template>
  <div class="op-page">
    <div class="top-bar">
      <span class="back" @click="$emit('back')">‹ 返回</span>
      <span class="title">优惠券管理</span>
      <span class="action" @click="openGrant">+ 手动发放</span>
    </div>

    <div class="search-row">
      <input v-model="searchQuery" placeholder="搜索用户(昵称/手机号)" @keyup.enter="doSearch" />
      <button class="search-btn" @click="doSearch">搜索</button>
    </div>

    <div v-if="loading" class="state-tip">加载中...</div>
    <div v-else-if="list.length === 0" class="state-tip">暂无优惠券</div>

    <div v-else class="card-list">
      <div v-for="c in list" :key="c.id" class="card">
        <div class="card-head">
          <span class="card-title">{{ c.title }}</span>
          <el-tag size="small" :type="c.status === 'unused' ? 'success' : 'info'">
            {{ statusText(c.status) }}
          </el-tag>
        </div>
        <div class="card-sub">用户 #{{ c.user_id }} · 面额 ¥{{ Number(c.amount) }} · {{ fmt(c.created_at) }}</div>
      </div>
    </div>

    <!-- 发放弹层 -->
    <div v-if="formVisible" class="overlay" @click.self="formVisible = false">
      <div class="panel">
        <div class="panel-title">手动发放优惠券</div>
        <div class="field">
          <label>搜索用户</label>
          <div class="search-inline">
            <input v-model="grantQuery" placeholder="昵称/手机号" @keyup.enter="doGrantSearch" />
            <button class="mini-btn" @click="doGrantSearch">搜</button>
          </div>
          <select v-model="form.user_id" size="5" class="user-select">
            <option v-for="u in grantUsers" :key="u.id" :value="u.id">
              {{ u.nickname || '未命名' }} (ID:{{ u.id }}) {{ u.phone || '' }}
            </option>
          </select>
        </div>
        <div class="field"><label>券名</label><input v-model="form.title" /></div>
        <div class="field"><label>面额(元)</label><input v-model.number="form.amount" type="number" min="1" /></div>
        <div class="field"><label>有效期(天)</label><input v-model.number="form.expires_days" type="number" min="1" /></div>
        <div class="form-actions">
          <button class="btn ghost" @click="formVisible = false">取消</button>
          <button class="btn primary" :disabled="saving" @click="save">发放</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { grantCoupon, listCoupons, searchUsers, type OnlineCoupon, type UserOption } from '@/api/online'

const list = ref<OnlineCoupon[]>([])
const loading = ref(true)
const saving = ref(false)
const formVisible = ref(false)
const searchQuery = ref('')

const grantUsers = ref<UserOption[]>([])
const grantQuery = ref('')
const form = reactive({ user_id: 0, title: '优惠券', amount: 20, expires_days: 30 })

function statusText(s: string) {
  const map: Record<string, string> = { unused: '未使用', used: '已使用', expired: '已过期' }
  return map[s] || s
}

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString()
}

async function load() {
  loading.value = true
  try {
    list.value = await listCoupons()
  } finally {
    loading.value = false
  }
}

async function doSearch() {
  loading.value = true
  try {
    // 优惠券列表本身不支持关键词,前端按标题过滤
    const all = await listCoupons()
    const q = searchQuery.value.trim()
    list.value = q ? all.filter((c) => c.title.includes(q) || String(c.user_id).includes(q)) : all
  } finally {
    loading.value = false
  }
}

async function openGrant() {
  Object.assign(form, { user_id: 0, title: '优惠券', amount: 20, expires_days: 30 })
  grantQuery.value = ''
  await doGrantSearch()
  formVisible.value = true
}

async function doGrantSearch() {
  grantUsers.value = await searchUsers(grantQuery.value)
}

async function save() {
  if (!form.user_id) {
    ElMessage.warning('请先搜索并选择用户')
    return
  }
  saving.value = true
  try {
    await grantCoupon(form)
    ElMessage.success('已发放')
    formVisible.value = false
    await load()
  } catch {
    /* 已提示 */
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
@import './op-shared.css';

.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.search-row input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #f0ebe6;
  border-radius: 10px;
  font-size: 14px;
  background: #fff;
}
.search-btn {
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  background: #a98b84;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}
.search-inline {
  display: flex;
  gap: 8px;
}
.search-inline input {
  flex: 1;
}
.mini-btn {
  padding: 10px 14px;
  border: none;
  border-radius: 8px;
  background: #a98b84;
  color: #fff;
  cursor: pointer;
}
.user-select {
  width: 100%;
  min-height: 110px;
  padding: 8px;
  border: 1px solid #f0ebe6;
  border-radius: 8px;
  background: #faf6f0;
  font-size: 14px;
}
</style>