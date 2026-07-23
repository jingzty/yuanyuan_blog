<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-start justify-between gap-4 mb-6">
      <div class="min-w-0">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--foreground)]">文章推荐管理</h1>
        <p class="mt-1.5 text-sm text-[var(--muted-foreground)]">管理首页「文章推荐」区展示的文章</p>
      </div>
      <button
        class="shrink-0 inline-flex items-center gap-1.5 px-4 h-10 rounded-[var(--radius-md)] bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-deep)] active:translate-y-px transition-all"
        @click="openDialog()"
      >
        <Plus class="w-4 h-4" />
        <span>新增推荐</span>
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      <StatCard label="推荐总数" :value="stats.total" color="var(--color-primary)" />
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
        placeholder="搜索文章标题"
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
      <el-table :data="filteredList" v-loading="loading" @selection-change="onSelectionChange" stripe>
        <el-table-column type="selection" width="48" />
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column label="封面预览" width="160">
          <template #default="{ row }">
            <img
              v-if="row.article && row.article.cover_url"
              :src="row.article.cover_url"
              alt="cover"
              class="w-full h-16 object-cover rounded-[var(--radius-sm)] border border-[var(--border)]"
            />
            <span v-else class="text-sm text-[var(--muted-foreground)]">无封面</span>
          </template>
        </el-table-column>
        <el-table-column label="文章标题" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.article ? row.article.title : '（文章已删除）' }}
          </template>
        </el-table-column>
        <el-table-column label="分类" width="140">
          <template #default="{ row }">
            <span v-if="row.article && row.article.categories && row.article.categories.length">
              {{ row.article.categories[0].name }}
            </span>
            <span v-else class="text-sm text-[var(--muted-foreground)]">未分类</span>
          </template>
        </el-table-column>
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

      <div class="flex justify-end items-center p-4 text-sm text-[var(--muted-foreground)]">
        共 {{ filteredList.length }} 条
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
        <el-form-item label="文章">
          <el-select
            v-model="dialogForm.article_id"
            filterable
            remote
            reserve-keyword
            placeholder="搜索文章标题"
            :remote-method="searchArticles"
            :loading="articleLoading"
            style="width: 100%"
            :disabled="dialogMode === 'edit'"
          >
            <el-option
              v-for="a in articleOptions"
              :key="a.id"
              :label="a.title"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="dialogForm.sort_order" :min="0" :max="9999" />
          <span class="ml-2 text-xs text-[var(--muted-foreground)]">数值越小越靠前</span>
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
import { list as listFeatured, remove as removeFeatured, stats as fetchStats, create as createFeatured, update as updateFeatured } from '@/api/featured'
import { list as listArticles } from '@/api/article'
import StatCard from '@/components/StatCard.vue'

const featuredList = ref([])
const loading = ref(false)

const stats = reactive({ total: 0, enabled: 0, disabled: 0 })

const filters = reactive({
  status: '',
  search: '',
})

const selectedIds = ref([])
function onSelectionChange(rows) {
  selectedIds.value = rows.map((r) => r.id)
}

// 前端二次筛选（搜索关键字）
const filteredList = computed(() => {
  const kw = filters.search.trim().toLowerCase()
  if (!kw) return featuredList.value
  return featuredList.value.filter((f) => (f.article?.title || '').toLowerCase().includes(kw))
})

function onFilterChange() {
  loadFeatured()
}

async function loadFeatured() {
  loading.value = true
  try {
    const params = {}
    if (filters.status) params.status = filters.status
    const data = await listFeatured(params)
    featuredList.value = Array.isArray(data) ? data : (data?.items || [])
  } catch (e) {
    featuredList.value = []
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

// === 文章选择器 ===
const articleOptions = ref([])
const articleLoading = ref(false)

async function searchArticles(query) {
  articleLoading.value = true
  try {
    const params = { page: 1, per_page: 50 }
    if (query) params.search = query
    const data = await listArticles(params)
    articleOptions.value = data?.items || data?.list || data || []
  } catch (e) {
    articleOptions.value = []
  } finally {
    articleLoading.value = false
  }
}

// === 弹窗 ===
const dialogVisible = ref(false)
const dialogSaving = ref(false)
const dialogMode = ref('create')
const editingId = ref(null)
const dialogForm = reactive({
  article_id: null,
  sort_order: 0,
  status: 'enabled',
})

const dialogTitle = computed(() => (dialogMode.value === 'create' ? '新增推荐' : '编辑推荐'))

function openDialog(row) {
  if (row) {
    dialogMode.value = 'edit'
    editingId.value = row.id
    Object.assign(dialogForm, {
      article_id: row.article_id,
      sort_order: row.sort_order ?? 0,
      status: row.status ?? 'enabled',
    })
    // 回显当前文章
    articleOptions.value = row.article
      ? [{ id: row.article.id, title: row.article.title }]
      : []
  } else {
    dialogMode.value = 'create'
    editingId.value = null
    Object.assign(dialogForm, {
      article_id: null,
      sort_order: 0,
      status: 'enabled',
    })
    searchArticles('')
  }
  dialogVisible.value = true
}

async function onDialogSave() {
  if (!dialogForm.article_id) {
    ElMessage.warning('请选择文章')
    return
  }
  dialogSaving.value = true
  try {
    if (dialogMode.value === 'create') {
      await createFeatured({ ...dialogForm })
      ElMessage.success('创建成功')
    } else {
      await updateFeatured(editingId.value, {
        sort_order: dialogForm.sort_order,
        status: dialogForm.status,
      })
      ElMessage.success('保存成功')
    }
    dialogVisible.value = false
    loadFeatured()
    loadStats()
  } catch (e) {
    // ignore
  } finally {
    dialogSaving.value = false
  }
}

async function onDelete(row) {
  const label = row.article ? row.article.title : '该项'
  try {
    await ElMessageBox.confirm(`确定要取消推荐「${label}」吗？`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  try {
    await removeFeatured(row.id)
    ElMessage.success('删除成功')
    loadFeatured()
    loadStats()
  } catch (e) {
    // ignore
  }
}

async function onBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 个推荐项吗？`, '批量删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  try {
    await Promise.all(selectedIds.value.map((id) => removeFeatured(id)))
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadFeatured()
    loadStats()
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  loadFeatured()
  loadStats()
})
</script>
