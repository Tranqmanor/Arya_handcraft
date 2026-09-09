// 本地账单统计(纯函数,基于订单数组计算)
// 两阶段模型:定金 → 尾款。
//   已完成订单(finalPaid)：计订单总价;
//   定金已付未尾款(depositPaid)：定金计入收入,尾款挂「未支付尾款」;
//   总收入 = 已完成订单总价之和 + 已付定金订单的定金之和。
import type { LocalOrder } from './types'

/** 账单视图:已支付定金 / 已完成订单 / 未支付尾款 */
export type BillView = 'deposit' | 'completed' | 'unpaid_final'

export const BILL_VIEW_LABEL: Record<BillView, string> = {
  deposit: '已支付定金',
  completed: '已完成订单',
  unpaid_final: '未支付尾款',
}

/** 订单总价 = 定金 + 尾款 */
export function orderTotal(o: LocalOrder): number {
  return (Number(o.depositDue) || 0) + (Number(o.finalDue) || 0)
}

function inDepositStage(o: LocalOrder): boolean {
  return o.depositPaid && !o.finalPaid
}

export interface BillRow {
  orderId: string
  customerName: string
  amount: number
}

/** 视图对应的订单行(微信名 + 阶段金额) */
export function billRows(orders: LocalOrder[], view: BillView): BillRow[] {
  const rows: BillRow[] = []
  for (const o of orders) {
    let amount: number | null = null
    if (view === 'completed' && o.finalPaid) amount = orderTotal(o)
    else if (view === 'deposit' && inDepositStage(o)) amount = Number(o.depositDue) || 0
    else if (view === 'unpaid_final' && inDepositStage(o)) amount = Number(o.finalDue) || 0
    if (amount != null) {
      rows.push({ orderId: o.id, customerName: o.wechatName || o.customerName || '—', amount })
    }
  }
  return rows
}

export function billTotal(orders: LocalOrder[], view: BillView): number {
  return billRows(orders, view).reduce((acc, r) => acc + r.amount, 0)
}

/** 总收入 = 已完成订单总价之和 + 已支付定金订单的定金之和 */
export function totalReceived(orders: LocalOrder[]): number {
  return billTotal(orders, 'completed') + billTotal(orders, 'deposit')
}