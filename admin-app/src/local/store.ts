// 本地订单存储(localStorage 持久化)
import type { LocalOrder } from './types'

const KEY = 'arya_admin_app_orders'

export function loadOrders(): LocalOrder[] {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    const arr = JSON.parse(raw) as LocalOrder[]
    let migrated = false
    const out = arr.map((o) => {
      const r = normalizeOrder(o)
      if (r !== o) migrated = true
      return r
    })
    if (migrated) localStorage.setItem(KEY, JSON.stringify(out))
    return out
  } catch {
    return []
  }
}

/** 旧三阶段数据 → 两阶段模型:制作定金并入尾款,单图升为图列表 */
function normalizeOrder(o: LocalOrder): LocalOrder {
  const any = o as unknown as Record<string, unknown>
  const hasLegacy = any.makingDue != null || any.makingPaid != null || any.catPhoto != null
  if (!hasLegacy) return o
  const makDue = Number(any.makingDue) || 0
  const makPaid = any.makingPaid === true
  const next = {
    ...o,
    depositPaid: !!o.depositPaid || makPaid,
    finalDue: (Number(o.finalDue) || 0) + makDue,
  } as Record<string, unknown>
  if (typeof any.catPhoto === 'string' && any.catPhoto) {
    next.catPhotos = [any.catPhoto, ...(Array.isArray(o.catPhotos) ? o.catPhotos : [])]
  }
  delete next.makingDue
  delete next.makingPaid
  delete next.catPhoto
  return next as unknown as LocalOrder
}

export function saveOrders(orders: LocalOrder[]) {
  localStorage.setItem(KEY, JSON.stringify(orders))
}

export function nowIso(): string {
  return new Date().toISOString()
}

/** 新建订单(自动填 id/createdAt) */
export function createLocalOrder(partial: Omit<LocalOrder, 'id' | 'createdAt'>): LocalOrder {
  return { ...partial, id: genId(), createdAt: nowIso() }
}

/** 生成订单 id */
export function genId(): string {
  return `O-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`
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
 * 排队列表:定金已付且尾款未付。
 * 排序:手动 queueNo 优先,否则按下单时间升序。
 * 即「尾款已支付即出队,后面订单自动进位」。
 */
export function queuedOrders(orders: LocalOrder[]): LocalOrder[] {
  return orders
    .filter((o) => o.depositPaid && !o.finalPaid)
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