// CSV 导出工具(订单列表 / 排队列表)
import type { LocalOrder } from './types'

export function ordersToCsv(orders: LocalOrder[]): string {
  const header = ['序号', '客户微信名', '客户姓名', '猫咪名字', '下单时间', '排队定金', '制作定金', '尾款', '付款状态', '电话', '地址', '备注']
  const rows = orders.map((o, i) => [
    String(i + 1),
    o.wechatName || '',
    o.customerName,
    o.catName,
    formatDate(o.orderTime || o.createdAt),
    String(o.depositDue),
    String(o.makingDue),
    String(o.finalDue),
    statusText(o),
    o.phone || '',
    (o.address || '').replace(/[\r\n,]/g, ' '),
    (o.note || '').replace(/[\r\n,]/g, ' '),
  ])
  return [header, ...rows].map((r) => r.map(esc).join(',')).join('\r\n')
}

export function queueToCsv(orders: LocalOrder[], queueIndexFn: (id: string) => number): string {
  const header = ['排队编号', '客户姓名', '猫咪名字', '付款状态']
  const rows = orders
    .filter((o) => queueIndexFn(o.id) > 0)
    .map((o) => [String(queueIndexFn(o.id)), o.customerName, o.catName, statusText(o)])
  return [header, ...rows].map((r) => r.map(esc).join(',')).join('\r\n')
}

function esc(v: string): string {
  if (/[",\n]/.test(v)) return `"${v.replace(/"/g, '""')}"`
  return v
}

function statusText(o: LocalOrder): string {
  if (o.finalPaid) return '尾款已支付'
  if (o.makingPaid) return '制作定金已支付'
  if (o.depositPaid) return '排队定金已支付'
  return '未付款'
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/**
 * 触发 CSV 导出。
 * - Android WebView 壳:通过原生桥(window.exportCsv)写文件并唤起系统分享
 * - 浏览器/开发环境:blob 下载
 */
export function downloadCsv(filename: string, csv: string) {
  const content = '\ufeff' + csv
  const bridge = (window as unknown as Record<string, { postMessage(msg: string): void } | undefined>)
    .exportCsv
  if (bridge?.postMessage) {
    bridge.postMessage(`${filename}\u0000${content}`)
    return
  }
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}