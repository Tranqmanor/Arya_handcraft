<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  createCarouselImage,
  deleteCarouselImage,
  listCarouselImages,
  updateCarouselImage,
  type AdminCarouselImage,
} from '@/api/admin'

const carouselImages = ref<AdminCarouselImage[]>([])
const dialogVisible = ref(false)
const editing = ref<AdminCarouselImage | null>(null)
const form = ref({
  image_url: '',
  title: '',
  description: '',
  is_published: true,
  sort_order: 0,
})

async function load() {
  carouselImages.value = await listCarouselImages()
}

function openCreate() {
  editing.value = null
  form.value = { image_url: '', title: '', description: '', is_published: true, sort_order: 0 }
  dialogVisible.value = true
}

function openEdit(item: AdminCarouselImage) {
  editing.value = item
  form.value = {
    image_url: item.image_url,
    title: item.title,
    description: item.description,
    is_published: item.is_published,
    sort_order: item.sort_order,
  }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.image_url) {
    ElMessage.warning('请填写图片地址')
    return
  }
  if (editing.value) {
    await updateCarouselImage(editing.value.id, form.value)
    ElMessage.success('已更新')
  } else {
    await createCarouselImage(form.value)
    ElMessage.success('已创建')
  }
  dialogVisible.value = false
  await load()
}

async function remove(item: AdminCarouselImage) {
  await ElMessageBox.confirm(`确定删除该轮播图?`, '提示')
  await deleteCarouselImage(item.id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="bar">
      <h3>轮播图管理</h3>
      <el-button type="primary" @click="openCreate">新增轮播图</el-button>
    </div>
    <el-table :data="carouselImages" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="图片" width="120">
        <template #default="{ row }">
          <img
            :src="row.image_url"
            style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px;"
            alt=""
          />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="120" />
      <el-table-column prop="sort_order" label="排序" width="70" />
      <el-table-column label="发布" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'info'">
            {{ row.is_published ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">
          {{ new Date(row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑轮播图' : '新增轮播图'" width="520px">
      <el-form label-width="80px">
        <el-form-item label="图片URL">
          <el-input v-model="form.image_url" placeholder="Cloudflare R2 或 CDN 地址" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="发布">
          <el-switch v-model="form.is_published" />
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