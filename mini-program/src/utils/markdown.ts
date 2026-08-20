// 轻量 Markdown → HTML 渲染(覆盖拍照指南等文章常用语法)
// 注意:小程序 rich-text 仅支持有限标签,这里保守输出 h1-h4/p/ul/li/blockquote/img/strong/table

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function inline(text: string): string {
  return text
    // **加粗**
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 行内代码
    .replace(/`(.+?)`/g, '<span style="background:#f0ebe6;padding:0 6rpx;border-radius:6rpx;">$1</span>')
    // 链接
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
}

export function renderMarkdown(md: string): string {
  if (!md) return ''

  const lines = md.split(/\r?\n/)
  const html: string[] = []
  let inList = false
  let inTable = false
  let tableRows: string[][] = []

  const closeList = () => {
    if (inList) {
      html.push('</ul>')
      inList = false
    }
  }
  const closeTable = () => {
    if (inTable) {
      // 渲染表格为简单 HTML
      const thead = tableRows[0] || []
      const body = tableRows.slice(1)
      let t = '<table style="width:100%;border-collapse:collapse;font-size:26rpx;">'
      t += '<thead><tr>'
      for (const h of thead) {
        t += `<th style="border:1px solid #e5ded8;padding:12rpx 16rpx;background:#faf6f0;">${inline(h)}</th>`
      }
      t += '</tr></thead><tbody>'
      for (const row of body) {
        t += '<tr>'
        for (const cell of row) {
          t += `<td style="border:1px solid #e5ded8;padding:12rpx 16rpx;">${inline(cell)}</td>`
        }
        t += '</tr>'
      }
      t += '</tbody></table>'
      html.push(t)
      inTable = false
      tableRows = []
    }
  }

  for (const raw of lines) {
    const line = raw.trim()

    // 表格行
    if (line.startsWith('|') && line.endsWith('|')) {
      if (!inTable) {
        inTable = true
        tableRows = []
      }
      const cells = line.slice(1, -1).split('|').map((c) => c.trim())
      // 分隔行(---)跳过
      if (cells.every((c) => /^:?-+:?$/.test(c))) continue
      tableRows.push(cells)
      continue
    } else {
      closeTable()
    }

    // 标题
    const h = line.match(/^(#{1,4})\s+(.*)$/)
    if (h) {
      closeList()
      const level = h[1].length
      html.push(`<h${level}>${inline(escapeHtml(h[2]))}</h${level}>`)
      continue
    }

    // 引用
    if (line.startsWith('>')) {
      closeList()
      html.push(
        `<blockquote style="border-left:6rpx solid #c9a9a6;padding:12rpx 20rpx;background:#faf6f0;color:#5a5350;margin:16rpx 0;">${inline(escapeHtml(line.slice(1).trim()))}</blockquote>`,
      )
      continue
    }

    // 无序列表
    const li = line.match(/^[-*]\s+(.*)$/)
    if (li) {
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${inline(escapeHtml(li[1]))}</li>`)
      continue
    }

    // 有序列表
    const oli = line.match(/^\d+[.、]\s+(.*)$/)
    if (oli) {
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${inline(escapeHtml(oli[1]))}</li>`)
      continue
    }

    // 图片
    const img = line.match(/^!\[.*?\]\((.+?)\)$/)
    if (img) {
      closeList()
      html.push(`<img src="${escapeHtml(img[1])}" style="width:100%;border-radius:16rpx;margin:16rpx 0;" />`)
      continue
    }

    // 分隔线
    if (/^(-{3,}|\*{3,})$/.test(line)) {
      closeList()
      html.push('<hr style="border:none;border-top:1px solid #e5ded8;margin:24rpx 0;" />')
      continue
    }

    // 空行
    if (line === '') {
      closeList()
      continue
    }

    // 普通段落
    closeList()
    html.push(`<p style="margin:16rpx 0;">${inline(escapeHtml(line))}</p>`)
  }

  closeList()
  closeTable()
  return html.join('')
}