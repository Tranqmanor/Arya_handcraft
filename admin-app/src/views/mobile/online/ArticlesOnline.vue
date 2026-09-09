<template>
  <div class="op-page">
    <div class="top-bar">
      <span class="back" @click="$emit('back')">‹ 返回</span>
      <span class="title">文章管理</span>
      <span class="action" @click="openCreate">+ 新增</span>
    </div>

    <div v-if="loading" class="state-tip">加载中...</div>
    <div v-else-if="list.length === 0" class="state-tip">暂无文章</div>

    <div v-else class="card-list">
      <div v-for="a in list" :key="a.id" class="card" @click="openEdit(a)">
        <div class="card-head">
          <span class="card-title">{{ a.title }}</span>
          <el-tag size="small" :type="a.is_published ? 'success' : 'info'">{{ a.is_published ? '上架' : '下架' }}</el-tag>
        </div>
        <div class="card-sub">{{ catText(a.category) }} · {{ a.view_count }} 阅读</div>
      </div>
    </div>

    <!-- 表单弹层 -->
    <div v-if="formVisible" class="overlay" @click.self="formVisible = false">
      <div class="panel">
        <div class="panel-title">{{ form.id ? '编辑文章' : '新增文章' }}</div>
        <div class="field"><label>标题</label><input v-model="form.title" placeholder="必填" /></div>
        <div class="field"><label>摘要</label><input v-model="form.summary" placeholder="选填" /></div>
        <div class="field">
          <label>分类</label>
          <select v-model="form.category">
            <option value="general">普通文章</option>
            <option value="photo_guide">拍照指南</option>
            <option value="about_wool">关于羊毛毡</option>
            <option value="about_arya">关于Arya</option>
          </select>
        </div>
        <div class="field">
          <label>正文(Markdown)</label>
          <textarea v-model="form.content" placeholder="支持 Markdown" rows="8" />
        </div>
        <div class="switch-row">
          <span>上架</span>
          <input v-model="form.is_published" type="checkbox" />
        </div>
        <div class="form-actions">
          <button class="btn ghost" @click="formVisible = false">取消</button>
          <button class="btn primary" :disabled="saving" @click="save">保存</button>
        </div>
        <button v-if="form.id" class="btn del" @click="remove">删除该文章</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import './op-shared.css';
</style>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { createArticle, deleteArticle, listArticles, updateArticle, type OnlineArticle } from '@/api/online'

defineEmits<{ back: [] }>()

const list = ref<OnlineArticle[]>([])
const loading = ref(true)
const saving = ref(false)
const formVisible = ref(false)

const form = reactive({
  id: 0,
  title: '',
  summary: '',
  category: 'general',
  content: '',
  is_published: true,
})

function catText(c: string) {
  const map: Record<string, string> = {
    general: '普通',
    photo_guide: '拍照指南',
    about_wool: '关于羊毛毡',
    about_arya: '关于Arya',
  }
  return map[c] || c
}

async function load() {
  loading.value = true
  try {
    list.value = await listArticles()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { id: 0, title: '', summary: '', category: 'general', content: '', is_published: true })
  formVisible.value = true
}

function openEdit(a: OnlineArticle) {
  Object.assign(form, {
    id: a.id,
    title: a.title,
    summary: a.summary,
    category: a.category,
    content: a.content,
    is_published: a.is_published,
  })
  formVisible.value = true
}

async function save() {
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning('标题与正文必填')
    return
  }
  saving.value = true
  try {
    const data = {
      title: form.title.trim(),
      summary: form.summary,
      category: form.category,
      content: form.content,
      is_published: form.is_published,
    }
    if (form.id) await updateArticle(form.id, data)
    else await createArticle(data)
    ElMessage.success('已保存')
    formVisible.value = false
    await load()
  } catch {
    /* 已提示 */
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!form.id) return
  try {
    await ElMessageBox.confirm('确定删除该文章?', '删除确认', { type: 'warning' })
  } catch {
    return
  }
  await deleteArticle(form.id)
  ElMessage.success('已删除')
  formVisible.value = false
  await load()
}

onMounted(load)
</script>