import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/FrontLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/HomeView.vue'),
      },
      {
        path: 'article/:id',
        name: 'article-detail',
        component: () => import('@/views/ArticleDetailView.vue'),
      },
      {
        path: 'category/:id?',
        name: 'category',
        component: () => import('@/views/CategoryView.vue'),
      },
    ],
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: () => import('@/views/admin/DashboardView.vue'),
      },
      {
        path: 'articles',
        name: 'admin-articles',
        component: () => import('@/views/admin/ArticleManageView.vue'),
      },
      {
        path: 'articles/edit/:id?',
        name: 'admin-article-edit',
        component: () => import('@/views/admin/ArticleEditView.vue'),
      },
      {
        path: 'banners',
        name: 'admin-banners',
        component: () => import('@/views/admin/BannerManageView.vue'),
      },
      {
        path: 'featured',
        name: 'admin-featured',
        component: () => import('@/views/admin/FeaturedManageView.vue'),
      },
      {
        path: 'categories',
        name: 'admin-categories',
        component: () => import('@/views/admin/CategoryManageView.vue'),
      },
      {
        path: 'profile',
        name: 'admin-profile',
        component: () => import('@/views/admin/ProfileManageView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0, behavior: 'smooth' }
  },
})

// 全局前置守卫：检查登录
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  // 需要登录：检查 meta 标记或路径以 /admin 开头
  const requiresAuth = to.meta.requiresAuth || to.path.startsWith('/admin')
  if (requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  // 已登录访问登录页 → 去后台
  if (to.name === 'login' && auth.isAuthenticated) {
    next({ name: 'admin-dashboard' })
    return
  }
  next()
})

export default router
