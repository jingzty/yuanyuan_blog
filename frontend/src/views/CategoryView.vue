<template>
  <div class="category-page">
    <!-- 顶部导航（与首页一致） -->
    <nav class="site-header" :class="{ scrolled: true }">
      <div class="header-inner">
        <router-link to="/" class="site-logo">
          <CloudSun class="logo-icon" />
          远远的天空
        </router-link>
        <nav>
          <ul class="site-nav">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/category" class="active">分类</router-link></li>
            <li><router-link to="/category">关于</router-link></li>
            <li><router-link to="/admin">后台</router-link></li>
          </ul>
        </nav>
      </div>
    </nav>

    <main class="category-container">
      <!-- 页头 -->
      <header class="category-header">
        <h1 class="category-title">{{ pageTitle }}</h1>
        <p class="category-desc">{{ pageDescription }}</p>
      </header>

      <!-- 分类筛选条 -->
      <div class="category-filter">
        <div class="category-filter-list">
          <button
            class="category-chip"
            :class="{ 'is-active': !selectedCategoryId }"
            @click="selectCategory(null)"
          >
            全部
          </button>
          <button
            v-for="cat in categories"
            :key="cat.id"
            class="category-chip"
            :class="{ 'is-active': selectedCategoryId === cat.id }"
            @click="selectCategory(cat.id)"
          >
            {{ cat.name }}
            <span class="category-chip-count">{{ cat.article_count || 0 }}</span>
          </button>
        </div>
      </div>

      <!-- 搜索框 -->
      <div class="category-search">
        <div class="category-search-box">
          <div class="category-search-input-wrap">
            <Search class="category-search-icon" />
            <input
              v-model="keyword"
              type="text"
              placeholder="搜索文章..."
              class="category-search-input"
              @keyup.enter="search"
            >
          </div>
          <button class="category-search-btn" @click="search">
            搜索
          </button>
        </div>
      </div>

      <!-- 文章列表 -->
      <div v-if="loading" class="category-loading">
        <div v-for="i in 3" :key="i" class="loading-card">
          <div class="loading-line w-1/4"></div>
          <div class="loading-line w-3/4"></div>
          <div class="loading-line w-full"></div>
        </div>
      </div>

      <div v-else-if="articles.length === 0" class="category-empty">
        <FileQuestion class="category-empty-icon" />
        <p>暂无文章</p>
      </div>

      <div v-else class="category-list">
        <ArticleCard
          v-for="article in articles"
          :key="article.id"
          :article="article"
          class="scroll-reveal"
        />

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="category-pagination">
          <button
            class="page-btn"
            :disabled="currentPage <= 1"
            @click="changePage(currentPage - 1)"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>

          <button
            v-for="p in displayPages"
            :key="p"
            class="page-btn page-btn--num"
            :class="{ 'is-active': p === currentPage }"
            @click="changePage(p)"
          >
            {{ p }}
          </button>

          <button
            class="page-btn"
            :disabled="currentPage >= totalPages"
            @click="changePage(currentPage + 1)"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search, ChevronLeft, ChevronRight, FileQuestion, CloudSun,
} from 'lucide-vue-next'
import { list as listArticles } from '@/api/article'
import { list as listCategories } from '@/api/category'
import ArticleCard from '@/components/ArticleCard.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const articles = ref([])
const categories = ref([])
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(10)
const selectedCategoryId = ref(null)
const keyword = ref('')

const totalPages = computed(() => Math.ceil(total.value / perPage.value) || 1)

const displayPages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const pageTitle = computed(() => {
  if (keyword.value) return `搜索：${keyword.value}`
  if (selectedCategoryId.value) {
    const cat = categories.value.find((c) => c.id === selectedCategoryId.value)
    return cat ? `${cat.name}` : '分类'
  }
  return '全部文章'
})

const pageDescription = computed(() => {
  if (keyword.value) return `找到 ${total.value} 篇相关文章`
  if (selectedCategoryId.value) {
    const cat = categories.value.find((c) => c.id === selectedCategoryId.value)
    return cat ? `共 ${cat.article_count || 0} 篇文章` : ''
  }
  return `共 ${total.value} 篇文章`
})

async function loadCategories() {
  try {
    const res = await listCategories({ include_count: 'true' })
    categories.value = res || []
  } catch (e) {
    // ignore
  }
}

async function loadArticles() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: perPage.value,
      status: 'published',
    }
    if (selectedCategoryId.value) params.category_id = selectedCategoryId.value
    if (keyword.value) params.keyword = keyword.value

    const res = await listArticles(params)
    articles.value = res?.items || []
    total.value = res?.total || 0
  } catch (e) {
    // ignore
  } finally {
    loading.value = false
  }
}

function selectCategory(id) {
  selectedCategoryId.value = id
  currentPage.value = 1
  updateQuery()
  loadArticles()
}

function search() {
  currentPage.value = 1
  updateQuery()
  loadArticles()
}

function changePage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  updateQuery()
  loadArticles()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function updateQuery() {
  const query = {}
  if (selectedCategoryId.value) query.category_id = selectedCategoryId.value
  if (keyword.value) query.keyword = keyword.value
  if (currentPage.value > 1) query.page = currentPage.value
  router.replace({ path: '/category', query })
}

function parseQuery() {
  const q = route.query
  selectedCategoryId.value = q.category_id ? Number(q.category_id) : null
  keyword.value = q.keyword || ''
  currentPage.value = q.page ? Number(q.page) : 1
}

// Scroll Reveal
let observer = null
function setupScrollReveal() {
  if (typeof IntersectionObserver === 'undefined') return
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' },
  )
}

watch(() => route.query, () => {
  parseQuery()
  loadArticles()
})

onMounted(async () => {
  parseQuery()
  await Promise.all([loadCategories(), loadArticles()])
  setupScrollReveal()
  nextTick(() => {
    document.querySelectorAll('.scroll-reveal').forEach((el) => {
      observer?.observe(el)
    })
  })
})
</script>

<style scoped>
/* ============ 页面容器 ============ */
.category-page {
  min-height: 100vh;
  background: #fdfaf5;
  color: #1a1a1c;
}

/* ============ 顶部导航（与首页一致） ============ */
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 1.5rem 0;
  transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.site-header.scrolled {
  background: rgba(253, 250, 245, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 1px 0 #e8e2d4;
  padding: 1rem 0;
}

.site-header.scrolled .site-logo {
  color: #1a1a1c;
}

.site-header.scrolled .site-nav a,
.site-header.scrolled .site-nav a:hover,
.site-header.scrolled .site-nav a.active {
  color: #1a1a1c;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.site-logo {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a1a1c;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.logo-icon {
  width: 22px;
  height: 22px;
  color: #d4856b;
}

.site-nav {
  display: flex;
  align-items: center;
  gap: 2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.site-nav a {
  font-size: 0.875rem;
  color: #1a1a1c;
  position: relative;
  padding: 0.25rem 0;
  text-decoration: none;
  transition: color 0.3s ease;
}

.site-nav a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1.5px;
  background: #d4856b;
  transition: width 0.3s ease;
}

.site-nav a:hover,
.site-nav a.active {
  color: #1a1a1c;
}

.site-nav a:hover::after,
.site-nav a.active::after {
  width: 100%;
}

/* ============ 主容器 ============ */
.category-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 120px 1.5rem 4rem;
}

/* ============ 页头 ============ */
.category-header {
  margin-bottom: 2.5rem;
}

.category-title {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1.3;
  color: #1a1a1c;
  margin-bottom: 0.75rem;
  letter-spacing: -0.01em;
}

@media (min-width: 768px) {
  .category-title {
    font-size: 2.25rem;
  }
}

.category-desc {
  font-size: 0.875rem;
  color: #6b6b72;
}

/* ============ 分类筛选 ============ */
.category-filter {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e8e2d4;
}

.category-filter-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.category-chip {
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  background: #efe9dc;
  color: #6b6b72;
  transition: all 0.3s ease;
}

.category-chip:hover {
  background: #f0f5ff;
  color: #004acc;
}

.category-chip.is-active {
  background: #d4856b;
  color: #ffffff;
}

.category-chip-count {
  margin-left: 0.25rem;
  opacity: 0.7;
}

/* ============ 搜索框 ============ */
.category-search {
  margin-bottom: 2rem;
}

.category-search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 480px;
}

.category-search-input-wrap {
  position: relative;
  flex: 1;
}

.category-search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: #6b6b72;
}

.category-search-input {
  width: 100%;
  height: 2.5rem;
  padding: 0 0.75rem 0 2.25rem;
  font-size: 0.875rem;
  border-radius: 0.375rem;
  border: 1px solid #e8e2d4;
  background: #fdfaf5;
  color: #1a1a1c;
  outline: none;
  transition: border-color 0.3s ease;
}

.category-search-input:focus {
  border-color: #d4856b;
}

.category-search-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  height: 2.5rem;
  border-radius: 0.375rem;
  background: #d4856b;
  color: #ffffff;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.3s ease;
}

.category-search-btn:hover {
  background: #b86b50;
}

/* ============ 加载占位 ============ */
.category-loading {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading-card {
  height: 8rem;
  border-radius: 1.2rem;
  border: 1px solid #e8e2d4;
  background: #ffffff;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.loading-line {
  height: 0.875rem;
  background: #efe9dc;
  border-radius: 0.25rem;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ============ 空状态 ============ */
.category-empty {
  padding: 4rem 0;
  text-align: center;
  color: #6b6b72;
}

.category-empty-icon {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 1rem;
  opacity: 0.3;
}

/* ============ 文章列表 ============ */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* ============ 分页 ============ */
.category-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 2.5rem;
}

.page-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.375rem;
  border: 1px solid #e8e2d4;
  color: #6b6b72;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #efe9dc;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn--num {
  min-width: 2.25rem;
  padding: 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.page-btn--num.is-active {
  background: #d4856b;
  color: #ffffff;
  border-color: #d4856b;
}

/* ============ 滚动揭示 ============ */
.scroll-reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}

.scroll-reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .scroll-reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
