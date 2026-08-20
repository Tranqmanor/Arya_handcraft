import http from './http'

// 管理员登录
export function adminLogin(username: string, password: string) {
  return http.post('/admin/auth/login', { username, password }) as Promise<{
    access_token: string
    token_type: string
  }>
}

// 概览统计
export function getSummary() {
  return http.get('/admin/stats/summary') as Promise<{
    user_count: number
    video_count: number
    article_count: number
    total_views: number
    coupon_count: number
    unused_coupon_count: number
  }>
}

// ===== 视频管理 =====
export interface AdminVideo {
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
  return http.get('/admin/videos') as Promise<AdminVideo[]>
}
export function createVideo(data: Partial<AdminVideo>) {
  return http.post('/admin/videos', data) as Promise<AdminVideo>
}
export function updateVideo(id: number, data: Partial<AdminVideo>) {
  return http.put(`/admin/videos/${id}`, data) as Promise<AdminVideo>
}
export function deleteVideo(id: number) {
  return http.delete(`/admin/videos/${id}`) as Promise<{ detail: string }>
}

// ===== 文章管理 =====
export interface AdminArticle {
  id: number
  title: string
  summary: string
  cover_url: string
  content: string
  category: string
  view_count: number
  is_published: boolean
  sort_order: number
}

export function listArticles() {
  return http.get('/admin/articles') as Promise<AdminArticle[]>
}
export function createArticle(data: Partial<AdminArticle>) {
  return http.post('/admin/articles', data) as Promise<AdminArticle>
}
export function updateArticle(id: number, data: Partial<AdminArticle>) {
  return http.put(`/admin/articles/${id}`, data) as Promise<AdminArticle>
}
export function deleteArticle(id: number) {
  return http.delete(`/admin/articles/${id}`) as Promise<{ detail: string }>
}

// ===== 优惠券 =====
export interface AdminCoupon {
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
  return http.get('/admin/coupons', { params: { user_id: userId } }) as Promise<AdminCoupon[]>
}
export function grantCoupon(data: { user_id: number; title: string; amount: number; expires_days?: number }) {
  return http.post('/admin/coupons/grant', data) as Promise<AdminCoupon>
}
export function searchUsers(q = '') {
  return http.get('/admin/coupons/users', { params: { q } }) as Promise<UserOption[]>
}