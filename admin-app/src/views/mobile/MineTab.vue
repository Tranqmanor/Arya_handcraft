<template>
  <div class="tab-page">
    <!-- 已登录(未登录被全局登录页拦截,不会进到这里) -->
    <div class="profile-card">
      <img class="avatar" :src="`${BASE}icons/default_avatar.png`" alt="头像" />
      <div class="profile-meta">
        <div class="nickname">{{ nickname || '管理员' }}</div>
        <button class="edit-btn" @click="editName">修改昵称</button>
      </div>
    </div>

    <!-- 当前总收入 -->
    <div class="income-box">
      <span class="income-label">当前总收入</span>
      <span class="income-value">¥{{ totalIncome }}</span>
    </div>

    <!-- 子菜单 -->
    <div class="menu-card">
      <div class="menu-item" @click="store.goto('manage')">
        <span class="menu-icon">🛠️</span><span class="menu-label">管理</span><span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="store.goto('stats')">
        <span class="menu-icon">📊</span><span class="menu-label">账单统计</span><span class="arrow">›</span>
      </div>
    </div>

    <button class="logout-btn" @click="logout">退出登录</button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { summarize } from '@/local/bills'
import { useAppStore } from '@/stores/app'


const store = useAppStore()
const BASE = import.meta.env.BASE_URL
const nickname = ref(localStorage.getItem('arya_admin_nickname') || '')

const totalIncome = computed(() => summarize(store.orders).totalReceived)

async function editName() {
  try {
    const { value } = await ElMessageBox.prompt('请输入昵称', '修改昵称', {
      inputValue: nickname.value,
      inputPattern: /^.{1,20}$/,
      inputErrorMessage: '1-20 个字符',
    })
    nickname.value = value
    localStorage.setItem('arya_admin_nickname', value)
  } catch {
    /* 取消 */
  }
}

function logout() {
  store.logout()
  ElMessage.success('已退出登录')
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

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 28px 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 10vh;
}
.login-title {
  text-align: center;
  font-size: 17px;
  font-weight: 600;
  color: #5a5350;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field label {
  font-size: 12px;
  color: #7a716d;
}
.field input {
  padding: 12px 14px;
  border: 1px solid #f0ebe6;
  border-radius: 10px;
  font-size: 14px;
  background: #faf6f0;
}
.login-btn {
  margin-top: 6px;
  padding: 13px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.login-tip {
  text-align: center;
  font-size: 12px;
  color: #b9b1ac;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 18px;
  background: #fff;
  border-radius: 16px;
  padding: 24px 22px;
}
.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  background: #f0ebe6;
  display: block;
}
.profile-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.nickname {
  font-size: 18px;
  font-weight: 600;
  color: #5a5350;
}
.edit-btn {
  align-self: flex-start;
  background: #faf6f0;
  border: none;
  border-radius: 999px;
  padding: 5px 14px;
  font-size: 12px;
  color: #a98b84;
  cursor: pointer;
}

.income-box {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}
.income-label {
  font-size: 14px;
  opacity: 0.9;
}
.income-value {
  font-size: 26px;
  font-weight: 700;
}

.menu-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 17px 20px;
  border-bottom: 1px solid #f5f0eb;
  cursor: pointer;
}
.menu-item:last-child {
  border-bottom: none;
}
.menu-icon {
  font-size: 20px;
}
.menu-label {
  flex: 1;
  color: #5a5350;
  font-size: 15px;
  font-weight: 500;
}
.arrow {
  color: #d9cfc9;
  font-size: 20px;
}

.logout-btn {
  margin-top: 8px;
  width: 100%;
  padding: 13px;
  border: 1px solid #e5ded8;
  border-radius: 10px;
  background: #fff;
  color: #a98b84;
  font-size: 15px;
  cursor: pointer;
}
</style>
