// 本地账单统计(纯函数,基于订单数组计算)
import type { LocalOrder } from './types'

export interface BillSummary {
  totalReceived: number // 三款项已收总和
  depositReceived: number
  makingReceived: number
  finalReceived: number
}

export function summarize(orders: LocalOrder[]): BillSummary {
  let deposit = 0
  let making = 0
  let final = 0
  for (const o of orders) {
    if (o.depositPaid) deposit += o.depositDue
    if (o.makingPaid) making += o.makingDue
    if (o.finalPaid) final += o.finalDue
  }
  return {
    depositReceived: deposit,
    makingReceived: making,
    finalReceived: final,
    totalReceived: deposit + making + final,
  }
}

export interface CustomerRow {
  orderId: string
  customerName: string
}

/** 指定阶段已付款的客户列表(账单钻取用) */
export function customersWith(orders: LocalOrder[], stage: 'deposit' | 'making' | 'final'): CustomerRow[] {
  return orders
    .filter((o) => (stage === 'deposit' ? o.depositPaid : stage === 'making' ? o.makingPaid : o.finalPaid))
    .map((o) => ({ orderId: o.id, customerName: o.customerName }))
}