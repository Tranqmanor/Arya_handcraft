// 本地订单模型(后台管理 App 手动录入)
export type PaymentStatus = 'deposit_paid' | 'making_paid' | 'final_paid' | 'none'

export interface LocalOrder {
  id: string
  /** 录入时间(ISO,用作队列基础排序) */
  createdAt: string
  totalPrice?: number
  /** 客户微信名(必填,首页排队展示用) */
  wechatName?: string
  /** 客户自行下单时间(ISO,必填;排队排序依据,补录旧单可排到正确位置) */
  orderTime?: string
  /** 手动编辑的排队号(可为空,留空则按录入顺序自动编号) */
  queueNo?: number

  /** 客户姓名(选填) */
  customerName: string
  catName: string
  phone?: string
  address?: string
  requirement?: string

  /** 三阶段应付(元) */
  depositDue: number
  makingDue: number
  finalDue: number
  /** 三阶段已付标志(驱动排队/账单) */
  depositPaid: boolean
  makingPaid: boolean
  finalPaid: boolean

  note?: string
}

// 付款状态派生:由三阶段已付标志推出当前资金状态
export function paymentStatusOf(o: LocalOrder): PaymentStatus {
  if (o.finalPaid) return 'final_paid'
  if (o.makingPaid) return 'making_paid'
  if (o.depositPaid) return 'deposit_paid'
  return 'none'
}

export const PAYMENT_LABEL: Record<PaymentStatus, string> = {
  none: '未付款',
  deposit_paid: '排队定金已支付',
  making_paid: '制作定金已支付',
  final_paid: '尾款已支付',
}

export const PAYMENT_COLOR: Record<PaymentStatus, string> = {
  none: '#b9b1ac',
  deposit_paid: '#a98b84',
  making_paid: '#9fb0b5',
  final_paid: '#6a9955',
}