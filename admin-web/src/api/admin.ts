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

// ===== 轮播图管理 =====
export interface AdminCarouselImage {
  id: number
  image_url: string
  title: string
  description: string
  sort_order: number
  is_published: boolean
  created_at: string
}

export function listCarouselImages() {
  return http.get('/admin/carousel') as Promise<AdminCarouselImage[]>
}
export function createCarouselImage(data: Partial<AdminCarouselImage>) {
  return http.post('/admin/carousel', data) as Promise<AdminCarouselImage>
}
export function updateCarouselImage(id: number, data: Partial<AdminCarouselImage>) {
  return http.put(`/admin/carousel/${id}`, data) as Promise<AdminCarouselImage>
}
export function deleteCarouselImage(id: number) {
  return http.delete(`/admin/carousel/${id}`) as Promise<{ detail: string }>
}

// ===== 订单管理 =====
export interface AdminOrder {
  id: number
  order_no: string
  status: string
  status_label: string
  cat_name: string
  user_nickname: string
  user_phone: string | null
  total_price: number | null
  deposit_due: number
  making_due: number
  final_due: number
  paid_deposit: number
  paid_making: number
  paid_final: number
  address: { receiver?: string; phone?: string; region?: string; detail?: string }
  images: string[]
  cover_image_url: string
  referrer_user_id: number | null
  queue_no: number
  created_at: string
  requirement?: string
  making_photos?: string[]
  shipping_company?: string
  tracking_no?: string
  price_note?: string
  refund_reason?: string
  refund_amount?: number
  cancel_reason?: string
  coupon_id?: number | null
  coupon_amount?: number
}

export function listAdminOrders(params?: { status?: string; q?: string }) {
  return http.get('/admin/orders', { params }) as Promise<AdminOrder[]>
}

export function getAdminOrder(id: number) {
  return http.get(`/admin/orders/${id}`) as Promise<AdminOrder>
}

export function setOrderPrice(id: number, data: { total_price: number; note?: string }) {
  return http.put(`/admin/orders/${id}/price`, data) as Promise<AdminOrder>
}

export function confirmOrderPayment(id: number, data: { stage: string; amount: number; note?: string }) {
  return http.put(`/admin/orders/${id}/confirm-payment`, data) as Promise<AdminOrder>
}

export function startOrderMaking(id: number) {
  return http.put(`/admin/orders/${id}/start-making`, {}) as Promise<AdminOrder>
}

export function finishOrderMaking(id: number) {
  return http.put(`/admin/orders/${id}/finish-making`, {}) as Promise<AdminOrder>
}

export function setOrderMakingPhotos(id: number, photos: string[]) {
  return http.put(`/admin/orders/${id}/making-photos`, { photos }) as Promise<AdminOrder>
}

export function setOrderCover(id: number, image_url: string) {
  return http.put(`/admin/orders/${id}/set-cover`, { image_url }) as Promise<AdminOrder>
}

export function shipOrder(id: number, data: { shipping_company: string; tracking_no: string }) {
  return http.put(`/admin/orders/${id}/ship`, data) as Promise<AdminOrder>
}

export function refundOrder(id: number, data: { amount: number; reason?: string }) {
  return http.put(`/admin/orders/${id}/refund`, data) as Promise<AdminOrder>
}

export function cancelAdminOrder(id: number, reason = '') {
  return http.put(`/admin/orders/${id}/cancel`, { reason }) as Promise<AdminOrder>
}

export function reopenOrder(id: number) {
  return http.put(`/admin/orders/${id}/reopen`, {}) as Promise<AdminOrder>
}

// ===== 首页配置 =====
export function getHomeSettings() {
  return http.get('/admin/home-settings') as Promise<{ promo_image_url: string }>
}

export function updateHomeSettings(promo_image_url: string) {
  return http.put('/admin/home-settings', { promo_image_url }) as Promise<{ promo_image_url: string }>
}

// ===== 账目统计 =====
export interface FinanceStats {
  order_count_by_status: Record<string, number>
  received: { deposit: number; making: number; final: number; total: number }
  refunded_total: number
  net_total: number
  pending_amount: number
  monthly: { month: string; income: number; refund: number; net: number }[]
}

export function getFinance() {
  return http.get('/admin/stats/finance') as Promise<FinanceStats>
}

// ===== 图片/视频上传(文章配图、封面、正文视频) =====
export function uploadImage(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  // axios 遇 FormData 自动使用 multipart 边界,勿手动覆盖 Content-Type
  return http.post('/admin/uploads/image', fd, { timeout: 60000 }) as Promise<{ url: string }>
}

/** 上传视频(≤200MB),onProgress 回调上传百分比;超时放宽至 10 分钟 */
export function uploadVideo(file: File, onProgress?: (percent: number) => void) {
  const fd = new FormData()
  fd.append('file', file)
  return http.post('/admin/uploads/video', fd, {
    timeout: 600000,
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  }) as Promise<{ url: string }>
}