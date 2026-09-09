// 图片选择并压缩为 dataURL(本地存储友好:最长边 ≤420px,JPEG 75%)
export function compressImageToDataUrl(file: File, maxSide = 420, quality = 0.75): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      compressFromDataUrl(reader.result as string, maxSide, quality).then(resolve, reject)
    }
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsDataURL(file)
  })
}

/** 由 dataURL/URL 压缩(原生桥选图回传 base64 时用) */
export function compressFromDataUrl(src: string, maxSide = 420, quality = 0.75): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      const scale = Math.min(1, maxSide / Math.max(img.width, img.height))
      const w = Math.max(1, Math.round(img.width * scale))
      const h = Math.max(1, Math.round(img.height * scale))
      const canvas = document.createElement('canvas')
      canvas.width = w
      canvas.height = h
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('canvas 不可用'))
        return
      }
      ctx.fillStyle = '#fff'
      ctx.fillRect(0, 0, w, h)
      ctx.drawImage(img, 0, 0, w, h)
      resolve(canvas.toDataURL('image/jpeg', quality))
    }
    img.onerror = () => reject(new Error('图片解析失败'))
    img.src = src
  })
}