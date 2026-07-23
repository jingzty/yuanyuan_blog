<template>
  <article
    class="article-card scroll-reveal group cursor-pointer flex flex-col p-4 rounded-[1.2rem] bg-[var(--card)] hover:bg-[var(--muted)] transition-colors"
    @click="goDetail"
  >
    <div class="flex flex-col sm:flex-row gap-5">
      <!-- 封面 -->
      <div class="w-full sm:w-[200px] h-[140px] sm:h-[160px] shrink-0 rounded-[0.8rem] relative overflow-hidden">
        <img
          v-if="article.cover_url"
          :src="article.cover_url"
          :alt="article.title"
          class="absolute inset-0 w-full h-full object-cover"
        >
        <div
          v-else
          class="absolute inset-0 w-full h-full"
          :style="{ background: gradient }"
        >
          <component :is="icon" class="absolute inset-0 m-auto w-8 h-8 text-white/70" />
        </div>
      </div>

      <!-- 内容 -->
      <div class="flex-1 min-w-0 flex flex-col">
        <div class="flex items-center gap-2 mb-2">
          <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-[var(--accent)] text-[var(--color-primary-deep)]">
            {{ primaryCategory }}
          </span>
          <span class="text-xs text-[var(--muted-foreground)]">{{ formatDate(article.published_at || article.created_at) }}</span>
        </div>
        <h3 class="text-lg font-semibold text-[var(--foreground)] group-hover:text-[var(--color-primary)] transition-colors line-clamp-1">
          {{ article.title }}
        </h3>
        <p class="mt-2 text-sm text-[var(--muted-foreground)] line-clamp-2 flex-1">
          {{ article.summary }}
        </p>
        <div class="mt-3 flex items-center gap-4 text-xs text-[var(--muted-foreground)]">
          <span class="inline-flex items-center gap-1">
            <Eye class="w-3.5 h-3.5" />
            {{ article.view_count || 0 }}
          </span>
          <span v-if="tags.length" class="inline-flex items-center gap-1">
            <Tag class="w-3.5 h-3.5" />
            {{ tags.join(', ') }}
          </span>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Eye, Tag, Cpu, Database, Terminal, Boxes, Bot, Code2 } from 'lucide-vue-next'

const props = defineProps({
  article: { type: Object, required: true },
})

const router = useRouter()

// 根据分类或 id 选取封面渐变
const gradients = [
  'linear-gradient(135deg, #a9c6ff 0%, #7da3ff 50%, #557fff 100%)',
  'linear-gradient(135deg, #7da3ff 0%, #557fff 50%, #0065fd 100%)',
  'linear-gradient(135deg, #557fff 0%, #0065fd 50%, #0043ad 100%)',
  'linear-gradient(135deg, #a9c6ff 0%, #557fff 50%, #0065fd 100%)',
  'linear-gradient(135deg, #7da3ff 0%, #0065fd 50%, #0043ad 100%)',
]
const icons = [Cpu, Database, Terminal, Boxes, Bot]
const gradient = computed(() => gradients[(props.article.id || 0) % gradients.length])
const icon = computed(() => icons[(props.article.id || 0) % icons.length])

const primaryCategory = computed(() => {
  const cats = props.article.categories || props.article.category_names || []
  return Array.isArray(cats) && cats.length ? (cats[0]?.name || cats[0]) : '未分类'
})

const tags = computed(() => {
  // 如果后端有 tags 字段则用，否则从分类派生
  if (props.article.tags) return props.article.tags
  const cats = props.article.categories || props.article.category_names || []
  return Array.isArray(cats) ? cats.slice(1, 3).map((c) => (c?.name || c)) : []
})

function formatDate(d) {
  if (!d) return ''
  const s = String(d)
  // 强制 UTC 解析，避免浏览器时区差异
  const ds = /\d$/.test(s) ? s + 'Z' : s
  return new Date(ds).toLocaleDateString('zh-CN')
}

function goDetail() {
  router.push({ path: `/article/${props.article.id}` })
}
</script>
