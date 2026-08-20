const BASE_URL: string = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: Record<string, unknown>
  auth?: boolean // 是否需要带 token
}

export interface ApiResponse<T = unknown> {
  code: number
  data: T
}

class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(
  options: RequestOptions,
): Promise<T> {
  const token = uni.getStorageSync('access_token')
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (options.auth !== false && token) {
    header.Authorization = `Bearer ${token}`
  }

  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header,
      success: (res) => {
        const { statusCode } = res as unknown as { statusCode: number }
        if (statusCode >= 200 && statusCode < 300) {
          resolve(res.data as T)
        } else if (statusCode === 401) {
          // token 失效,清理并提示重新登录
          uni.removeStorageSync('access_token')
          uni.removeStorageSync('refresh_token')
          uni.showToast({ title: '登录已过期,请重新登录', icon: 'none' })
          reject(new ApiError('未登录', 401))
        } else {
          const detail = (res.data as { detail?: string })?.detail || '请求失败'
          uni.showToast({ title: detail, icon: 'none' })
          reject(new ApiError(detail, statusCode))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常,请稍后重试', icon: 'none' })
        reject(new ApiError(err.errMsg || '网络错误', -1))
      },
    })
  })
}

// 简化 get/post 封装
export const http = {
  get: <T>(url: string, auth = true) =>
    request<T>({ url, method: 'GET', auth }),
  post: <T>(url: string, data?: Record<string, unknown>, auth = true) =>
    request<T>({ url, method: 'POST', data, auth }),
  put: <T>(url: string, data?: Record<string, unknown>, auth = true) =>
    request<T>({ url, method: 'PUT', data, auth }),
}

export default request