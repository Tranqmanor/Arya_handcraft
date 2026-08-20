// Arya 聊天接口
import { http } from './request'

export interface ChatResult {
  reply: string
  intent: string
  call_master_hint: string
}

export function sendMessage(message: string) {
  return http.post<ChatResult>('/arya/chat', { message })
}

export function clearSessions() {
  return http.post<{ detail: string }>('/arya/sessions', {})
}