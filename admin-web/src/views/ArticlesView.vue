<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  createArticle,
  deleteArticle,
  listArticles,
  updateArticle,
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

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑文章' : '新增文章'" width="640px">
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
        <el-form-item label="封面URL"><el-input v-model="form.cover_url" /></el-form-item>
        <el-form-item label="正文(Markdown)">
          <el-input v-model="form.content" type="textarea" :rows="12" />
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
</style>