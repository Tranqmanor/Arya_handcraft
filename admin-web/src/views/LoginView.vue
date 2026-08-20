<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminLogin } from '@/api/admin'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    // eslint-disable-next-line no-alert
    window.alert('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await adminLogin(username.value, password.value)
    localStorage.setItem('admin_token', res.access_token)
    router.push('/dashboard')
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="title">Arya_handcraft 管理后台</h2>
      <el-form label-position="top" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" show-password placeholder="请输入密码" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="loading" @click="handleLogin">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #faf6f0, #eadcd9);
}
.login-card {
  width: 380px;
  border-radius: 16px;
}
.title {
  text-align: center;
  color: #a98b84;
  margin: 8px 0 24px;
}
.submit {
  width: 100%;
}
</style>
