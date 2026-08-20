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
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  },
)

export default http
