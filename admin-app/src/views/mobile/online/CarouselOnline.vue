<template>
  <div class="op-page">
    <div class="top-bar">
      <span class="back" @click="$emit('back')">‹ 返回</span>
      <span class="title">轮播图管理</span>
      <span class="action" @click="openCreate">+ 新增</span>
    </div>

    <div v-if="loading" class="state-tip">加载中...</div>
    <div v-else-if="list.length === 0" class="state-tip">暂无轮播图</div>

    <div v-else class="card-list">
      <div v-for="c in list" :key="c.id" class="card">
        <img v-if="c.image_url" class="card-img" :src="c.image_url" alt="" />
        <div class="card-head">
          <span class="card-title">{{ c.title || '(无标题)' }}</span>
          <el-tag size="small" :type="c.is_published ? 'success' : 'info'">{{ c.is_published ? '上架' : '下架' }}</el-tag>
        </div>
        <div v-if="c.description" class="card-sub">{{ c.description }}</div>
        <div class="card-actions">
          <el-button size="small" type="danger" plain @click="remove(c)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 新增弹层 -->
    <div v-if="formVisible" class="overlay" @click.self="formVisible = false">
      <div class="panel">
        <div class="panel-title">新增轮播图</div>
        <div class="field">
          <label>图片(上传到 R2)</label>
          <input type="file" accept="image/*" @change="onFile" />
          <div v-if="form.image_url" class="preview-row"><img :src="form.image_url" alt="" /></div>
        </div>
        <div class="field"><label>标题</label><input v-model="form.title" placeholder="选填" /></div>
        <div class="field"><label>描述</label><textarea v-model="form.description" placeholder="选填" rows="2" /></div>
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
import { ElMessage } from 'element-plus'

import { createCarousel, deleteCarousel, listCarousel, uploadImage, type OnlineCarousel } from '@/api/online'

defineEmits<{ back: [] }>()

const list = ref<OnlineCarousel[]>([])
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const progress = ref(0)
const formVisible = ref(false)

const form = reactive({
  image_url: '',
  title: '',
  description: '',
  is_published: true,
})

async function load() {
  loading.value = true
  try {
    list.value = await listCarousel()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { image_url: '', title: '', description: '', is_published: true })
  progress.value = 0
  formVisible.value = true
}

async function onFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const { url } = await uploadImage(file, (p) => (progress.value = p))
    form.image_url = url
    ElMessage.success('图片上传完成')
  } catch {
    /* 已提示 */
  } finally {
    uploading.value = false
  }
}

async function save() {
  if (!form.image_url) {
    ElMessage.warning('请先上传图片')
    return
  }
  saving.value = true
  try {
    await createCarousel({
      image_url: form.image_url,
      title: form.title.trim(),
      description: form.description,
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

async function remove(c: OnlineCarousel) {
  if (!confirm('确定删除该轮播图?')) return
  await deleteCarousel(c.id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

<style scoped>
@import './op-shared.css';

.card-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
  margin-bottom: 8px;
}
.card-actions {
  margin-top: 10px;
}
.progress-tip {
  margin-top: 6px;
  color: #a98b84;
  font-size: 12px;
}
.preview-row {
  margin-top: 8px;
}
.preview-row img {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
}
</style>