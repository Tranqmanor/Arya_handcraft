// 在线 API 客户端(axios):与 admin-web 同协议
// - token 存 localStorage('admin_token')
// - 401 时清除并提示重新登录
import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (resp) => resp.data,
  (error) => {
    const status = error.response?.status
    const detail: string = error.response?.data?.detail || '请求失败'
    if (status === 401) {
      localStorage.removeItem('admin_token')
      ElMessage.warning('在线登录已过期,请在「我的」重新登录')
    } else {
      ElMessage.error(detail)
    }
    return Promise.reject(error)
  },
)

export default http