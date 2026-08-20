<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import {
  grantCoupon,
  listCoupons,
  searchUsers,
  type AdminCoupon,
  type UserOption,
} from '@/api/admin'

const coupons = ref<AdminCoupon[]>([])
const dialogVisible = ref(false)
const users = ref<UserOption[]>([])
const form = ref({ user_id: 0, title: '优惠券', amount: 20, expires_days: 30 })
const searchQuery = ref('')

async function load() {
  coupons.value = await listCoupons()
}

async function search() {
  users.value = await searchUsers(searchQuery.value)
}

async function openGrant() {
  form.value = { user_id: 0, title: '优惠券', amount: 20, expires_days: 30 }
  searchQuery.value = ''
  users.value = []
  await search()
  dialogVisible.value = true
}

async function save() {
  if (!form.value.user_id) {
    ElMessage.warning('请选择用户')
    return
  }
  await grantCoupon(form.value)
  ElMessage.success('已发放')
  dialogVisible.value = false
  await load()
}

const statusMap: Record<string, string> = { unused: '未使用', used: '已使用', expired: '已过期' }

onMounted(load)
</script>

<template>
  <div>
    <div class="bar">
      <h3>优惠券管理</h3>
      <el-button type="primary" @click="openGrant">手动发放</el-button>
    </div>
    <el-table :data="coupons" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="title" label="券名" min-width="140" />
      <el-table-column prop="amount" label="面额(元)" width="100" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'unused' ? 'success' : 'info'">{{ statusMap[row.status] || row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="发放时间" width="160" />
    </el-table>

    <el-dialog v-model="dialogVisible" title="手动发放优惠券" width="420px">
      <el-form label-width="100px">
        <el-form-item label="搜索用户">
          <el-input v-model="searchQuery" placeholder="昵称/OpenID" @input="search" />
        </el-form-item>
        <el-form-item label="选择用户">
          <el-select v-model="form.user_id" filterable placeholder="选一个用户">
            <el-option v-for="u in users" :key="u.id" :label="`${u.nickname}(${u.phone || '无手机'})`" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="券名"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="面额(元)"><el-input-number v-model="form.amount" :min="1" :step="5" /></el-form-item>
        <el-form-item label="有效期(天)"><el-input-number v-model="form.expires_days" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">发放</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
</style>