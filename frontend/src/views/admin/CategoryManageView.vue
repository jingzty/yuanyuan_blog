<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-start justify-between gap-4 mb-6">
      <div class="min-w-0">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--foreground)]">分类管理</h1>
        <p class="mt-1.5 text-sm text-[var(--muted-foreground)]">管理文章分类</p>
      </div>
      <button
        class="shrink-0 inline-flex items-center gap-1.5 px-4 h-10 rounded-[var(--radius-md)] bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-deep)] active:translate-y-px transition-all"
        @click="openDialog()"
      >
        <Plus class="w-4 h-4" />
        <span>新建分类</span>
      </button>
    </div>

    <!-- 表格 -->
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-lg)] overflow-hidden">
      <el-table :data="categories" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column label="文章数" width="120">
          <template #default="{ row }">
            <span class="text-sm tabular-nums">{{ row.article_count ?? row.count ?? 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            <span class="text-sm text-[var(--muted-foreground)]">{{ formatDate(row.created_at) }}</span>
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
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="420px"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form :model="dialogForm" label-width="60px">
        <el-form-item label="名称">
          <el-input v-model="dialogForm.name" placeholder="请输入分类名称" />
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
import { list as listCategories, create as createCategory, update as updateCategory, remove as removeCategory } from '@/api/category'

const categories = ref([])
const loading = ref(false)

async function loadCategories() {
  loading.value = true
  try {
    const data = await listCategories({ include_count: true })
    categories.value = data?.items || data?.list || data || []
  } catch (e) {
    categories.value = []
  } finally {
    loading.value = false
  }
}

function formatDate(d) {
  if (!d) return '-'
  const s = String(d)
  const ds = /\d$/.test(s) ? s + 'Z' : s
  return new Date(ds).toLocaleString('zh-CN', { hour12: false })
}

// 弹窗
const dialogVisible = ref(false)
const dialogSaving = ref(false)
const dialogMode = ref('create')
const editingId = ref(null)
const dialogForm = reactive({
  name: '',
})

const dialogTitle = computed(() => (dialogMode.value === 'create' ? '新建分类' : '编辑分类'))

function openDialog(row) {
  if (row) {
    dialogMode.value = 'edit'
    editingId.value = row.id
    dialogForm.name = row.name ?? ''
  } else {
    dialogMode.value = 'create'
    editingId.value = null
    dialogForm.name = ''
  }
  dialogVisible.value = true
}

async function onDialogSave() {
  if (!dialogForm.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  dialogSaving.value = true
  try {
    if (dialogMode.value === 'create') {
      await createCategory({ name: dialogForm.name })
      ElMessage.success('创建成功')
    } else {
      await updateCategory(editingId.value, { name: dialogForm.name })
      ElMessage.success('保存成功')
    }
    dialogVisible.value = false
    loadCategories()
  } catch (e) {
    // ignore
  } finally {
    dialogSaving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除分类「${row.name}」吗？`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  try {
    await removeCategory(row.id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  loadCategories()
})
</script>
