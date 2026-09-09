<template>
  <div class="tab-page">
    <!-- 未登录 -->
    <div v-if="!loggedIn" class="login-card">
      <div class="login-title">管理员登录</div>
      <div class="field"><label>账号</label><input v-model="loginUser" placeholder="admin" /></div>
      <div class="field"><label>密码</label><input v-model="loginPass" type="password" placeholder="密码" @keyup.enter="doLogin" /></div>
      <button class="login-btn" @click="doLogin">登 录</button>
      <div class="login-tip">与后台管理网页账号密码一致</div>
    </div>

    <!-- 已登录 -->
    <template v-else>
      <!-- 头像区(点击可改昵称) -->
      <div class="profile-card">
        <div class="avatar">🐱</div>
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { adminLogin } from '@/api/online'
import { summarize } from '@/local/bills'
import { useAppStore } from '@/stores/app'


const store = useAppStore()
const loggedIn = ref(localStorage.getItem('arya_admin_logged') === '1')
const loginUser = ref('admin')
const loginPass = ref('')
const nickname = ref(localStorage.getItem('arya_admin_nickname') || '')

const totalIncome = computed(() => summarize(store.orders).totalReceived)

async function doLogin() {
  const saved = localStorage.getItem('arya_admin_pass')
  if (!saved) {
    // 首次登录:将输入的密码存为本地密码
    if (!loginPass.value) {
      ElMessage.warning('请输入密码')
      return
    }
    localStorage.setItem('arya_admin_pass', loginPass.value)
    localStorage.setItem('arya_admin_logged', '1')
    loggedIn.value = true
    ElMessage.success('已设为本地登录密码')
    tryOnlineLogin(loginPass.value)
    return
  }
  if (loginUser.value === 'admin' && loginPass.value === saved) {
    localStorage.setItem('arya_admin_logged', '1')
    loggedIn.value = true
    tryOnlineLogin(loginPass.value)
  } else {
    ElMessage.error('账号或密码错误')
  }
}

/** 双模式:本地校验通过后,静默尝试在线登录(在线模块需要 token) */
async function tryOnlineLogin(pass: string) {
  try {
    const res = await adminLogin('admin', pass)
    localStorage.setItem('admin_token', res.access_token)
    ElMessage.success('在线功能已同步登录')
  } catch {
    // 密码与后台不一致或网络不可用:仅提示,不阻塞本地功能
    ElMessage.info('在线模块未登录(密码与后台不一致或网络不可用),本地功能不受影响')
  }
}

function editName() {
  const name = prompt('请输入昵称', nickname.value)
  if (name != null) {
    nickname.value = name
    localStorage.setItem('arya_admin_nickname', name)
  }
}

function logout() {
  localStorage.setItem('arya_admin_logged', '0')
  localStorage.removeItem('admin_token')
  loggedIn.value = false
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
  background: linear-gradient(160deg, #eadcd9, #c9a9a6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
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
