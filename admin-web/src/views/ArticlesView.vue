<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'

import {
  createArticle,
  deleteArticle,
  listArticles,
  updateArticle,
  uploadImage,
  uploadVideo,
  type AdminArticle,
} from '@/api/admin'

const articles = ref<AdminArticle[]>([])
const dialogVisible = ref(false)
const editing = ref<AdminArticle | null>(null)
const form = ref({
  title: '',
  summary: '',
  cover_url: '',
  content: '',
  category: 'general',
  is_published: true,
  sort_order: 0,
})

async function load() {
  articles.value = await listArticles()
}

function openCreate() {
  editing.value = null
  form.value = { title: '', summary: '', cover_url: '', content: '', category: 'general', is_published: true, sort_order: 0 }
  dialogVisible.value = true
}

function openEdit(a: AdminArticle) {
  editing.value = a
  form.value = {
    title: a.title,
    summary: a.summary,
    cover_url: a.cover_url,
    content: a.content,
    category: a.category,
    is_published: a.is_published,
    sort_order: a.sort_order,
  }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.title || !form.value.content) {
    ElMessage.warning('请填写标题和正文')
    return
  }
  if (editing.value) {
    await updateArticle(editing.value.id, form.value)
    ElMessage.success('已更新')
  } else {
    await createArticle(form.value)
    ElMessage.success('已创建')
  }
  dialogVisible.value = false
  await load()
}

async function remove(a: AdminArticle) {
  await ElMessageBox.confirm(`确定删除「${a.title}」?`, '提示')
  await deleteArticle(a.id)
  ElMessage.success('已删除')
  await load()
}

// ===== Markdown 图文编辑器 =====
const contentInputRef = ref<{ textarea: HTMLTextAreaElement } | null>(null)
const contentFileRef = ref<HTMLInputElement | null>(null)
const coverFileRef = ref<HTMLInputElement | null>(null)
const videoFileRef = ref<HTMLInputElement | null>(null)
const uploadingImage = ref(false)
const uploadingCover = ref(false)
const uploadingVideo = ref(false)
const videoProgress = ref(0)

const previewHtml = computed(() => {
  // 预览不支持内嵌播放,将视频语法替换为占位卡片
  const md = (form.value.content || '').replace(
    /!video\[\]\(([^)]+)\)/g,
    '<div style="padding:18px;text-align:center;border:1px dashed #c9a9a6;border-radius:8px;background:#fff;color:#a98b84;font-size:14px;">🎬 视频片段(保存后在小程序内播放)</div>',
  )
  return marked.parse(md, { async: false }) as string
})

/** 包裹选中文字;无选中则在光标处插入模板 */
function wrap(before: string, after = '') {
  const el = contentInputRef.value?.textarea
  const val = form.value.content
  if (!el) {
    form.value.content = `${val}${before}文字${after}`
    return
  }
  const start = el.selectionStart ?? val.length
  const end = el.selectionEnd ?? start
  const selected = val.slice(start, end) || '文字'
  form.value.content = val.slice(0, start) + before + selected + after + val.slice(end)
  nextTick(() => {
    el.focus()
    const pos = start + before.length + selected.length + after.length
    el.setSelectionRange(pos, pos)
  })
}

/** 在光标处插入纯文本(如图片 Markdown) */
function insertText(text: string) {
  const el = contentInputRef.value?.textarea
  const val = form.value.content
  if (!el) {
    form.value.content = val + text
    return
  }
  const start = el.selectionStart ?? val.length
  form.value.content = val.slice(0, start) + text + val.slice(start)
  nextTick(() => {
    el.focus()
    const pos = start + text.length
    el.setSelectionRange(pos, pos)
  })
}

async function onContentPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = '' // 允许再次选择同一文件
  if (!file) return
  uploadingImage.value = true
  try {
    const { url } = await uploadImage(file)
    insertText(`\n![图片](${url})\n`)
    ElMessage.success('图片已插入')
  } catch (err) {
    console.error('图片上传失败:', err) // http.ts 已统一弹出后端错误详情
  } finally {
    uploadingImage.value = false
  }
}

async function onCoverPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  uploadingCover.value = true
  try {
    const { url } = await uploadImage(file)
    form.value.cover_url = url
    ElMessage.success('封面上传成功')
  } catch (err) {
    console.error('封面上传失败:', err)
  } finally {
    uploadingCover.value = false
  }
}

async function onVideoPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  uploadingVideo.value = true
  videoProgress.value = 0
  try {
    const { url } = await uploadVideo(file, (p) => (videoProgress.value = p))
    insertText(`\n!video[](${url})\n`)
    ElMessage.success('视频已插入')
  } catch (err) {
    console.error('视频上传失败:', err) // http.ts 已统一弹出后端错误详情
  } finally {
    uploadingVideo.value = false
  }
}

const categoryOptions = [
  { label: '普通文章', value: 'general' },
  { label: '拍照指南', value: 'photo_guide' },
]

onMounted(load)
</script>

<template>
  <div>
    <div class="bar">
      <h3>文章管理</h3>
      <el-button type="primary" @click="openCreate">新增文章</el-button>
    </div>
    <el-table :data="articles" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column label="分类" width="100">
        <template #default="{ row }">
          <el-tag>{{ row.category === 'photo_guide' ? '拍照指南' : '普通' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="阅读" width="80" />
      <el-table-column prop="sort_order" label="排序" width="70" />
      <el-table-column label="发布" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'info'">{{ row.is_published ? '上架' : '下架' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑文章' : '新增文章'" width="920px" top="4vh">
      <el-form label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="摘要"><el-input v-model="form.summary" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category">
            <el-option v-for="o in categoryOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        <el-form-item label="发布"><el-switch v-model="form.is_published" /></el-form-item>
        <el-form-item label="封面">
          <div class="cover-row">
            <el-input v-model="form.cover_url" placeholder="留空则不显示封面;可直接上传生成地址" />
            <el-button :loading="uploadingCover" @click="coverFileRef?.click()">上传封面</el-button>
          </div>
          <input ref="coverFileRef" type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden @change="onCoverPicked" />
        </el-form-item>
        <el-form-item label="正文">
          <div class="editor-wrap">
            <div class="toolbar">
              <el-button size="small" @click="wrap('## ', '')">标题</el-button>
              <el-button size="small" @click="wrap('**', '**')">加粗</el-button>
              <el-button size="small" @click="wrap('\n- ', '')">列表</el-button>
              <el-button size="small" @click="wrap('> ', '')">引用</el-button>
              <el-button size="small" @click="wrap('\n---\n', '')">分隔线</el-button>
              <el-divider direction="vertical" />
              <el-button size="small" type="primary" :loading="uploadingImage" @click="contentFileRef?.click()">
                插入图片
              </el-button>
              <el-button
                size="small"
                type="warning"
                plain
                :loading="uploadingVideo"
                @click="videoFileRef?.click()"
              >
                {{ uploadingVideo ? `上传中 ${videoProgress}%` : '插入视频' }}
              </el-button>
              <span class="toolbar-tip">图片即传即嵌;视频 ≤200MB,保存后小程序内播放</span>
              <input ref="contentFileRef" type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden @change="onContentPicked" />
              <input ref="videoFileRef" type="file" accept="video/mp4,video/quicktime,video/x-m4v,video/webm" hidden @change="onVideoPicked" />
            </div>
            <div class="split">
              <el-input
                ref="contentInputRef"
                v-model="form.content"
                type="textarea"
                :autosize="{ minRows: 18, maxRows: 18 }"
                placeholder="在此撰写正文…&#10;&#10;# 一级标题&#10;- 列表项&#10;**加粗** > 引用&#10;点上方「插入图片」可上传图片并自动嵌入"
              />
              <div class="preview markdown-body" v-html="previewHtml"></div>
            </div>
            <div class="hint">左侧编辑 · 右侧实时预览(渲染效果与小程序端一致)</div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.cover-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

/* ===== 图文编辑器 ===== */
.editor-wrap {
  width: 100%;
}

.toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.toolbar-tip {
  margin-left: auto;
  font-size: 12px;
  color: #b9b1ac;
}

.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.preview {
  height: 414px;
  padding: 12px 16px;
  border: 1px solid #e5ded8;
  border-radius: 6px;
  background: #faf6f0;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.8;
  color: #5a5350;
  word-break: break-word;
}

.preview :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  display: block;
  margin: 8px 0;
}

.preview :deep(h1),
.preview :deep(h2),
.preview :deep(h3),
.preview :deep(h4) {
  margin: 10px 0 6px;
  line-height: 1.4;
}

.preview :deep(blockquote) {
  margin: 8px 0;
  padding: 4px 12px;
  border-left: 4px solid #c9a9a6;
  background: #fff;
  color: #7a716d;
}

.hint {
  margin-top: 6px;
  font-size: 12px;
  color: #b9b1ac;
}
</style>