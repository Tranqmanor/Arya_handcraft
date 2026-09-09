// 本地账单统计(纯函数,基于订单数组计算)
// 规则:一个订单只归属其「当前付款阶段」一个列表;
//   金额为该阶段及之前各期累计应付之和(如制作定金阶段 = 排队定金 + 制作定金)。
import type { LocalOrder } from './types'

export type BillStage = 'deposit' | 'making' | 'final'

/** 订单当前所处阶段(尾款 > 制作 > 排队;未付款返回 null) */
export function currentStage(o: LocalOrder): BillStage | null {
  if (o.finalPaid) return 'final'
  if (o.makingPaid) return 'making'
  if (o.depositPaid) return 'deposit'
  return null
}

/** 累计已收金额 = 已付各期应付之和 */
export function paidAmountOf(o: LocalOrder): number {
  let sum = 0
  if (o.depositPaid) sum += o.depositDue
  if (o.makingPaid) sum += o.makingDue
  if (o.finalPaid) sum += o.finalDue
  return sum
}

export interface BillSummary {
  totalReceived: number
  depositReceived: number
  makingReceived: number
  finalReceived: number
}

function stageSum(orders: LocalOrder[], stage: BillStage): number {
  return orders.reduce((acc, o) => acc + (currentStage(o) === stage ? paidAmountOf(o) : 0), 0)
}

export function summarize(orders: LocalOrder[]): BillSummary {
  const depositReceived = stageSum(orders, 'deposit')
  const makingReceived = stageSum(orders, 'making')
  const finalReceived = stageSum(orders, 'final')
  return {
    depositReceived,
    makingReceived,
    finalReceived,
    totalReceived: depositReceived + makingReceived + finalReceived,
  }
}

export interface CustomerRow {
  orderId: string
  customerName: string
  amount: number
}

/** 指定阶段列表:当前阶段恰为该阶段的订单(不重复计入其他阶段) */
export function customersWith(orders: LocalOrder[], stage: BillStage): CustomerRow[] {
  return orders
    .filter((o) => currentStage(o) === stage)
    .map((o) => ({
      orderId: o.id,
      customerName: o.wechatName || o.customerName,
      amount: paidAmountOf(o),
    }))
}