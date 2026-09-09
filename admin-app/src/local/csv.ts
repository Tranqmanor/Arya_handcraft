// CSV 导出/导入工具(订单列表 / 排队列表)
import type { LocalOrder } from './types'
import { genId, nowIso } from './store'

/** 导出与导入共用的订单列头(列名一致即可识别,列顺序不限) */
export const ORDERS_CSV_HEADER = [
  '序号', '客户微信名', '客户姓名', '猫咪名字', '下单时间',
  '排队定金', '制作定金', '尾款', '付款状态', '电话', '地址', '备注',
]

export function ordersToCsv(orders: LocalOrder[]): string {
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
  return [ORDERS_CSV_HEADER, ...rows].map((r) => r.map(esc).join(',')).join('\r\n')
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

// ———— CSV 导入 ————

/** 标准 CSV 解析(支持引号包裹、字段内换行、BOM、\r\n) */
export function parseCsv(text: string): string[][] {
  const s = text.replace(/^\uFEFF/, '').replace(/\r\n/g, '\n').replace(/\r/g, '\n')
  const rows: string[][] = []
  let row: string[] = []
  let field = ''
  let inQuotes = false
  for (let i = 0; i < s.length; i++) {
    const c = s[i]
    if (inQuotes) {
      if (c === '"') {
        if (s[i + 1] === '"') {
          field += '"'
          i++
        } else {
          inQuotes = false
        }
      } else {
        field += c
      }
    } else if (c === '"') {
      inQuotes = true
    } else if (c === ',') {
      row.push(field)
      field = ''
    } else if (c === '\n') {
      row.push(field)
      rows.push(row)
      row = []
      field = ''
    } else {
      field += c
    }
  }
  if (field !== '' || row.length > 0) {
    row.push(field)
    rows.push(row)
  }
  return rows.filter((r) => r.some((f) => f.trim() !== ''))
}

/**
 * 从导出的 CSV 文本解析订单(按列名识别,列顺序不限;缺列给默认值)。
 * 识别失败(无「猫咪名字」「付款状态」列)返回空数组。
 * 注意:猫咪照片不随 CSV 导出,导入后照片为空。
 */
export function ordersFromCsv(text: string): LocalOrder[] {
  const rows = parseCsv(text)
  if (rows.length < 2) return []
  const header = rows[0].map((h) => h.trim())
  const col = (name: string) => header.indexOf(name)
  const iWechat = col('客户微信名')
  const iCustomer = col('客户姓名')
  const iCat = col('猫咪名字')
  const iTime = col('下单时间')
  const iDep = col('排队定金')
  const iMak = col('制作定金')
  const iFin = col('尾款')
  const iPay = col('付款状态')
  const iPhone = col('电话')
  const iAddr = col('地址')
  const iNote = col('备注')
  if (iCat === -1 || iPay === -1) return []

  const out: LocalOrder[] = []
  for (const r of rows.slice(1)) {
    const g = (i: number) => (i >= 0 ? (r[i] ?? '').trim() : '')
    const catName = g(iCat)
    if (!catName) continue

    const depositDue = Number(g(iDep)) || 0
    const makingDue = Number(g(iMak)) || 0
    const finalDue = Number(g(iFin)) || 0
    const status = g(iPay)
    const depositPaid = status.includes('排队') || status.includes('制作') || status.includes('尾款')
    const makingPaid = status.includes('制作') || status.includes('尾款')
    const finalPaid = status.includes('尾款')

    // 下单时间:"YYYY-MM-DD HH:mm" → 本地 "YYYY-MM-DDTHH:mm:ss"(与表单选择器格式一致)
    const timeRaw = g(iTime).trim()
    let orderTime = nowIso().slice(0, 19)
    if (timeRaw) {
      const t = new Date(timeRaw.replace(' ', 'T'))
      if (!isNaN(t.getTime())) {
        const pad = (n: number) => String(n).padStart(2, '0')
        orderTime = `${t.getFullYear()}-${pad(t.getMonth() + 1)}-${pad(t.getDate())}T${pad(t.getHours())}:${pad(t.getMinutes())}:${pad(t.getSeconds())}`
      }
    }

    out.push({
      id: genId(),
      createdAt: nowIso(),
      orderTime,
      totalPrice: depositDue + makingDue + finalDue,
      wechatName: g(iWechat) || undefined,
      customerName: g(iCustomer),
      catName,
      depositDue,
      makingDue,
      finalDue,
      depositPaid,
      makingPaid,
      finalPaid,
      phone: g(iPhone) || undefined,
      address: g(iAddr) || undefined,
      note: g(iNote) || undefined,
    })
  }
  return out
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