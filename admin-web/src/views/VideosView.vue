<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  createVideo,
  deleteVideo,
  listVideos,
  updateVideo,
  type AdminVideo,
} from '@/api/admin'

const videos = ref<AdminVideo[]>([])
const dialogVisible = ref(false)
const editing = ref<AdminVideo | null>(null)
const form = ref({
  title: '',
  description: '',
  video_url: '',
  cover_url: '',
  duration: 0,
  is_published: true,
  sort_order: 0,
})

async function load() {
  videos.value = await listVideos()
}

function openCreate() {
  editing.value = null
  form.value = { title: '', description: '', video_url: '', cover_url: '', duration: 0, is_published: true, sort_order: 0 }
  dialogVisible.value = true
}

function openEdit(v: AdminVideo) {
  editing.value = v
  form.value = {
    title: v.title,
    description: v.description,
    video_url: v.video_url,
    cover_url: v.cover_url,
    duration: v.duration,
    is_published: v.is_published,
    sort_order: v.sort_order,
  }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.title || !form.value.video_url) {
    ElMessage.warning('请填写标题和视频地址')
    return
  }
  if (editing.value) {
    await updateVideo(editing.value.id, form.value)
    ElMessage.success('已更新')
  } else {
    await createVideo(form.value)
    ElMessage.success('已创建')
  }
  dialogVisible.value = false
  await load()
}

async function remove(v: AdminVideo) {
  await ElMessageBox.confirm(`确定删除「${v.title}」?`, '提示')
  await deleteVideo(v.id)
  ElMessage.success('已删除')
  await load()
}

function fmtDuration(s: number) {
  const m = Math.floor(s / 60)
  const r = s % 60
  return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`
}

onMounted(load)
</script>

<template>
  <div>
    <div class="bar">
      <h3>视频管理</h3>
      <el-button type="primary" @click="openCreate">新增视频</el-button>
    </div>
    <el-table :data="videos" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="160" />
      <el-table-column label="时长" width="80">
        <template #default="{ row }">{{ fmtDuration(row.duration) }}</template>
      </el-table-column>
      <el-table-column prop="view_count" label="浏览量" width="90" />
      <el-table-column prop="sort_order" label="排序" width="70" />
      <el-table-column label="发布" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'info'">
            {{ row.is_published ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑视频' : '新增视频'" width="520px">
      <el-form label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="视频URL"><el-input v-model="form.video_url" placeholder="R2 或 CDN 地址" /></el-form-item>
        <el-form-item label="封面URL"><el-input v-model="form.cover_url" /></el-form-item>
        <el-form-item label="时长(秒)"><el-input-number v-model="form.duration" :min="0" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        <el-form-item label="发布">
          <el-switch v-model="form.is_published" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
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
