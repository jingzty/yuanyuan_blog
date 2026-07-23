<template>
  <main class="min-h-screen bg-[var(--background)]">
    <!-- 顶部导航栏 -->
    <header class="sticky top-0 z-20 bg-[var(--card)] border-b border-[var(--border)]">
      <div class="flex items-center justify-between h-16 px-6 max-w-[1440px] mx-auto">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-[var(--radius-md)] bg-[var(--color-primary)] flex items-center justify-center">
            <CloudSun class="w-5 h-5 text-white" />
          </div>
          <span class="text-lg font-semibold tracking-tight text-[var(--foreground)]">远远的天空</span>
        </div>
        <div class="flex items-center gap-5">
          <router-link
            to="/"
            class="inline-flex items-center gap-1.5 text-sm text-[var(--muted-foreground)] hover:text-[var(--color-primary)] transition-colors"
          >
            <ExternalLink class="w-4 h-4" />
            <span>返回前台</span>
          </router-link>
          <div
            class="w-9 h-9 rounded-full bg-[var(--accent)] flex items-center justify-center text-[var(--accent-foreground)] text-sm font-medium cursor-pointer hover:ring-2 hover:ring-[var(--color-primary)]/30 transition-all"
          >
            {{ userInitial }}
          </div>
        </div>
      </div>
    </header>

    <!-- 主体布局 -->
    <div class="flex max-w-[1440px] mx-auto">
      <!-- 左侧边栏 -->
      <aside
        class="w-60 shrink-0 border-r border-[var(--border)] min-h-[calc(100vh-4rem)] sticky top-16 self-start py-6 px-3 relative"
      >
        <!-- 内容管理分组 -->
        <div class="mb-6">
          <div class="px-3 mb-2 text-xs font-medium text-[var(--muted-foreground)] tracking-wider uppercase">
            内容管理
          </div>
          <nav class="space-y-1">
            <router-link
              to="/admin"
              v-slot="{ isActive }"
              custom
            >
              <a
                href="/admin"
                @click.prevent="router.push('/admin')"
                :class="[
                  'flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm transition-colors',
                  isActive
                    ? 'text-white bg-[var(--color-primary)] shadow-sm font-medium'
                    : 'text-[var(--foreground)] hover:bg-[var(--secondary)]',
                ]"
              >
                <LayoutDashboard class="w-4 h-4" />
                <span>仪表盘</span>
              </a>
            </router-link>

            <router-link
              to="/admin/articles"
              v-slot="{ isActive }"
              custom
            >
              <a
                href="/admin/articles"
                @click.prevent="router.push('/admin/articles')"
                :class="[
                  'flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm transition-colors',
                  isActive
                    ? 'text-white bg-[var(--color-primary)] shadow-sm font-medium'
                    : 'text-[var(--foreground)] hover:bg-[var(--secondary)]',
                ]"
              >
                <FileText class="w-4 h-4" />
                <span>文章管理</span>
              </a>
            </router-link>

            <router-link
              to="/admin/featured"
              v-slot="{ isActive }"
              custom
            >
              <a
                href="/admin/featured"
                @click.prevent="router.push('/admin/featured')"
                :class="[
                  'flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm transition-colors',
                  isActive
                    ? 'text-white bg-[var(--color-primary)] shadow-sm font-medium'
                    : 'text-[var(--foreground)] hover:bg-[var(--secondary)]',
                ]"
              >
                <Star class="w-4 h-4" />
                <span>文章推荐</span>
              </a>
            </router-link>

            <router-link
              to="/admin/banners"
              v-slot="{ isActive }"
              custom
            >
              <a
                href="/admin/banners"
                @click.prevent="router.push('/admin/banners')"
                :class="[
                  'flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm transition-colors',
                  isActive
                    ? 'text-white bg-[var(--color-primary)] shadow-sm font-medium'
                    : 'text-[var(--foreground)] hover:bg-[var(--secondary)]',
                ]"
              >
                <Images class="w-4 h-4" />
                <span>轮播图管理</span>
              </a>
            </router-link>

            <router-link
              to="/admin/categories"
              v-slot="{ isActive }"
              custom
            >
              <a
                href="/admin/categories"
                @click.prevent="router.push('/admin/categories')"
                :class="[
                  'flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm transition-colors',
                  isActive
                    ? 'text-white bg-[var(--color-primary)] shadow-sm font-medium'
                    : 'text-[var(--foreground)] hover:bg-[var(--secondary)]',
                ]"
              >
                <Tags class="w-4 h-4" />
                <span>分类标签</span>
              </a>
            </router-link>
          </nav>
        </div>

        <!-- 系统设置分组 -->
        <div class="mb-6">
          <div class="px-3 mb-2 text-xs font-medium text-[var(--muted-foreground)] tracking-wider uppercase">
            系统设置
          </div>
          <nav class="space-y-1">
            <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm text-[var(--foreground)] hover:bg-[var(--secondary)] transition-colors">
              <Settings class="w-4 h-4 text-[var(--muted-foreground)]" />
              <span>站点配置</span>
            </a>
            <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm text-[var(--foreground)] hover:bg-[var(--secondary)] transition-colors">
              <Sparkles class="w-4 h-4 text-[var(--muted-foreground)]" />
              <span>AI 配置</span>
            </a>
            <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm text-[var(--foreground)] hover:bg-[var(--secondary)] transition-colors">
              <Database class="w-4 h-4 text-[var(--muted-foreground)]" />
              <span>OSS 配置</span>
            </a>
            <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm text-[var(--foreground)] hover:bg-[var(--secondary)] transition-colors">
              <Shield class="w-4 h-4 text-[var(--muted-foreground)]" />
              <span>安全策略</span>
            </a>
          </nav>
        </div>

        <!-- 底部 个人中心 -->
        <div class="absolute bottom-6 left-3 right-3">
          <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm text-[var(--foreground)] hover:bg-[var(--secondary)] transition-colors">
            <User class="w-4 h-4 text-[var(--muted-foreground)]" />
            <span>个人中心</span>
          </a>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <section class="flex-1 min-w-0 p-6 lg:p-8">
        <router-view />
      </section>
    </div>
  </main>
</template>

<script setup>
import {
  CloudSun,
  ExternalLink,
  LayoutDashboard,
  FileText,
  Star,
  Images,
  Tags,
  Settings,
  Sparkles,
  Database,
  Shield,
  User,
} from 'lucide-vue-next'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const userInitial = computed(() => {
  const u = auth.user
  if (!u) return '远'
  return (u.nickname || u.username || '远').charAt(0)
})
</script>
