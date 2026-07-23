<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-start justify-between gap-4 mb-6">
      <div class="min-w-0">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--foreground)]">文章管理</h1>
        <p class="mt-1.5 text-sm text-[var(--muted-foreground)]">管理博客所有文章</p>
      </div>
      <router-link
        to="/admin/articles/edit"
        class="shrink-0 inline-flex items-center gap-1.5 px-4 h-10 rounded-[var(--radius-md)] bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-deep)] active:translate-y-px transition-all"
      >
        <Plus class="w-4 h-4" />
        <span>新建文章</span>
      </router-link>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard label="文章总数" :value="stats.total" color="var(--color-primary)" />
      <StatCard label="已发布" :value="stats.published" color="var(--chart-1)" />
      <StatCard label="草稿" :value="stats.draft" color="var(--chart-4)" />
      <StatCard label="今日新增" :value="stats.today_new" color="var(--chart-3)" />
    </div>

    <!-- 筛选 + 搜索 + 批量操作 -->
    <div
      class="bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-lg)] p-4 mb-4 flex flex-wrap items-center gap-3"
    >
      <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px" @change="onFilterChange">
        <el-option label="已发布" value="published" />
        <el-option label="草稿" value="draft" />
      </el-select>

      <el-select v-model="filters.category_id" placeholder="全部分类" clearable filterable style="width: 180px" @change="onFilterChange">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>

      <el-input
        v-model="filters.search"
        placeholder="搜索文章标题"
        clearable
        style="width: 240px"
        @change="onFilterChange"
      >
        <template #prefix>
          <Search class="w-4 h-4 text-[var(--muted-foreground)]" />
        </template>
      </el-input>

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
      <el-table
        :data="articles"
        v-loading="loading"
        @selection-change="onSelectionChange"
        row-key="id"
        stripe
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="分类" width="160">
          <template #default="{ row }">
            <span class="text-sm text-[var(--muted-foreground)]">{{ formatCategories(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span
              class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs"
              :style="
                row.status === 'published'
                  ? 'background: var(--accent); color: var(--accent-foreground)'
                  : 'background: var(--secondary); color: var(--secondary-foreground)'
              "
            >
              <span
                class="w-1.5 h-1.5 rounded-full"
                :style="row.status === 'published' ? 'background: var(--color-primary)' : 'background: var(--muted-foreground)'"
              />
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布时间" width="180">
          <template #default="{ row }">
            <span class="text-sm text-[var(--muted-foreground)]">{{ formatDate(row.published_at || row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="阅读量" width="100">
          <template #default="{ row }">
            <span class="text-sm tabular-nums">{{ row.view_count ?? row.views ?? 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="onEdit(row)">
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
          @current-change="loadArticles"
          @size-change="loadArticles"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Trash2, Pencil } from 'lucide-vue-next'
import { list as listArticles, remove as removeArticle, batchRemove as batchRemoveArticles, stats as fetchStats } from '@/api/article'
import { list as listCategories } from '@/api/category'
import StatCard from '@/components/StatCard.vue'

const router = useRouter()

const articles = ref([])
const categories = ref([])
const loading = ref(false)

const stats = reactive({ total: 0, published: 0, draft: 0, today_new: 0 })

const filters = reactive({
  status: '',
  category_id: '',
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
  loadArticles()
}

async function loadArticles() {
  loading.value = true
  try {
    const params = {
      page: page.current,
      per_page: page.size,
    }
    if (filters.status) params.status = filters.status
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.search) params.search = filters.search
    const data = await listArticles(params)
    articles.value = data?.items || data?.list || data || []
    page.total = data?.total ?? articles.value.length
  } catch (e) {
    articles.value = []
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const data = await listCategories({ include_count: true })
    categories.value = data?.items || data?.list || data || []
  } catch (e) {
    categories.value = []
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

function onEdit(row) {
  router.push(`/admin/articles/edit/${row.id}`)
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除文章「${row.title}」吗？`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  try {
    await removeArticle(row.id)
    ElMessage.success('删除成功')
    loadArticles()
    loadStats()
  } catch (e) {
    // 错误已提示
  }
}

async function onBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 篇文章吗？`, '批量删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  try {
    await batchRemoveArticles(selectedIds.value)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadArticles()
    loadStats()
  } catch (e) {
    // ignore
  }
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

function formatCategories(row) {
  if (Array.isArray(row.categories) && row.categories.length) {
    return row.categories.map((c) => c.name || c).join('、')
  }
  if (row.category_name) return row.category_name
  return '-'
}

onMounted(() => {
  loadCategories()
  loadArticles()
  loadStats()
})
</script>
