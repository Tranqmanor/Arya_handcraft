// 在线模块接口:文章/视频/轮播/优惠券(移动端精简版)
// 复用现有 FastAPI 后端协议,与 admin-web 一致
import http from './http'

// ---------- 登录 ----------
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export function adminLogin(username: string, password: string) {
  return http.post<never, TokenResponse>('/admin/auth/login', { username, password })
}

// ---------- 文章 ----------
export interface OnlineArticle {
  id: number
  title: string
  summary: string
  cover_url: string
  category: string
  content: string
  view_count: number
  is_published: boolean
  sort_order: number
}

export function listArticles() {
  return http.get<never, OnlineArticle[]>('/admin/articles')
}

export function createArticle(data: Partial<OnlineArticle>) {
  return http.post<never, OnlineArticle>('/admin/articles', data)
}

export function updateArticle(id: number, data: Partial<OnlineArticle>) {
  return http.put<never, OnlineArticle>(`/admin/articles/${id}`, data)
}

export function deleteArticle(id: number) {
  return http.delete<never, { detail: string }>(`/admin/articles/${id}`)
}

// ---------- 视频 ----------
export interface OnlineVideo {
  id: number
  title: string
  description: string
  video_url: string
  cover_url: string
  duration: number
  view_count: number
  is_published: boolean
  sort_order: number
}

export function listVideos() {
  return http.get<never, OnlineVideo[]>('/admin/videos')
}

export function createVideo(data: Partial<OnlineVideo>) {
  return http.post<never, OnlineVideo>('/admin/videos', data)
}

export function deleteVideo(id: number) {
  return http.delete<never, { detail: string }>(`/admin/videos/${id}`)
}

// ---------- 轮播图 ----------
export interface OnlineCarousel {
  id: number
  image_url: string
  title: string
  description: string
  is_published: boolean
  sort_order: number
}

export function listCarousel() {
  return http.get<never, OnlineCarousel[]>('/admin/carousel')
}

export function createCarousel(data: Partial<OnlineCarousel>) {
  return http.post<never, OnlineCarousel>('/admin/carousel', data)
}

export function deleteCarousel(id: number) {
  return http.delete<never, { detail: string }>(`/admin/carousel/${id}`)
}

// ---------- 优惠券 ----------
export interface OnlineCoupon {
  id: number
  user_id: number
  title: string
  amount: number
  status: string
  created_at: string
}

export interface UserOption {
  id: number
  nickname: string
  phone: string | null
}

export function listCoupons(userId?: number) {
  return http.get<never, OnlineCoupon[]>('/admin/coupons', {
    params: userId ? { user_id: userId } : undefined,
  }) as Promise<OnlineCoupon[]>
}

export function searchUsers(q = '') {
  return http.get<never, UserOption[]>('/admin/coupons/users', { params: { q } })
}

export function grantCoupon(data: { user_id: number; title: string; amount: number; expires_days?: number }) {
  return http.post<never, OnlineCoupon>('/admin/coupons/grant', data)
}

// ---------- 图片/视频上传(multipart → R2) ----------

export function uploadImage(file: File, onProgress?: (p: number) => void): Promise<{ url: string }> {
  const fd = new FormData()
  fd.append('file', file)
  return http.post<never, { url: string }>('/admin/uploads/image', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
}

export function uploadVideo(file: File, onProgress?: (p: number) => void): Promise<{ url: string }> {
  const fd = new FormData()
  fd.append('file', file)
  return http.post<never, { url: string }>('/admin/uploads/video', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000,
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
}