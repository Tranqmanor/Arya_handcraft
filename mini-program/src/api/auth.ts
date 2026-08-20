// 认证相关接口
import { http } from './request'

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserInfo {
  id: number
  openid: string
  unionid: string | null
  nickname: string
  avatar_url: string
  phone: string | null
  created_at: string
  updated_at: string
}

export interface CouponItem {
  id: number
  title: string
  amount: number
  status: string
  expires_at: string | null
  used_at: string | null
  created_at: string
}

export function loginWithCode(code: string) {
  return http.post<TokenResponse>('/auth/login', { code }, false)
}

export function getMe() {
  return http.get<UserInfo>('/users/me')
}

export function updateMe(data: Partial<Pick<UserInfo, 'nickname' | 'avatar_url' | 'phone'>>) {
  return http.put<UserInfo>('/users/me', data)
}

export function getMyCoupons() {
  return http.get<CouponItem[]>('/users/me/coupons')
}