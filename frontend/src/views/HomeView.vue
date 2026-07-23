<template>
  <div class="home-page">
    <!-- ============ 顶部导航 ============ -->
    <nav class="site-header" :class="{ scrolled: isScrolled }">
      <div class="header-inner">
        <router-link to="/" class="site-logo">
          <span class="logo-dot"></span>
          远远的天空
        </router-link>
        <nav>
          <ul class="site-nav">
            <li><router-link to="/" class="active">首页</router-link></li>
            <li><router-link to="/category">分类</router-link></li>
            <li><router-link to="/category">关于</router-link></li>
            <li><router-link to="/admin">后台</router-link></li>
          </ul>
        </nav>
      </div>
    </nav>

    <!-- ============ Hero 轮播（保留） ============ -->
    <section
      class="hero-carousel relative overflow-hidden"
      aria-roledescription="轮播图"
      aria-label="首页精选内容"
      @mouseenter="stop"
      @mouseleave="start"
    >
      <div class="relative w-full h-[560px] md:h-[640px]">
        <article
          v-for="(slide, index) in heroSlides"
          :key="index"
          class="hero-slide hero-slide--banner absolute inset-0 flex items-center justify-center"
          :class="{
            'is-active': index === currentIndex,
            'is-before': isBefore(index),
            'is-after': isAfter(index),
          }"
          role="group"
          aria-roledescription="幻灯片"
          :aria-label="`第 ${index + 1} 张，共 ${heroSlides.length} 张`"
          :aria-hidden="index !== currentIndex"
        >
          <!-- 背景图片层 -->
          <div
            v-if="slide.image_url"
            class="hero-slide-bg-image absolute inset-0 z-[0]"
            :style="{ backgroundImage: `url('${slide.image_url}')` }"
          />

          <!-- 底部渐变遮罩 -->
          <div class="hero-slide-gradient absolute inset-x-0 bottom-0 z-[1] h-[120px] md:h-[160px]" />

          <!-- 文案 -->
          <div class="relative z-10 w-full px-16 md:px-24 py-24 text-center flex flex-col items-center justify-center">
            <h1 class="hero-copy-title text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tight text-white" style="text-wrap: balance; word-break: keep-all; overflow-wrap: break-word;">
              {{ slide.title }}
            </h1>
            <p v-if="slide.subtitle" class="hero-copy-subtitle mt-3 text-sm md:text-base max-w-2xl mx-auto leading-relaxed text-white/80" style="text-wrap: balance;">
              {{ slide.subtitle }}
            </p>
            <div class="hero-copy-actions mt-7 flex flex-col sm:flex-row items-center justify-center gap-3 w-full sm:w-auto">
              <button
                class="inline-flex items-center gap-1.5 px-6 h-11 rounded-md text-sm font-medium bg-[var(--color-primary)] text-[var(--color-primary-foreground)] hover:bg-[var(--color-primary-deep)] transition-colors w-full sm:w-auto justify-center whitespace-nowrap"
                @click="scrollToArticles"
              >
                开始阅读
                <BookOpen class="w-4 h-4" />
              </button>
            </div>
          </div>
        </article>

        <!-- 上一张/下一张 -->
        <button
          type="button"
          class="hero-carousel-control absolute z-30 left-3 md:left-8 top-1/2 -translate-y-1/2 inline-flex items-center justify-center w-11 h-11 rounded-full disabled:opacity-40 disabled:cursor-not-allowed"
          :disabled="heroSlides.length <= 1"
          aria-label="上一张"
          @click="prev"
        >
          <ChevronLeft class="w-5 h-5" />
        </button>
        <button
          type="button"
          class="hero-carousel-control absolute z-30 right-3 md:right-8 top-1/2 -translate-y-1/2 inline-flex items-center justify-center w-11 h-11 rounded-full disabled:opacity-40 disabled:cursor-not-allowed"
          :disabled="heroSlides.length <= 1"
          aria-label="下一张"
          @click="next"
        >
          <ChevronRight class="w-5 h-5" />
        </button>

        <!-- 圆点指示器 -->
        <div class="absolute z-30 bottom-7 md:bottom-9 left-1/2 -translate-x-1/2 flex items-center justify-center gap-2.5" role="group" aria-label="选择幻灯片">
          <button
            v-for="(_slide, index) in heroSlides"
            :key="index"
            type="button"
            class="hero-carousel-dot"
            :class="{ 'is-active': index === currentIndex }"
            :aria-label="`切换到第 ${index + 1} 张`"
            :aria-current="index === currentIndex"
            @click="goTo(index)"
          />
        </div>
      </div>
    </section>

    <!-- ============ 精选文章 ============ -->
    <section class="section section-no-top" id="featured">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title-featured">文章推荐</h2>
          <p class="section-subtitle">每期精选，带你看见不一样的世界</p>
        </div>

        <div v-if="featuredArticles.length" class="featured-row">
          <!-- Main Card -->
          <div class="featured-main-wrap">
            <!-- 底层：当前主图（常驻，永不参与动画） -->
            <div v-if="mainFeaturedArticle" class="featured-main featured-main--base" @click="goArticle(mainFeaturedArticle.id)">
              <img v-if="mainFeaturedArticle.cover_url" :src="mainFeaturedArticle.cover_url" :alt="mainFeaturedArticle.title">
              <div v-else class="featured-main-placeholder"></div>
              <div class="featured-content">
                <div class="featured-tag">{{ getCategoryName(mainFeaturedArticle) }}</div>
                <h3>{{ mainFeaturedArticle.title }}</h3>
                <div class="featured-date">{{ formatDate(mainFeaturedArticle.published_at || mainFeaturedArticle.created_at) }}</div>
              </div>
            </div>
            <!-- 顶层：下一张（仅切换瞬间存在，淡入覆盖底层） -->
            <div v-if="pendingFeaturedArticle" class="featured-main featured-main--overlay" :class="{ 'is-fading-in': isFeaturedFading }" @click="goArticle(pendingFeaturedArticle.id)">
              <img v-if="pendingFeaturedArticle.cover_url" :src="pendingFeaturedArticle.cover_url" :alt="pendingFeaturedArticle.title">
              <div v-else class="featured-main-placeholder"></div>
              <div class="featured-content">
                <div class="featured-tag">{{ getCategoryName(pendingFeaturedArticle) }}</div>
                <h3>{{ pendingFeaturedArticle.title }}</h3>
                <div class="featured-date">{{ formatDate(pendingFeaturedArticle.published_at || pendingFeaturedArticle.created_at) }}</div>
              </div>
            </div>
          </div>

          <!-- Side Cards -->
          <div class="featured-side">
            <TransitionGroup name="featured-side-swap">
            <div
              v-for="article in sideFeaturedArticles"
              :key="article.id"
              class="featured-side-item"
              @click="swapToFeatured(featuredArticles.indexOf(article))"
            >
              <div class="fs-thumb">
                <img
                  v-if="article.cover_url"
                  :src="article.cover_url"
                  :alt="article.title"
                >
                <div v-else class="fs-thumb-placeholder"></div>
              </div>
              <div class="fs-info">
                <div class="fs-date">{{ formatDate(article.published_at || article.created_at) }}</div>
                <h4>{{ article.title }}</h4>
              </div>
            </div>
            </TransitionGroup>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 最新文章 + 侧边栏 ============ -->
    <section class="section" id="articles-section" style="padding-top: 0;">
      <div class="container">
        <div class="page-layout">

          <!-- Left: Latest Articles -->
          <div class="articles-main">
            <div class="section-header section-header-left section-header-row">
              <h2>最新文章</h2>
              <router-link to="/category" class="view-all-btn">所有文章 →</router-link>
            </div>

            <div v-if="loading" class="articles-grid">
              <div v-for="i in 6" :key="i" class="article-card">
                <div class="card-image">
                  <div class="card-image-placeholder animate-pulse"></div>
                </div>
                <div class="card-body">
                  <div class="h-3 bg-[var(--muted)] rounded w-1/3 mb-2 animate-pulse"></div>
                  <div class="h-5 bg-[var(--muted)] rounded w-3/4 mb-2 animate-pulse"></div>
                  <div class="h-3 bg-[var(--muted)] rounded w-full animate-pulse"></div>
                </div>
              </div>
            </div>

            <div v-else-if="articles.length === 0" class="py-16 text-center text-[var(--muted-foreground)]">
              暂无文章
            </div>

            <div v-else class="articles-grid">
              <div
                v-for="article in articles"
                :key="article.id"
                class="article-card scroll-reveal"
                @click="goArticle(article.id)"
              >
                <div class="card-image">
                  <img
                    v-if="article.cover_url"
                    :src="article.cover_url"
                    :alt="article.title"
                  >
                  <div v-else class="card-image-placeholder"></div>
                  <span class="card-category">{{ getCategoryName(article) }}</span>
                </div>
                <div class="card-body">
                  <div class="card-date">{{ formatDate(article.published_at || article.created_at) }}</div>
                  <h3>{{ article.title }}</h3>
                  <p class="card-excerpt">{{ article.summary }}</p>
                  <div class="card-footer">
                    <span class="card-author">远远</span>
                    <span class="card-read">阅读全文 →</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Sidebar -->
          <aside class="sidebar">
            <!-- 搜索 -->
            <div class="sidebar-widget">
              <h4>搜索文章</h4>
              <div class="search-box">
                <input
                  v-model="sidebarKeyword"
                  type="text"
                  placeholder="输入关键词..."
                  @keyup.enter="doSidebarSearch"
                >
                <button @click="doSidebarSearch" aria-label="搜索">
                  <Search class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- 分类 -->
            <div class="sidebar-widget">
              <h4>文章分类</h4>
              <ul class="category-list">
                <li>
                  <router-link
                    to="/category"
                    class="active"
                  >
                    全部文章
                    <span class="count">{{ totalCount }}</span>
                  </router-link>
                </li>
                <li v-for="cat in categories" :key="cat.id">
                  <router-link
                    :to="{ path: '/category', query: { category_id: cat.id } }"
                  >
                    {{ cat.name }}
                    <span class="count">{{ cat.article_count || 0 }}</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- 关于我 -->
            <div class="sidebar-widget">
              <h4>关于我</h4>
              <p class="about-text">
                你好，我是远远。<br>
                一个热爱旅行、摄影和写作的人。在这里记录生活中的每一个值得被记住的瞬间。
              </p>
              <p class="about-sub">
                目前正在探索世界的不同角落，用文字和镜头定格那些关于远方的想象。
              </p>
            </div>
          </aside>

        </div>
      </div>
    </section>

    <!-- ============ 页脚 ============ -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="site-logo">
            <span class="logo-dot"></span>
            远远的天空
          </div>
          <p>记录旅行、生活与远方。用文字和镜头，捕捉每一个值得被记住的瞬间。</p>
        </div>
        <div class="footer-links">
          <h4>导航</h4>
          <ul>
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/category">分类</router-link></li>
            <li><router-link to="/admin">后台管理</router-link></li>
          </ul>
        </div>
        <div class="footer-links">
          <h4>联系</h4>
          <ul>
            <li><a href="#">邮箱</a></li>
            <li><a href="#">RSS 订阅</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        © 2026 远远的天空 · Distant Sky. All rights reserved.
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChevronLeft, ChevronRight, BookOpen, Search,
} from 'lucide-vue-next'
import { list as listArticles } from '@/api/article'
import { list as listCategories } from '@/api/category'
import { list as listBanners } from '@/api/banner'
import { list as listFeatured } from '@/api/featured'

const router = useRouter()

// ============ 滚动导航 ============
const isScrolled = ref(false)
function handleScroll() {
  isScrolled.value = window.scrollY > 80
}

// ============ 搜索 ============
const sidebarKeyword = ref('')
function doSidebarSearch() {
  if (!sidebarKeyword.value.trim()) return
  router.push({ path: '/category', query: { keyword: sidebarKeyword.value.trim() } })
}

// ============ Hero 轮播 ============
const heroSlides = ref([])
const currentIndex = ref(0)
let timer = null
const interval = 5000
const reduceMotion = ref(false)

function isBefore(index) {
  if (heroSlides.value.length === 0) return false
  const forwardDistance = (index - currentIndex.value + heroSlides.value.length) % heroSlides.value.length
  return forwardDistance > heroSlides.value.length / 2
}

function isAfter(index) {
  if (index === currentIndex.value || heroSlides.value.length === 0) return false
  const forwardDistance = (index - currentIndex.value + heroSlides.value.length) % heroSlides.value.length
  return forwardDistance <= heroSlides.value.length / 2
}

function render(nextIndex) {
  if (heroSlides.value.length <= 1) return
  currentIndex.value = (nextIndex + heroSlides.value.length) % heroSlides.value.length
}

function start() {
  stop()
  if (reduceMotion.value || document.hidden || heroSlides.value.length <= 1) return
  timer = setInterval(() => render(currentIndex.value + 1), interval)
}

function stop() {
  if (timer !== null) {
    clearInterval(timer)
    timer = null
  }
}

function prev() {
  render(currentIndex.value - 1)
  start()
}

function next() {
  render(currentIndex.value + 1)
  start()
}

function goTo(index) {
  render(index)
  start()
}

function scrollToArticles() {
  const el = document.getElementById('articles-section')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

// ============ 数据加载 ============
const loading = ref(true)
const articles = ref([])
const categories = ref([])

const featuredList = ref([])
const featuredArticles = computed(() => {
  // 优先使用后台配置的推荐文章；未配置时回退到最新 4 篇
  if (featuredList.value.length) return featuredList.value
  return articles.value.slice(0, 4)
})
const featuredMainIndex = ref(0)          // 侧栏过滤/高亮依据（先变 → 小图先动）
const featuredDisplayedIndex = ref(0)     // 底层大图实际显示（后变 → 大图再换）
let featuredTimer = null

const mainFeaturedArticle = computed(() => featuredArticles.value[featuredDisplayedIndex.value])

const sideFeaturedArticles = computed(() => {
  const all = featuredArticles.value
  return all.filter((_, i) => i !== featuredMainIndex.value).slice(0, 3)
})

const featuredPendingIndex = ref(null)
const isFeaturedFading = ref(false)
let featuredBusy = false

const pendingFeaturedArticle = computed(() =>
  featuredPendingIndex.value !== null
    ? featuredArticles.value[featuredPendingIndex.value] || null
    : null
)

function preloadImage(src) {
  return new Promise((resolve) => {
    if (!src) return resolve()
    const img = new Image()
    img.onload = () => {
      img.decode ? img.decode().then(resolve, resolve) : resolve()
    }
    img.onerror = () => resolve()
    img.src = src
  })
}

async function goFeatured(globalIndex) {
  if (featuredBusy) return
  const len = featuredArticles.value.length
  if (len <= 1) return
  const target = ((globalIndex % len) + len) % len
  if (target === featuredDisplayedIndex.value) return

  featuredBusy = true
  await preloadImage(featuredArticles.value[target]?.cover_url)

  // 1) 先更新侧栏索引 → 小图立即开始动画
  featuredMainIndex.value = target

  // 2) 顶层覆盖层淡入（底层大图仍在显示旧的）
  featuredPendingIndex.value = target
  await nextTick()
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      isFeaturedFading.value = true
    })
  })

  // 3) 淡入完成后，底层换图、撤掉顶层
  setTimeout(() => {
    featuredDisplayedIndex.value = target
    featuredPendingIndex.value = null
    isFeaturedFading.value = false
    featuredBusy = false
  }, 500)
}

function swapToFeatured(globalIndex) {
  stopFeaturedTimer()
  goFeatured(globalIndex)
  startFeaturedTimer()
}

function startFeaturedTimer() {
  stopFeaturedTimer()
  if (featuredArticles.value.length <= 1) return
  featuredTimer = setInterval(() => {
    goFeatured(featuredDisplayedIndex.value + 1)
  }, 4000)
}

function stopFeaturedTimer() {
  if (featuredTimer !== null) {
    clearInterval(featuredTimer)
    featuredTimer = null
  }
}

const totalCount = computed(() => articles.value.length)

function getCategoryName(article) {
  const cats = article.categories || article.category_names || []
  return Array.isArray(cats) && cats.length ? (cats[0]?.name || cats[0]) : '未分类'
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function goArticle(id) {
  router.push(`/article/${id}`)
}

async function loadArticles() {
  try {
    const res = await listArticles({ page: 1, per_page: 6, status: 'published' })
    articles.value = res?.items || []
  } catch (e) {
    // ignore
  } finally {
    loading.value = false
    observeScrollReveal()
    startFeaturedTimer()
  }
}

async function loadCategories() {
  try {
    const res = await listCategories({ include_count: 'true' })
    categories.value = res || []
  } catch (e) {
    // ignore
  }
}

async function loadBanners() {
  try {
    const res = await listBanners({ status: 'enabled' })
    const banners = Array.isArray(res) ? res : (res?.items ?? [])
    const slides = banners.slice(0, 6).map((b) => ({
      title: b.title || '',
      subtitle: b.subtitle || '',
      image_url: b.image_url || '',
    }))
    heroSlides.value = slides
    currentIndex.value = 0
    start()
  } catch (e) {
    console.error('[HomeView] 轮播图加载失败:', e)
    heroSlides.value = []
  }
}

async function loadFeatured() {
  try {
    const res = await listFeatured({ status: 'enabled' })
    const items = Array.isArray(res) ? res : (res?.items ?? [])
    // 仅展示已发布文章
    featuredList.value = items
      .filter((f) => f.article && f.article.status === 'published')
      .map((f) => f.article)
  } catch (e) {
    featuredList.value = []
  } finally {
    startFeaturedTimer()
  }
}

// ============ Scroll Reveal ============
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

function observeScrollReveal() {
  nextTick(() => {
    document.querySelectorAll('.scroll-reveal').forEach((el) => {
      const rect = el.getBoundingClientRect()
      const isInViewport = rect.top < window.innerHeight && rect.bottom > 0
      if (isInViewport) {
        el.classList.add('is-visible')
      } else {
        observer?.observe(el)
      }
    })
  })
}

// ============ 生命周期 ============
function handleVisibilityChange() {
  if (document.hidden) {
    stop()
  } else {
    start()
  }
}

onMounted(() => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    reduceMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }

  window.addEventListener('scroll', handleScroll)
  loadArticles()
  loadCategories()
  loadBanners()
  loadFeatured()
  setupScrollReveal()
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  stop()
  stopFeaturedTimer()
  observer?.disconnect()
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
/* === Fonts === */
.home-page {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  color: #1a1a1c;
  background: #fdfaf5;
  line-height: 1.75;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* === Grain texture overlay === */
.home-page::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
}

/* === Typography === */
.home-page h1, .home-page h2, .home-page h3, .home-page h4 {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 700;
  line-height: 1.3;
  color: #1a1a1c;
}

.home-page .hero-slide h1 {
  color: #ffffff;
}

/* === Layout Helpers === */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section {
  padding: 3rem 0;
}

.section-no-top {
  padding-top: 0;
}

.section-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.section-header-left {
  text-align: left;
  margin-bottom: 1.5rem;
}

.section-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.view-all-btn {
  font-family: 'Noto Serif SC', 'STSong', 'Songti SC', 'SimSun', serif;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #d4856b;
  text-decoration: none;
  transition: color 0.3s ease;
  white-space: nowrap;
}

.view-all-btn:hover {
  color: #b06a54;
}

.section-header h2 {
  font-family: 'Noto Serif SC', 'STSong', 'Songti SC', 'SimSun', serif;
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  letter-spacing: 0.02em;
}

.section-title-featured {
  font-size: 22px !important;
}

.section-subtitle {
  font-size: 0.9rem;
  color: #6b6b72;
}

/* === Header === */
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
  color: #ffffff;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.logo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d4856b;
  display: inline-block;
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
  color: #ffffff;
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
  color: #ffffff;
}

.site-nav a:hover::after,
.site-nav a.active::after {
  width: 100%;
}

/* === Featured Row === */
.featured-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 2rem;
}

.featured-main {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  height: 460px;
  cursor: pointer;
}

.featured-main img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 20px;
  transition: transform 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.featured-main:hover img {
  transform: scale(1.05);
}

.featured-main::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(26, 26, 28, 0.7) 0%, transparent 50%);
}

.featured-main-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #8bb8c9 0%, #5b8ba0 100%);
}

.featured-main .featured-content {
  position: absolute;
  bottom: 2rem;
  left: 2rem;
  right: 2rem;
  z-index: 2;
}

.featured-main .featured-tag {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #e8a894;
  margin-bottom: 0.5rem;
}

.featured-main h3 {
  color: #fffefa;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.featured-main .featured-date {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.65);
}

.featured-side {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 460px;
}

.featured-side-item {
  display: grid;
  grid-template-columns: 40% 60%;
  background: #fffefa;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  box-shadow: 0 1px 2px rgba(26, 26, 28, 0.06);
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.featured-side-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(26, 26, 28, 0.1);
}

.fs-thumb {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.fs-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fs-thumb-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #dbb87a 0%, #c49a5c 100%);
}

.fs-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem;
  min-width: 0;
}

.fs-date {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 0.7rem;
  color: #6b6b72;
  margin-bottom: 4px;
}

.featured-side-item h4 {
  font-family: 'Noto Serif SC', 'STSong', 'Songti SC', 'SimSun', serif;
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* === Articles Grid === */
.page-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2.5rem;
  align-items: start;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.article-card {
  position: relative;
  background: #fffefa;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(26, 26, 28, 0.06);
  transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
  cursor: pointer;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(26, 26, 28, 0.1);
}

.article-card .card-image {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #f0ebe0;
}

.article-card .card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.article-card:hover .card-image img {
  transform: scale(1.05);
}

.card-image-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #8bb8c9 0%, #5b8ba0 100%);
}

.article-card .card-category {
  position: absolute;
  top: 1rem;
  left: 1rem;
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  background: rgba(253, 250, 245, 0.9);
  backdrop-filter: blur(8px);
  color: #3a6375;
  padding: 4px 12px;
  border-radius: 100px;
}

.article-card .card-body {
  padding: 1.5rem;
}

.article-card .card-date {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 0.75rem;
  color: #6b6b72;
  margin-bottom: 0.5rem;
}

.article-card h3 {
  font-family: 'Noto Serif SC', 'STSong', 'Songti SC', 'SimSun', serif;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-card .card-excerpt {
  font-family: 'Noto Serif SC', 'STSong', 'Songti SC', 'SimSun', serif;
  font-size: 12px;
  color: #3d3d42;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-card .card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e8e2d4;
}

.article-card .card-author {
  font-size: 0.8rem;
  color: #6b6b72;
}

.article-card .card-read {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #d4856b;
}

/* === Sidebar === */
.sidebar {
  position: sticky;
  top: 100px;
}

.sidebar-widget {
  background: #fffefa;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 2px rgba(26, 26, 28, 0.06);
}

.sidebar-widget h4 {
  font-family: 'Noto Serif SC', 'STSong', 'Songti SC', 'SimSun', serif;
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-widget h4::before {
  content: '';
  width: 3px;
  height: 18px;
  background: #d4856b;
  border-radius: 2px;
}

.search-box {
  display: flex;
  gap: 0.5rem;
}

.search-box input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d9d2c4;
  border-radius: 8px;
  background: #fffefa;
  color: #1a1a1c;
  font-size: 0.9rem;
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  outline: none;
  transition: all 0.3s ease;
}

.search-box input:focus {
  border-color: #5b8ba0;
  box-shadow: 0 0 0 3px rgba(91, 139, 160, 0.1);
}

.search-box button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #1a1a1c;
  color: #fffefa;
  border: none;
  cursor: pointer;
  transition: background 0.3s ease;
  flex-shrink: 0;
}

.search-box button:hover {
  background: #3d3d42;
}

.category-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.category-list li {
  margin-bottom: 2px;
}

.category-list a {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #3d3d42;
  text-decoration: none;
  transition: all 0.3s ease;
}

.category-list a:hover,
.category-list a.active {
  background: #faf6f0;
  color: #1a1a1c;
}

.category-list .count {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 0.75rem;
  color: #6b6b72;
  background: #faf6f0;
  padding: 2px 8px;
  border-radius: 100px;
}

.about-text {
  font-size: 0.875rem;
  color: #3d3d42;
  line-height: 1.7;
  margin-bottom: 1rem;
}

.about-sub {
  font-size: 0.8rem;
  color: #6b6b72;
  line-height: 1.6;
}

/* === Footer === */
.site-footer {
  border-top: 1px solid #d9d2c4;
  padding: 2rem 0 0;
  background: #fffefa;
  margin-top: 2rem;
}

.footer-inner {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-brand .site-logo {
  margin-bottom: 1rem;
  color: #1a1a1c;
}

.footer-brand p {
  font-size: 0.875rem;
  color: #4a4a50;
  line-height: 1.6;
}

.footer-links h4 {
  font-family: 'Noto Serif SC', 'STSong', 'Songti SC', 'SimSun', serif;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.footer-links ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-links a {
  font-size: 0.85rem;
  color: #4a4a50;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-links a:hover {
  color: #d4856b;
}

.footer-bottom {
  text-align: center;
  padding: 1.5rem 2rem;
  font-size: 0.8rem;
  color: #4a4a50;
  border-top: 1px solid #e8e2d4;
  margin-top: 1.5rem;
}

/* === Hero Slide（保留原轮播逻辑） === */
.hero-slide {
  opacity: 0;
  transform: translateX(7%);
  visibility: hidden;
  pointer-events: none;
  transition: opacity 700ms ease, transform 700ms ease, visibility 700ms step-end;
}

.hero-slide--banner {
  background: #fdfaf5;
}

.hero-slide-bg-image {
  position: absolute;
  inset: 0;
  z-index: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.hero-slide-gradient {
  background: linear-gradient(to bottom, transparent 0%, rgba(253, 250, 245, 0.6) 70%, #fdfaf5 95%);
}

.hero-slide.is-active {
  z-index: 10;
  opacity: 1;
  transform: translateX(0);
  visibility: visible;
  pointer-events: auto;
  transition: opacity 700ms ease, transform 700ms ease, visibility 0ms step-start;
}

.hero-slide.is-before {
  transform: translateX(-7%);
}

.hero-slide.is-after {
  transform: translateX(7%);
}

.hero-copy-title,
.hero-copy-subtitle,
.hero-copy-actions {
  opacity: 0;
  transform: translateX(1.25rem);
  transition: opacity 520ms ease, transform 520ms ease;
}

.hero-slide.is-active .hero-copy-title {
  opacity: 1;
  transform: translateX(0);
  transition-delay: 80ms;
}

.hero-slide.is-active .hero-copy-subtitle {
  opacity: 1;
  transform: translateX(0);
  transition-delay: 160ms;
}

.hero-slide.is-active .hero-copy-actions {
  opacity: 1;
  transform: translateX(0);
  transition-delay: 240ms;
}

/* === 轮播控制按钮（隐藏式） === */
.hero-carousel-control {
  position: absolute;
  z-index: 100;
  color: #1a1a1c;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  pointer-events: auto;
  opacity: 0;
  transition: opacity 280ms ease, background-color 200ms ease, scale 180ms ease;
}

.hero-carousel:hover .hero-carousel-control {
  opacity: 1;
}

.hero-carousel-control:hover {
  background: #fffefa;
  border-color: #d9d2c4;
}

.hero-carousel-control:active {
  scale: 0.96;
}

/* === 圆点指示器 === */
.hero-carousel-dot {
  z-index: 40;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.4);
  transition: width 260ms ease, background-color 260ms ease;
  cursor: pointer;
  pointer-events: auto;
  border: none;
  padding: 0;
}

.hero-carousel-dot.is-active {
  width: 1.75rem;
  border-radius: 4px;
  background: #fffefa;
}

/* === Scroll Reveal === */
.scroll-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.scroll-reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* === Featured 双层切换 === */
.featured-main-wrap {
  position: relative;
}

.featured-main--base {
  z-index: 1;
}

.featured-main--overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  opacity: 0;
  transition: opacity 0.45s ease;
}

.featured-main--overlay.is-fading-in {
  opacity: 1;
}

/* === Featured 侧栏切换过渡 === */
.featured-side-swap-move,
.featured-side-swap-enter-active,
.featured-side-swap-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.featured-side-swap-enter-from,
.featured-side-swap-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.featured-side-swap-leave-active {
  position: absolute;
  right: 0;
  left: 0;
}

/* === Responsive === */
@media (max-width: 1024px) {
  .articles-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }

  .featured-row {
    grid-template-columns: 1fr;
  }

  .featured-main {
    height: 300px;
  }

  .footer-inner {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .articles-grid {
    grid-template-columns: 1fr;
  }

  .site-nav {
    display: none;
  }

  .footer-inner {
    grid-template-columns: 1fr;
  }

  .section {
    padding: 2rem 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-slide,
  .hero-slide.is-active,
  .hero-copy-title,
  .hero-copy-subtitle,
  .hero-copy-actions,
  .hero-slide.is-active .hero-copy-title,
  .hero-slide.is-active .hero-copy-subtitle,
  .hero-slide.is-active .hero-copy-actions,
  .hero-carousel-control,
  .hero-carousel-dot,
  .featured-main--overlay,
  .scroll-reveal,
  .scroll-reveal.is-visible {
    transition-duration: 1ms !important;
    transition-delay: 0ms !important;
  }
}
</style>
