<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-start justify-between gap-4 mb-6">
      <div class="min-w-0">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--foreground)]">轮播图管理</h1>
        <p class="mt-1.5 text-sm text-[var(--muted-foreground)]">管理首页轮播图与 Banner</p>
      </div>
      <button
        class="shrink-0 inline-flex items-center gap-1.5 px-4 h-10 rounded-[var(--radius-md)] bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-deep)] active:translate-y-px transition-all"
        @click="openDialog()"
      >
        <Plus class="w-4 h-4" />
        <span>新增轮播项</span>
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      <StatCard label="轮播项总数" :value="stats.total" color="var(--color-primary)" />
      <StatCard label="启用中" :value="stats.enabled" color="var(--chart-1)" />
      <StatCard label="已禁用" :value="stats.disabled" color="var(--chart-4)" />
    </div>

    <!-- 筛选 + 批量操作 -->
    <div
      class="bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-lg)] p-4 mb-4 flex flex-wrap items-center gap-3"
    >
      <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px" @change="onFilterChange">
        <el-option label="启用" value="enabled" />
        <el-option label="禁用" value="disabled" />
      </el-select>

      <el-input
        v-model="filters.search"
        placeholder="搜索标题"
        clearable
        style="width: 240px"
        @change="onFilterChange"
      />

      <div class="flex-1" />

      <el-button
        type="danger"
        :disabled="selectedIds.length === 0"
        @click="onBatchDelete"
      >
        <Trash2 class="w-4 h-4 mr-1" />
        批量删除<sup v-if="selectedIds.length" class="ml-1">{{ selectedIds.length }}</sup>
      </el-button>
    </div>

    <!-- 表格 -->
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-lg)] overflow-hidden">
      <el-table :data="banners" v-loading="loading" @selection-change="onSelectionChange" stripe>
        <el-table-column type="selection" width="48" />
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column label="封面预览" width="160">
          <template #default="{ row }">
            <img
              v-if="row.image_url"
              :src="row.image_url"
              alt="banner"
              class="w-full h-16 object-cover rounded-[var(--radius-sm)] border border-[var(--border)]"
            />
            <span v-else class="text-sm text-[var(--muted-foreground)]">无封面</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="subtitle" label="副标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="link_url" label="链接" min-width="180" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span
              class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs"
              :style="
                row.status === 'enabled'
                  ? 'background: var(--accent); color: var(--accent-foreground)'
                  : 'background: var(--secondary); color: var(--secondary-foreground)'
              "
            >
              <span
                class="w-1.5 h-1.5 rounded-full"
                :style="row.status === 'enabled' ? 'background: var(--color-primary)' : 'background: var(--muted-foreground)'"
              />
              {{ row.status === 'enabled' ? '启用' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDialog(row)">
              <Pencil class="w-3.5 h-3.5 mr-0.5" />
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="onDelete(row)">
              <Trash2 class="w-3.5 h-3.5 mr-0.5" />
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="flex justify-end items-center p-4">
        <el-pagination
          v-model:current-page="page.current"
          v-model:page-size="page.size"
          :total="page.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="loadBanners"
          @size-change="loadBanners"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="520px"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="dialogForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="副标题">
          <el-input v-model="dialogForm.subtitle" placeholder="请输入副标题（可选）" />
        </el-form-item>
        <el-form-item label="图片 URL">
          <el-input v-model="dialogForm.image_url" placeholder="https://…" />
        </el-form-item>
        <el-form-item label="链接 URL">
          <el-input v-model="dialogForm.link_url" placeholder="https://…" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="dialogForm.sort_order" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="dialogForm.status">
            <el-radio value="enabled">启用</el-radio>
            <el-radio value="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogSaving" @click="onDialogSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Trash2, Pencil } from 'lucide-vue-next'
import { list as listBanners, remove as removeBanner, stats as fetchStats, create as createBanner, update as updateBanner } from '@/api/banner'
import StatCard from '@/components/StatCard.vue'

const banners = ref([])
const loading = ref(false)

const stats = reactive({ total: 0, enabled: 0, disabled: 0 })

const filters = reactive({
  status: '',
  search: '',
})

const page = reactive({
  current: 1,
  size: 10,
  total: 0,
})

const selectedIds = ref([])
function onSelectionChange(rows) {
  selectedIds.value = rows.map((r) => r.id)
}

function onFilterChange() {
  page.current = 1
  loadBanners()
}

async function loadBanners() {
  loading.value = true
  try {
    const params = {
      page: page.current,
      per_page: page.size,
    }
    if (filters.status) params.status = filters.status
    if (filters.search) params.search = filters.search
    const data = await listBanners(params)
    banners.value = data?.items || data?.list || data || []
    page.total = data?.total ?? banners.value.length
  } catch (e) {
    banners.value = []
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const data = await fetchStats()
    Object.assign(stats, data || {})
  } catch (e) {
    // ignore
  }
}

// 弹窗
const dialogVisible = ref(false)
const dialogSaving = ref(false)
const dialogMode = ref('create')
const editingId = ref(null)
const dialogForm = reactive({
  title: '',
  subtitle: '',
  image_url: '',
  link_url: '',
  sort_order: 0,
  status: 'enabled',
})

const dialogTitle = computed(() => (dialogMode.value === 'create' ? '新增轮播项' : '编辑轮播项'))

function openDialog(row) {
  if (row) {
    dialogMode.value = 'edit'
    editingId.value = row.id
    Object.assign(dialogForm, {
      title: row.title ?? '',
      subtitle: row.subtitle ?? '',
      image_url: row.image_url ?? '',
      link_url: row.link_url ?? '',
      sort_order: row.sort_order ?? 0,
      status: row.status ?? 'enabled',
    })
  } else {
    dialogMode.value = 'create'
    editingId.value = null
    Object.assign(dialogForm, {
      title: '',
      subtitle: '',
      image_url: '',
      link_url: '',
      sort_order: 0,
      status: 'enabled',
    })
  }
  dialogVisible.value = true
}

async function onDialogSave() {
  if (!dialogForm.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  dialogSaving.value = true
  try {
    if (dialogMode.value === 'create') {
      await createBanner({ ...dialogForm })
      ElMessage.success('创建成功')
    } else {
      await updateBanner(editingId.value, { ...dialogForm })
      ElMessage.success('保存成功')
    }
    dialogVisible.value = false
    loadBanners()
    loadStats()
  } catch (e) {
    // ignore
  } finally {
    dialogSaving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除轮播项「${row.title}」吗？`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  try {
    await removeBanner(row.id)
    ElMessage.success('删除成功')
    loadBanners()
    loadStats()
  } catch (e) {
    // ignore
  }
}

async function onBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 个轮播项吗？`, '批量删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  try {
    // 后端如未提供批量删除接口，则串行删除
    await Promise.all(selectedIds.value.map((id) => removeBanner(id)))
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadBanners()
    loadStats()
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  loadBanners()
  loadStats()
})
</script>
