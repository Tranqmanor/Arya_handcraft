<template>
  <div class="op-page">
    <div class="top-bar">
      <span class="back" @click="$emit('back')">‹ 返回</span>
      <span class="title">视频管理</span>
      <span class="action" @click="openCreate">+ 新增</span>
    </div>

    <div v-if="loading" class="state-tip">加载中...</div>
    <div v-else-if="list.length === 0" class="state-tip">暂无视频</div>

    <div v-else class="card-list">
      <div v-for="v in list" :key="v.id" class="card">
        <div class="card-head">
          <span class="card-title">{{ v.title }}</span>
          <el-tag size="small" :type="v.is_published ? 'success' : 'info'">{{ v.is_published ? '上架' : '下架' }}</el-tag>
        </div>
        <div class="card-sub">▶ {{ v.view_count }} 浏览</div>
        <div class="card-actions">
          <el-button size="small" type="danger" plain @click="remove(v)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 新增视频弹层 -->
    <div v-if="formVisible" class="overlay" @click.self="formVisible = false">
      <div class="panel">
        <div class="panel-title">新增视频</div>
        <div class="field"><label>标题</label><input v-model="form.title" placeholder="必填" /></div>
        <div class="field"><label>描述</label><textarea v-model="form.description" placeholder="选填" rows="3" /></div>
        <div class="field">
          <label>视频文件(mp4,上传到 R2)</label>
          <input type="file" accept="video/mp4,video/quicktime,video/webm" @change="onFile" />
          <div v-if="progress > 0" class="progress-tip">上传中 {{ progress }}%</div>
        </div>
        <div class="field">
          <label>封面图片(选填)</label>
          <input type="file" accept="image/*" @change="onCover" />
        </div>
        <div class="switch-row">
          <span>上架</span>
          <input v-model="form.is_published" type="checkbox" />
        </div>
        <div class="form-actions">
          <button class="btn ghost" @click="formVisible = false">取消</button>
          <button class="btn primary" :disabled="saving || uploading" @click="save">
            {{ uploading ? `上传中 ${progress}%` : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { createVideo, deleteVideo, listVideos, uploadImage, uploadVideo, type OnlineVideo } from '@/api/online'

defineEmits<{ back: [] }>()

const list = ref<OnlineVideo[]>([])
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const progress = ref(0)
const formVisible = ref(false)

const form = reactive({
  title: '',
  description: '',
  video_url: '',
  cover_url: '',
  is_published: true,
})

async function load() {
  loading.value = true
  try {
    list.value = await listVideos()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { title: '', description: '', video_url: '', cover_url: '', is_published: true })
  progress.value = 0
  formVisible.value = true
}

async function onFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const { url } = await uploadVideo(file, (p) => (progress.value = p))
    form.video_url = url
    ElMessage.success('视频上传完成')
  } catch {
    /* 已提示 */
  } finally {
    uploading.value = false
  }
}

async function onCover(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    const { url } = await uploadImage(file)
    form.cover_url = url
    ElMessage.success('封面上传完成')
  } catch {
    /* 已提示 */
  }
}

async function save() {
  if (!form.title.trim() || !form.video_url) {
    ElMessage.warning('请填写标题并上传视频')
    return
  }
  saving.value = true
  try {
    await createVideo({
      title: form.title.trim(),
      description: form.description,
      video_url: form.video_url,
      cover_url: form.cover_url,
      is_published: form.is_published,
    })
    ElMessage.success('已保存')
    formVisible.value = false
    await load()
  } catch {
    /* 已提示 */
  } finally {
    saving.value = false
  }
}

async function remove(v: OnlineVideo) {
  try {
    await ElMessageBox.confirm(`确定删除视频「${v.title}」?`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  await deleteVideo(v.id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

<style scoped>
@import './op-shared.css';

.card-actions {
  margin-top: 10px;
}
.progress-tip {
  margin-top: 6px;
  color: #a98b84;
  font-size: 12px;
}
</style>