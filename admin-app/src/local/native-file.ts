// 原生文件选择桥(安卓 WebView 壳内 file_picker 插件;浏览器开发环境自动回退 input)
export interface NativeFile {
  name: string
  dataUrl: string
}

interface PickReply {
  reqId: string
  name: string | null
  data: string | null
  mime: string | null
}

const bridge = () => (window as unknown as Record<string, { postMessage(m: string): void } | undefined>).filePicker

let seq = 0
const pending = new Map<string, (v: NativeFile | null) => void>()

;(window as unknown as Record<string, unknown>).__onNativeFile = (p: PickReply) => {
  const cb = pending.get(p.reqId)
  if (!cb) return
  pending.delete(p.reqId)
  if (!p.data) {
    cb(null)
  } else {
    cb({ name: p.name || 'file', dataUrl: `data:${p.mime || 'application/octet-stream'};base64,${p.data}` })
  }
}

/** App 壳内可用(浏览器返回 false,走普通 file input) */
export function hasNativeFilePicker(): boolean {
  return !!bridge()
}

export function pickNativeFile(kind: 'image' | 'csv'): Promise<NativeFile | null> {
  const b = bridge()
  if (!b) return Promise.resolve(null)
  const reqId = `f${Date.now()}_${++seq}`
  return new Promise((resolve) => {
    pending.set(reqId, resolve)
    b.postMessage(JSON.stringify({ reqId, kind }))
  })
}

/** dataURL → UTF-8 文本(导入 CSV 用) */
export function dataUrlToText(dataUrl: string): string {
  const b64 = dataUrl.slice(dataUrl.indexOf(',') + 1)
  const bin = atob(b64)
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0))
  return new TextDecoder('utf-8').decode(bytes)
}