<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-start justify-between gap-4 mb-6">
      <div class="min-w-0">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--foreground)]">仪表盘</h1>
        <p class="mt-1.5 text-sm text-[var(--muted-foreground)]">站点概览与数据</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard label="文章总数" :value="stats.total" color="var(--color-primary)" />
      <StatCard label="已发布" :value="stats.published" color="var(--chart-1)" />
      <StatCard label="草稿" :value="stats.draft" color="var(--chart-4)" />
      <StatCard label="今日新增" :value="stats.today_new" color="var(--chart-3)" />
    </div>

    <!-- 最近文章 -->
    <div
      class="bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-lg)] p-5"
    >
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">最近文章</h2>
        <router-link to="/admin/articles" class="text-sm text-[var(--color-primary)] hover:underline">
          查看全部
        </router-link>
      </div>

      <el-table :data="recent" v-loading="loadingRecent" stripe>
        <el-table-column prop="title" label="标题" min-width="220" />
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
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            <span class="text-sm text-[var(--muted-foreground)]">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { list as listArticles, stats as fetchStats } from '@/api/article'
import StatCard from '@/components/StatCard.vue'

const stats = reactive({ total: 0, published: 0, draft: 0, today_new: 0 })
const recent = ref([])
const loadingRecent = ref(false)

function formatDate(d) {
  if (!d) return '-'
  const date = new Date(d)
  return date.toLocaleString('zh-CN', { hour12: false })
}

async function loadStats() {
  try {
    const data = await fetchStats()
    Object.assign(stats, data || {})
  } catch (e) {
    // 静默失败，错误已由拦截器提示
  }
}

async function loadRecent() {
  loadingRecent.value = true
  try {
    const data = await listArticles({ page: 1, per_page: 5 })
    recent.value = data?.items || data?.list || data || []
  } catch (e) {
    recent.value = []
  } finally {
    loadingRecent.value = false
  }
}

onMounted(() => {
  loadStats()
  loadRecent()
})
</script>
