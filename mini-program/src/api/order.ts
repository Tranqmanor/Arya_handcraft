// 订单/地址/上传相关接口
import { BASE_URL, http } from './request'

// ---------- 类型 ----------

export interface OrderListItem {
  id: number
  order_no: string
  cat_name: string
  status: string
  status_label: string
  total_price: number | null
  deposit_due: number
  making_due: number
  final_due: number
  paid_deposit: number
  paid_making: number
  paid_final: number
  cover_image_url: string
  queue_no: number
  created_at: string
}

export interface OrderDetail extends OrderListItem {
  images: string[]
  requirement: string
  address: { receiver?: string; phone?: string; region?: string; detail?: string }
  making_photos: string[]
  shipping_company: string
  tracking_no: string
  price_note: string
  refund_reason: string
  refund_amount: number
  cancel_reason: string
  coupon_amount: number
}

export interface AddressItem {
  id: number
  receiver: string
  phone: string
  region: string
  detail: string
  is_default: boolean
  created_at: string
}

export interface WorkItem {
  cat_name: string
  cover_image_url: string
  completed_at: string | null
}

// ---------- 订单 ----------

export function createOrder(payload: {
  cat_name: string
  images: string[]
  address_id: number
  requirement?: string
  coupon_id?: number
  referrer_user_id?: number
}) {
  return http.post<OrderListItem>('/orders', payload)
}

export function getMyOrders() {
  return http.get<OrderListItem[]>('/orders')
}

export function getOrderDetail(id: number) {
  return http.get<OrderDetail>(`/orders/${id}`)
}

export function cancelOrder(id: number, reason = '') {
  return http.post<OrderListItem>(`/orders/${id}/cancel?reason=${encodeURIComponent(reason)}`, {})
}

export function requestOrderRefund(id: number, reason = '') {
  return http.post<OrderListItem>(`/orders/${id}/refund-request?reason=${encodeURIComponent(reason)}`, {})
}

export function confirmReceive(id: number) {
  return http.post<OrderListItem>(`/orders/${id}/confirm-receive`, {})
}

// ---------- 地址簿 ----------

export function getAddresses() {
  return http.get<AddressItem[]>('/addresses')
}

export function createAddress(payload: Omit<AddressItem, 'id' | 'created_at'>) {
  return http.post<AddressItem>('/addresses', payload)
}

export function updateAddress(id: number, payload: Omit<AddressItem, 'id' | 'created_at'>) {
  return http.put<AddressItem>(`/addresses/${id}`, payload)
}

export function deleteAddress(id: number) {
  return http.post<{ detail: string }>(`/addresses/${id}/delete`, {})
}

// 便捷删除(DELETE 语义)
export function removeAddress(id: number) {
  return http.delete<{ detail: string }>(`/addresses/${id}`)
}

// ---------- 公开内容 ----------

export function getWorks() {
  return http.get<WorkItem[]>('/works', false)
}

export function getHomeSettings() {
  return http.get<{ promo_image_url: string }>('/home-settings', false)
}

// ---------- 用户图片上传 ----------

export function uploadUserImage(filePath: string): Promise<{ url: string }> {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: BASE_URL + '/user/uploads/image',
      filePath,
      name: 'file',
      header: { Authorization: `Bearer ${uni.getStorageSync('access_token') || ''}` },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(res.data) as { url: string })
          } catch {
            reject(new Error('响应解析失败'))
          }
        } else {
          let detail = '上传失败'
          try {
            detail = (JSON.parse(res.data) as { detail?: string }).detail || detail
          } catch {
            /* ignore */
          }
          uni.showToast({ title: detail, icon: 'none' })
          reject(new Error(detail))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常,请稍后重试', icon: 'none' })
        reject(new Error(err.errMsg))
      },
    })
  })
}