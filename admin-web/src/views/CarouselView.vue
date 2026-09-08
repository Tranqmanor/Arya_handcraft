<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  createCarouselImage,
  deleteCarouselImage,
  getHomeSettings,
  listCarouselImages,
  updateCarouselImage,
  updateHomeSettings,
  uploadImage,
  type AdminCarouselImage,
} from '@/api/admin'

const carouselImages = ref<AdminCarouselImage[]>([])
const dialogVisible = ref(false)
const editing = ref<AdminCarouselImage | null>(null)

// 首页宣传图配置
const promoImage = ref('')
const promoUploading = ref(false)
const promoFileRef = ref<HTMLInputElement | null>(null)
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

async function loadPromo() {
  try {
    const settings = await getHomeSettings()
    promoImage.value = settings.promo_image_url
  } catch { /* ignore */ }
}

async function onPromoPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  promoUploading.value = true
  try {
    const { url } = await uploadImage(file)
    await updateHomeSettings(url)
    promoImage.value = url
    ElMessage.success('宣传图已更新')
  } catch (err) {
    console.error('宣传图上传失败:', err)
  } finally {
    promoUploading.value = false
  }
}

async function clearPromo() {
  await updateHomeSettings('')
  promoImage.value = ''
  ElMessage.success('已清除,小程序将显示默认占位')
}

onMounted(() => {
  load()
  loadPromo()
})
</script>

<template>
  <div>
    <div class="bar">
      <h3>轮播图管理</h3>
      <el-button type="primary" @click="openCreate">新增轮播图</el-button>
    </div>

    <!-- 首页宣传图(六宫格下方横幅) -->
    <el-card shadow="never" class="promo-card">
      <template #header>首页宣传图(六宫格下方的横版大图)</template>
      <div class="promo-row">
        <div class="promo-preview">
          <img v-if="promoImage" :src="promoImage" alt="" />
          <div v-else class="promo-empty">未设置(小程序显示默认品牌横幅)</div>
        </div>
        <div class="promo-actions">
          <el-button type="primary" :loading="promoUploading" @click="promoFileRef?.click()">
            {{ promoImage ? '更换宣传图' : '上传宣传图' }}
          </el-button>
          <el-button v-if="promoImage" plain @click="clearPromo">清除</el-button>
          <div class="promo-tip">建议横版,比例约 3:1,宽度 ≥ 750px</div>
        </div>
      </div>
      <input ref="promoFileRef" type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden @change="onPromoPicked" />
    </el-card>
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

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑轮播图' : '新增轮播图'" width="520px"
      :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
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

.promo-card {
  margin-bottom: 16px;
}

.promo-row {
  display: flex;
  gap: 24px;
  align-items: center;
}

.promo-preview {
  width: 320px;
  height: 110px;
  border-radius: 8px;
  overflow: hidden;
  background: #faf6f0;
  border: 1px solid #f0ebe6;
  flex-shrink: 0;
}

.promo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.promo-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b9b1ac;
  font-size: 13px;
}

.promo-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.promo-tip {
  color: #b9b1ac;
  font-size: 12px;
}
</style>