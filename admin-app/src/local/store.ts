// 本地订单存储(localStorage 持久化)
import type { LocalOrder } from './types'

const KEY = 'arya_admin_app_orders'

export function loadOrders(): LocalOrder[] {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    return JSON.parse(raw) as LocalOrder[]
  } catch {
    return []
  }
}

export function saveOrders(orders: LocalOrder[]) {
  localStorage.setItem(KEY, JSON.stringify(orders))
}

function genId(): string {
  return `O-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`
}

export function nowIso(): string {
  return new Date().toISOString()
}

/** 新建订单(自动填 id/createdAt) */
export function createLocalOrder(partial: Omit<LocalOrder, 'id' | 'createdAt'>): LocalOrder {
  return { ...partial, id: genId(), createdAt: nowIso() }
}

/** 删除订单 */
export function deleteLocalOrder(orders: LocalOrder[], id: string): LocalOrder[] {
  return orders.filter((o) => o.id !== id)
}

/** 更新订单 */
export function updateLocalOrder(orders: LocalOrder[], updated: LocalOrder): LocalOrder[] {
  return orders.map((o) => (o.id === updated.id ? updated : o))
}

/**
 * 排队列表:付款状态 ∈ {排队定金已付, 制作定金已付} 且尾款未付。
 * 排序:手动 queueNo 优先,否则按 createdAt 升序。
 * 即「尾款已支付即出队,后续自动进位」。
 */
export function queuedOrders(orders: LocalOrder[]): LocalOrder[] {
  return orders
    .filter((o) => (o.depositPaid || o.makingPaid) && !o.finalPaid)
    .sort((a, b) => sortKey(a) - sortKey(b))
}

/** 排队/列表排序时间:优先客户下单时间,回退录入时间 */
export function timeMs(o: LocalOrder): number {
  return o.orderTime ? Date.parse(o.orderTime) : Date.parse(o.createdAt)
}

function sortKey(o: LocalOrder): number {
  if (o.queueNo != null && o.queueNo > 0) return o.queueNo
  return timeMs(o)
}

/** 该订单在队列中的编号(从 1 起);不在队返回 0 */
export function queueIndexOf(orders: LocalOrder[], id: string): number {
  return queuedOrders(orders).findIndex((o) => o.id === id) + 1
}