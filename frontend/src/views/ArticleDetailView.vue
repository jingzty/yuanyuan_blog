<template>
  <div class="article-page">
    <!-- 阅读进度条 -->
    <div class="read-progress-bar">
      <div
        class="read-progress-fill"
        :style="{ width: `${readProgress}%` }"
      />
    </div>

    <!-- 顶部导航（与首页一致） -->
    <nav class="site-header" :class="{ scrolled: true }">
      <div class="header-inner">
        <router-link to="/" class="site-logo">
          <span class="logo-dot"></span>
          远远的天空
        </router-link>
        <nav>
          <ul class="site-nav">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/category">分类</router-link></li>
            <li><router-link to="/category">关于</router-link></li>
            <li><router-link to="/admin">后台</router-link></li>
          </ul>
        </nav>
      </div>
    </nav>

    <!-- 加载中 -->
    <div v-if="loading" class="article-container">
      <div class="article-loading">
        <div class="loading-line w-3/4"></div>
        <div class="loading-line w-1/2"></div>
        <div class="loading-line w-full"></div>
        <div class="loading-line w-5/6"></div>
        <div class="loading-line w-4/5"></div>
      </div>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="article-container text-center">
      <p class="article-error">{{ error }}</p>
      <router-link to="/" class="back-btn">
        <ArrowLeft class="back-btn-icon" />
        <span>返回首页</span>
      </router-link>
    </div>

    <!-- 文章主体 -->
    <main v-else class="article-container">
      <!-- 返回 -->
      <router-link to="/" class="back-btn">
        <ArrowLeft class="back-btn-icon" />
        <span>返回首页</span>
      </router-link>

      <!-- 文章头部 -->
      <header class="mb-10">
        <h1 class="article-title">
          {{ article.title }}
        </h1>

        <div class="article-meta">
          <span class="article-meta-item">
            <Calendar class="w-4 h-4" />
            {{ formatDate(article.published_at || article.created_at) }}
          </span>
          <span class="article-meta-item">
            <Eye class="w-4 h-4" />
            {{ article.view_count || 0 }} 次阅读
          </span>
          <span v-if="readingTime" class="article-meta-item">
            <Clock class="w-4 h-4" />
            约 {{ readingTime }} 分钟
          </span>
        </div>
      </header>

      <!-- 封面图 -->
      <div v-if="article.cover_url" class="article-cover">
        <img :src="article.cover_url" :alt="article.title">
      </div>

      <!-- 文章正文 -->
      <div class="article-content" v-html="renderedContent" />

      <!-- 文章底部 -->
      <footer class="article-footer">
        <div class="article-tags">
          <span class="article-tags-label">标签：</span>
          <router-link
            v-for="cat in article.categories"
            :key="cat.id"
            :to="{ path: '/category', query: { category_id: cat.id } }"
            class="article-category-tag"
          >
            {{ cat.name }}
          </router-link>
        </div>

        <div class="article-share">
          <span class="article-tags-label">分享：</span>
          <button class="share-btn" @click="copyLink">
            <Link class="w-3.5 h-3.5" />
            {{ copied ? '已复制' : '复制链接' }}
          </button>
        </div>
      </footer>

      <!-- 上下篇导航 -->
      <nav v-if="article.prev || article.next" class="article-nav">
        <router-link
          v-if="article.prev"
          :to="`/article/${article.prev.id}`"
          class="article-nav-card"
        >
          <div class="article-nav-label">
            <ArrowLeft class="w-3.5 h-3.5" />
            上一篇
          </div>
          <div class="article-nav-title">
            {{ article.prev.title }}
          </div>
        </router-link>

        <router-link
          v-if="article.next"
          :to="`/article/${article.next.id}`"
          class="article-nav-card article-nav-card--right"
        >
          <div class="article-nav-label article-nav-label--right">
            下一篇
            <ArrowRight class="w-3.5 h-3.5" />
          </div>
          <div class="article-nav-title">
            {{ article.next.title }}
          </div>
        </router-link>
      </nav>

      <!-- 评论区占位 -->
      <section class="article-comments">
        <h2>评论</h2>
        <div class="comments-placeholder">
          评论功能即将上线，敬请期待
        </div>
      </section>
    </main>

    <!-- 返回顶部 -->
    <transition name="fade">
      <button
        v-if="showBackTop"
        class="back-top-btn"
        @click="scrollToTop"
      >
        <ArrowUp class="w-5 h-5" />
      </button>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
  ArrowLeft, ArrowRight, ArrowUp, Calendar, Eye, Clock, Link,
} from 'lucide-vue-next'
import { get as getArticle } from '@/api/article'

const route = useRoute()

const loading = ref(true)
const error = ref('')
const article = reactive({
  title: '',
  content: '',
  summary: '',
  cover_url: '',
  view_count: 0,
  published_at: '',
  created_at: '',
  categories: [],
  prev: null,
  next: null,
})

const readProgress = ref(0)
const showBackTop = ref(false)
const copied = ref(false)

const renderedContent = computed(() => {
  try {
    const html = marked.parse(article.content || '', { breaks: true, gfm: true })
    return DOMPurify.sanitize(html)
  } catch (e) {
    return ''
  }
})

const readingTime = computed(() => {
  if (!article.content) return 0
  return Math.max(1, Math.ceil(article.content.length / 500))
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

async function loadArticle() {
  const id = route.params.id
  if (!id) return

  loading.value = true
  error.value = ''

  try {
    const data = await getArticle(id)
    Object.assign(article, data || {})
  } catch (e) {
    error.value = '文章不存在或加载失败'
  } finally {
    loading.value = false
    nextTick(() => {
      window.scrollTo({ top: 0, behavior: 'auto' })
      setupCodeCopyButtons()
    })
  }
}

function setupCodeCopyButtons() {
  const preElements = document.querySelectorAll('.article-content pre')
  preElements.forEach((pre) => {
    if (pre.querySelector('.code-copy-btn')) return
    pre.style.position = 'relative'

    const btn = document.createElement('button')
    btn.className = 'code-copy-btn'
    btn.type = 'button'
    btn.setAttribute('aria-label', '复制代码')
    btn.innerHTML = copyIconSvg
    btn.addEventListener('click', () => {
      const code = pre.querySelector('code')
      const text = code ? code.textContent : pre.textContent
      const fallbackCopy = () => {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.select()
        try { document.execCommand('copy') } catch (e) { /* ignore */ }
        document.body.removeChild(ta)
      }
      const done = () => {
        btn.innerHTML = checkIconSvg
        btn.classList.add('is-copied')
        setTimeout(() => {
          btn.innerHTML = copyIconSvg
          btn.classList.remove('is-copied')
        }, 2000)
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done).catch(() => { fallbackCopy(); done() })
      } else {
        fallbackCopy()
        done()
      }
    })
    pre.appendChild(btn)
  })
}

const copyIconSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
const checkIconSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'

function copyLink() {
  const url = window.location.href
  const fallbackCopy = (text) => {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    try {
      document.execCommand('copy')
      copied.value = true
      setTimeout(() => (copied.value = false), 2000)
    } catch (e) {
      // ignore
    }
    document.body.removeChild(ta)
  }

  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(url).then(() => {
      copied.value = true
      setTimeout(() => (copied.value = false), 2000)
    }).catch(() => fallbackCopy(url))
  } else {
    fallbackCopy(url)
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleScroll() {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  readProgress.value = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
  showBackTop.value = scrollTop > 400
}

watch(() => route.params.id, loadArticle)

onMounted(() => {
  loadArticle()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* ============ 页面容器 ============ */
.article-page {
  min-height: 100vh;
  background: #fdfaf5;
  color: #1a1a1c;
}

/* ============ 阅读进度条 ============ */
.read-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 110;
  height: 3px;
  background: transparent;
  pointer-events: none;
}

.read-progress-fill {
  height: 100%;
  background: #d4856b;
  transition: width 0.15s ease-out;
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

/* ============ 文章容器 ============ */
.article-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 120px 1.5rem 4rem;
}

/* ============ 加载占位 ============ */
.article-loading {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading-line {
  height: 1rem;
  background: #efe9dc;
  border-radius: 0.5rem;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ============ 错误 / 返回 ============ */
.article-error {
  color: #6b6b72;
  margin-bottom: 1.5rem;
}

/* ============ 返回按钮 ============ */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem 0.5rem 0.75rem;
  margin-bottom: 2rem;
  border-radius: 100px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #6b6b72;
  background: rgba(212, 133, 107, 0.08);
  border: 1px solid transparent;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.back-btn-icon {
  width: 1rem;
  height: 1rem;
  transition: transform 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.back-btn:hover {
  color: #d4856b;
  background: rgba(212, 133, 107, 0.15);
  border-color: rgba(212, 133, 107, 0.3);
}

.back-btn:hover .back-btn-icon {
  transform: translateX(-3px);
}

/* ============ 文章头部 ============ */
.article-categories {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.article-category-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  background: #f0f5ff;
  color: #004acc;
  text-decoration: none;
  transition: all 0.3s ease;
}

.article-category-tag:hover {
  background: #0065fd;
  color: #ffffff;
}

.article-title {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1.3;
  color: #1a1a1c;
  margin-bottom: 1rem;
  letter-spacing: -0.01em;
  text-align: center;
}

@media (min-width: 768px) {
  .article-title {
    font-size: 2.25rem;
  }
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b6b72;
}

.article-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

/* ============ 封面图 ============ */
.article-cover {
  margin-bottom: 2.5rem;
  border-radius: 1.2rem;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  height: auto;
  object-fit: cover;
  display: block;
}

/* ============ 文章正文 ============ */
.article-content {
  font-size: 1rem;
  line-height: 1.8;
  color: #1a1a1c;
  word-break: break-word;
}

.article-content :deep(h1) {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 2rem 0 1rem;
  line-height: 1.3;
}

.article-content :deep(h2) {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 2.5rem 0 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e8e2d4;
  line-height: 1.3;
}

.article-content :deep(h3) {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 2rem 0 1rem;
  line-height: 1.4;
}

.article-content :deep(h4) {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 1.5rem 0 0.75rem;
}

.article-content :deep(p) {
  margin: 0 0 1.25rem;
}

.article-content :deep(a) {
  color: #0065fd;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.article-content :deep(a:hover) {
  color: #004acc;
}

.article-content :deep(ul) {
  list-style: disc;
  padding-left: 1.5rem;
  margin: 0 0 1.25rem;
}

.article-content :deep(ol) {
  list-style: decimal;
  padding-left: 1.5rem;
  margin: 0 0 1.25rem;
}

.article-content :deep(li) {
  margin-bottom: 0.5rem;
}

.article-content :deep(li:last-child) {
  margin-bottom: 0;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #d4856b;
  padding: 0.5rem 0 0.5rem 1rem;
  margin: 0 0 1.25rem;
  color: #6b6b72;
  background: #faf6ee;
  border-radius: 0 0.5rem 0.5rem 0;
}

.article-content :deep(blockquote p) {
  margin-bottom: 0;
}

.article-content :deep(pre) {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 1rem 1.25rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0 0 1.25rem;
  font-size: 0.875rem;
  line-height: 1.6;
}

.article-content :deep(.code-copy-btn) {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  opacity: 0;
  transition: all 0.25s ease;
  z-index: 1;
}

.article-content :deep(pre:hover .code-copy-btn) {
  opacity: 1;
}

.article-content :deep(.code-copy-btn:hover) {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.3);
}

.article-content :deep(.code-copy-btn.is-copied) {
  opacity: 1;
  color: #a6e3a1;
  border-color: rgba(166, 227, 161, 0.4);
}

.article-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: inherit;
}

.article-content :deep(code) {
  background: #efe9dc;
  color: #1a1a1c;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1.5rem 0;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 1.25rem;
  font-size: 0.9375rem;
}

.article-content :deep(th) {
  background: #efe9dc;
  font-weight: 600;
  text-align: left;
  padding: 0.75rem 1rem;
  border: 1px solid #e8e2d4;
}

.article-content :deep(td) {
  padding: 0.75rem 1rem;
  border: 1px solid #e8e2d4;
}

.article-content :deep(hr) {
  border: 0;
  border-top: 1px solid #e8e2d4;
  margin: 2rem 0;
}

/* ============ 文章底部 ============ */
.article-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e8e2d4;
}

.article-tags,
.article-share {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.article-tags-label {
  font-size: 0.875rem;
  color: #6b6b72;
  margin-right: 0.5rem;
}

.share-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0 0.75rem;
  height: 2rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid #e8e2d4;
  color: #6b6b72;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-btn:hover {
  color: #d4856b;
  border-color: #d4856b;
}

/* ============ 上下篇导航 ============ */
.article-nav {
  margin-top: 3rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .article-nav {
    grid-template-columns: 1fr 1fr;
  }
}

.article-nav-card {
  display: block;
  padding: 1rem;
  border-radius: 1.2rem;
  border: 1px solid #e8e2d4;
  text-decoration: none;
  transition: border-color 0.3s ease;
}

.article-nav-card:hover {
  border-color: #d4856b;
}

.article-nav-card--right {
  text-align: right;
}

.article-nav-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #6b6b72;
  margin-bottom: 0.5rem;
}

.article-nav-label--right {
  justify-content: flex-end;
}

.article-nav-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1a1a1c;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-nav-card:hover .article-nav-title {
  color: #d4856b;
}

/* ============ 评论区 ============ */
.article-comments {
  margin-top: 4rem;
}

.article-comments h2 {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.comments-placeholder {
  padding: 2rem;
  text-align: center;
  border: 1px dashed #e8e2d4;
  border-radius: 0.5rem;
  color: #6b6b72;
}

/* ============ 返回顶部 ============ */
.back-top-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 40;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: #d4856b;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: background 0.3s ease;
}

.back-top-btn:hover {
  background: #b86b50;
}

/* ============ 淡入淡出 ============ */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
