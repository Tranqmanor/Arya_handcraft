<script setup lang="ts">
// 全局登录门禁:未登录时唯一可见页面
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'
import { adminLogin } from '@/api/online'

const store = useAppStore()
const BASE = import.meta.env.BASE_URL
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
    <!-- 品牌头部卡片 -->
    <div class="brand-card">
      <img :src="`${BASE}icons/logo.png`" alt="Arya手作" />
      <div class="brand-text">
        <b>Arya手作管理端</b>
        <span>订单 · 排队 · 账单</span>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-title">管理员登录</div>
      <div class="field-row">
        <label>账号</label>
        <input v-model="loginUser" placeholder="admin" />
      </div>
      <div class="field-row">
        <label>密码</label>
        <input v-model="loginPass" type="password" placeholder="请输入密码" @keyup.enter="doLogin" />
      </div>
      <p class="login-tip">首次使用:输入的密码即成为本机管理密码;若已开通在线后台,请使用后台账号密码。</p>
      <button class="btn btn-primary" @click="doLogin">进入管理</button>
    </div>
  </div>
</template>

<style scoped>
/* 整屏上下左右居中,两张卡片间距拉开 */
.login-page {
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 56px;
  padding: 24px 32px calc(32px + env(safe-area-inset-bottom));
}

/* 1. 品牌头部卡片 */
.brand-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  border-radius: 22px;
  padding: 26px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  box-shadow: 0 6px 24px rgba(169, 139, 132, 0.12);
}
.brand-card img {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  object-fit: cover;
  display: block;
}
.brand-text b {
  display: block;
  font-size: 20px;
  color: #5a5350;
  letter-spacing: 1px;
}
.brand-text span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #b9b1ac;
}

/* 2. 登录卡片 */
.login-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  border-radius: 22px;
  padding: 26px 24px;
  box-shadow: 0 6px 24px rgba(169, 139, 132, 0.12);
}
.login-title {
  text-align: center;
  font-size: 17px;
  font-weight: 600;
  color: #5a5350;
  margin-bottom: 18px;
}
.field-row {
  margin-bottom: 14px;
}
.field-row label {
  display: block;
  font-size: 12px;
  color: #7a716d;
  margin-bottom: 5px;
}
.field-row input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #f0ebe6;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  background: #faf6f0;
  box-sizing: border-box;
}
.field-row input:focus {
  border-color: #c9a9a6;
  background: #fff;
}
.login-tip {
  font-size: 11px;
  color: #b9b1ac;
  line-height: 1.6;
  margin: 2px 0 16px;
}
.btn {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary {
  background: linear-gradient(160deg, #c9a9a6, #a98b84);
  color: #fff;
}
.btn-primary:active {
  opacity: 0.85;
}
</style>