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

interface RawResponse {
  statusCode: number
  data: unknown
  errMsg?: string
}

/** 发起一次原始请求(不处理状态码/刷新逻辑)。 */
function rawRequest(options: RequestOptions, header: Record<string, string>): Promise<RawResponse> {
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header,
      success: (res) => resolve(res as unknown as RawResponse),
      fail: (err) => {
        uni.showToast({ title: '网络异常,请稍后重试', icon: 'none' })
        reject(new ApiError(err.errMsg || '网络错误', -1))
      },
    })
  })
}

// 并发的多个 401 共享同一次 refresh,避免重复请求刷新接口
let refreshingPromise: Promise<boolean> | null = null

/** 用 refresh_token 换新 token;成功返回 true 并更新本地存储。 */
function tryRefreshToken(): Promise<boolean> {
  const refreshToken = uni.getStorageSync('refresh_token') as string
  if (!refreshToken) return Promise.resolve(false)
  if (refreshingPromise) return refreshingPromise

  refreshingPromise = new Promise<boolean>((resolve) => {
    uni.request({
      url: BASE_URL + '/auth/refresh',
      method: 'POST',
      data: { refresh_token: refreshToken },
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        const { statusCode } = res as unknown as RawResponse
        if (statusCode >= 200 && statusCode < 300) {
          const tokens = res.data as { access_token: string; refresh_token: string }
          uni.setStorageSync('access_token', tokens.access_token)
          uni.setStorageSync('refresh_token', tokens.refresh_token)
          resolve(true)
        } else {
          // refresh token 也失效:彻底退出登录态
          uni.removeStorageSync('access_token')
          uni.removeStorageSync('refresh_token')
          resolve(false)
        }
      },
      fail: () => resolve(false),
    })
  }).finally(() => {
    refreshingPromise = null
  })
  return refreshingPromise
}

async function request<T>(
  options: RequestOptions,
): Promise<T> {
  const buildHeader = (): Record<string, string> => {
    const header: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    const token = uni.getStorageSync('access_token')
    if (options.auth !== false && token) {
      header.Authorization = `Bearer ${token}`
    }
    return header
  }

  let resp: RawResponse
  try {
    resp = await rawRequest(options, buildHeader())
  } catch (err) {
    uni.showToast({ title: '网络异常,请稍后重试', icon: 'none' })
    throw err
  }

  // access_token 过期:自动静默刷新一次并重放(仅对需鉴权的请求)
  if (resp.statusCode === 401 && options.auth !== false) {
    const refreshed = await tryRefreshToken()
    if (refreshed) {
      try {
        resp = await rawRequest(options, buildHeader())
      } catch (err) {
        uni.showToast({ title: '网络异常,请稍后重试', icon: 'none' })
        throw err
      }
    }
  }

  const { statusCode } = resp
  if (statusCode >= 200 && statusCode < 300) {
    return resp.data as T
  }
  if (statusCode === 401) {
    // 刷新失败或重放仍 401:清理并提示重新登录
    uni.removeStorageSync('access_token')
    uni.removeStorageSync('refresh_token')
    uni.showToast({ title: '登录已过期,请重新登录', icon: 'none' })
    throw new ApiError('未登录', 401)
  }
  const detail = (resp.data as { detail?: string })?.detail || '请求失败'
  uni.showToast({ title: detail, icon: 'none' })
  throw new ApiError(detail, statusCode)
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