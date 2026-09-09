<script setup lang="ts">
// 全局登录门禁:未登录时唯一可见页面
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'
import { adminLogin } from '@/api/online'
import aryapng from '@/assets/aryapng.png'

const store = useAppStore()
const loginUser = ref('admin')
const loginPass = ref('')

async function doLogin() {
  const saved = localStorage.getItem('arya_admin_pass')
  if (!saved) {
    if (!loginPass.value) {
      ElMessage.warning('首次使用:请先输入作为本机管理密码')
      return
    }
    localStorage.setItem('arya_admin_pass', loginPass.value)
    store.login()
    ElMessage.success('已设置管理密码并登录(首次)')
    tryOnlineLogin(loginPass.value)
    return
  }
  if (loginUser.value === 'admin' && loginPass.value === saved) {
    store.login()
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
    ElMessage.info('在线模块未登录(密码与后台不一致或网络不可用),本地功能不受影响')
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-brand">
      <img :src="aryapng" alt="Arya手作" />
      <div>
        <b>Arya手作管理端</b>
        <span>订单 · 排队 · 账单</span>
      </div>
    </div>

    <div class="login-card">
      <div class="login-title">管理员登录</div>
      <div class="field-row"><label>账号</label><input v-model="loginUser" placeholder="admin" /></div>
      <div class="field-row"><label>密码</label><input v-model="loginPass" type="password" placeholder="请输入密码" @keyup.enter="doLogin" /></div>
      <p class="login-tip">首次使用:输入的密码即成为本机管理密码;若已登录在线后台,密码与在线后台一致。</p>
      <button class="btn btn-primary" @click="doLogin">进入管理</button>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  padding: calc(40px + var(--safe-top)) 16px 24px;
}
.login-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
}
.login-brand img {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  object-fit: cover;
}
.login-brand b {
  display: block;
  font-size: 18px;
}
.login-brand span {
  display: block;
  font-size: 12px;
  color: var(--muted);
}
.login-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
}
.login-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}
.field-row {
  margin-bottom: 10px;
}
.field-row label {
  display: block;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 4px;
}
.field-row input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: #fff;
}
.field-row input:focus {
  border-color: var(--primary);
}
.login-tip {
  font-size: 11px;
  color: var(--muted);
  margin: 4px 0 12px;
  line-height: 1.5;
}
.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary {
  background: var(--primary);
  color: #fff;
}
</style>