import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 15000,
})

// 请求拦截:附加 token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截:统一错误提示
http.interceptors.response.use(
  (resp) => resp.data,
  (error) => {
    // 登录态失效:清理 token 并跳回登录页(登录接口本身的 401 除外)
    if (
      error.response?.status === 401 &&
      !String(error.config?.url || '').includes('/admin/auth/login')
    ) {
      localStorage.removeItem('admin_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  },
)

export default http
