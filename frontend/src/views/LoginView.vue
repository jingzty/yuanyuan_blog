<template>
  <main class="min-h-screen flex flex-col font-sans antialiased overflow-x-hidden relative">
    <!-- 背景：多层渐变 -->
    <div
      class="fixed inset-0 -z-10"
      style="background: linear-gradient(160deg, #d4e4f7 0%, #eef2f6 38%, #f7f3ea 68%, #f0ece4 100%)"
    />

    <!-- 光晕球（模糊径向渐变制造深度） -->
    <div
      class="fixed top-[-200px] right-[-200px] w-[550px] h-[550px] rounded-full pointer-events-none -z-10"
      style="background: radial-gradient(ellipse at center, rgba(0,101,253,0.08) 0%, transparent 70%)"
    />
    <div
      class="fixed bottom-[-200px] left-[-200px] w-[500px] h-[500px] rounded-full pointer-events-none -z-10"
      style="background: radial-gradient(ellipse at center, rgba(0,101,253,0.06) 0%, transparent 70%)"
    />
    <div
      class="fixed top-[40%] left-[50%] translate-x-[-50%] w-[600px] h-[300px] rounded-full pointer-events-none -z-10"
      style="background: radial-gradient(ellipse at center, rgba(255,255,255,0.3) 0%, transparent 70%)"
    />

    <!-- SVG 云朵装饰（极低透明度，pointer-events-none） -->
    <svg
      class="fixed pointer-events-none -z-10"
      style="width: 280px; height: 100px; top: 10%; right: 8%; opacity: 0.09"
      viewBox="0 0 280 100"
      fill="white"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M40 80 Q15 80 12 62 Q2 58 6 42 Q10 28 30 28 Q35 12 58 12 Q78 12 85 28 Q100 24 110 32 Q125 30 132 45 Q145 48 145 62 Q140 76 125 80 Z"
      />
    </svg>
    <svg
      class="fixed pointer-events-none -z-10"
      style="width: 200px; height: 75px; bottom: 18%; left: 5%; opacity: 0.06"
      viewBox="0 0 280 100"
      fill="white"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M40 80 Q15 80 12 62 Q2 58 6 42 Q10 28 30 28 Q35 12 58 12 Q78 12 85 28 Q100 24 110 32 Q125 30 132 45 Q145 48 145 62 Q140 76 125 80 Z"
      />
    </svg>
    <svg
      class="fixed pointer-events-none -z-10"
      style="width: 160px; height: 60px; top: 45%; left: 16%; opacity: 0.05"
      viewBox="0 0 280 100"
      fill="white"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M40 80 Q15 80 12 62 Q2 58 6 42 Q10 28 30 28 Q35 12 58 12 Q78 12 85 28 Q100 24 110 32 Q125 30 132 45 Q145 48 145 62 Q140 76 125 80 Z"
      />
    </svg>

    <div class="flex-1 flex flex-col items-center justify-center px-4 py-12 sm:py-16">
      <!-- 返回首页链接 -->
      <router-link
        to="/"
        class="anim-logo text-sm inline-flex items-center gap-1.5 mb-10 transition-colors duration-150 hover:text-[var(--foreground)]"
        style="color: var(--muted-foreground)"
      >
        <ArrowLeft class="w-4 h-4" />
        <span>返回首页</span>
      </router-link>

      <!-- 品牌 Logo -->
      <div class="anim-logo text-center mb-10">
        <div
          class="flex items-center justify-center w-10 h-10 rounded-full mx-auto mb-3"
          style="background: var(--color-primary-soft)"
        >
          <CloudSun class="w-5 h-5" style="color: var(--color-primary)" />
        </div>
        <h1 class="text-2xl font-semibold tracking-tight" style="color: var(--foreground); font-family: var(--font-sans)">
          远远的天空
        </h1>
        <p class="text-sm mt-1" style="color: var(--muted-foreground)">登录管理后台</p>
      </div>

      <!-- 登录卡片 -->
      <div
        class="anim-card w-full max-w-[420px]"
        style="background: var(--card); border-radius: var(--radius-lg); padding: 2.5rem 2.5rem 2rem; box-shadow: var(--shadow-lg)"
      >
        <form @submit.prevent="onSubmit">
          <!-- 用户名 -->
          <div class="relative mb-5">
            <User class="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none" style="color: var(--muted-foreground)" />
            <input
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              autocomplete="username"
              class="login-input w-full h-12 pl-11 pr-4 text-sm outline-none transition-all duration-150"
              style="border-radius: var(--radius-md); border: 1px solid var(--input); background: var(--background); color: var(--foreground); font-family: var(--font-sans)"
            />
          </div>

          <!-- 密码 -->
          <div class="relative mb-5">
            <Lock class="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none" style="color: var(--muted-foreground)" />
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="current-password"
              class="login-input w-full h-12 pl-11 pr-10 text-sm outline-none transition-all duration-150"
              style="border-radius: var(--radius-md); border: 1px solid var(--input); background: var(--background); color: var(--foreground); font-family: var(--font-sans)"
            />
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)] hover:text-[var(--color-primary)] transition-colors"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              <Eye v-if="!showPassword" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>

          <!-- 验证码 -->
          <div class="flex gap-3 mb-5">
            <div class="relative flex-1 min-w-0">
              <ShieldCheck class="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none" style="color: var(--muted-foreground)" />
              <input
                v-model="form.captcha"
                type="text"
                placeholder="请输入验证码"
                autocomplete="off"
                class="login-input w-full h-12 pl-11 pr-4 text-sm outline-none transition-all duration-150"
                style="border-radius: var(--radius-md); border: 1px solid var(--input); background: var(--background); color: var(--foreground); font-family: var(--font-sans)"
              />
            </div>
            <div
              class="shrink-0 overflow-hidden cursor-pointer relative"
              style="width: 120px; height: 48px; border-radius: var(--radius-md); background: linear-gradient(135deg, #a8c8f8 0%, #c8ddf8 30%, #d8e8fa 60%, #b8d4f5 100%)"
              @click="refreshCaptcha"
              title="点击刷新验证码"
            >
              <img
                v-if="captchaImg"
                :src="captchaImg"
                alt="验证码"
                class="w-full h-full object-cover"
              />
              <div
                v-else
                class="flex items-center justify-center h-full text-xs text-[var(--muted-foreground)]"
              >
                加载中…
              </div>
            </div>
          </div>

          <!-- 错误提示 -->
          <div
            v-if="errorMessage"
            class="text-sm mb-4"
            style="color: var(--destructive)"
          >
            {{ errorMessage }}
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full h-12 font-medium text-base cursor-pointer transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            style="border-radius: var(--radius-md); background: var(--color-primary); color: var(--color-primary-foreground); font-family: var(--font-sans)"
          >
            {{ loading ? '登录中…' : '登录' }}
          </button>
        </form>

        <p class="text-center text-xs mt-5" style="color: var(--muted-foreground)">
          请输入管理员账号和密码
        </p>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="anim-footer text-center py-6">
      <p class="text-xs" style="color: var(--muted-foreground)">
        &copy; 2026 远远的天空 &middot; 个人博客
      </p>
    </footer>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  CloudSun,
  User,
  Lock,
  ShieldCheck,
  Eye,
  EyeOff,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { getCaptcha } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = reactive({
  username: '',
  password: '',
  captcha: '',
})

const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const captchaImg = ref('')
const captchaCode = ref('')

async function refreshCaptcha() {
  try {
    const data = await getCaptcha()
    captchaImg.value = data?.captcha || data?.image || ''
  } catch (e) {
    ElMessage.error('验证码加载失败，请刷新重试')
  }
}

async function onSubmit() {
  errorMessage.value = ''
  if (!form.username || !form.password) {
    errorMessage.value = '请输入用户名和密码'
    return
  }
  if (!form.captcha) {
    errorMessage.value = '请输入验证码'
    return
  }

  loading.value = true
  try {
    await auth.login(form.username, form.password, form.captcha)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/admin'
    router.replace(redirect)
  } catch (e) {
    errorMessage.value = e?.message || '登录失败，请检查账号密码'
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshCaptcha()
})
</script>

<style scoped>
.login-input:focus {
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 3px rgba(0, 101, 253, 0.12);
}
.login-input::placeholder {
  color: var(--muted-foreground);
  opacity: 0.7;
}
</style>
