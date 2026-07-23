import { defineStore } from 'pinia'
import { login as apiLogin, me as apiMe, getCaptcha as apiGetCaptcha } from '@/api/auth'

function parseJwtPayload(token) {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    return JSON.parse(atob(parts[1]))
  } catch {
    return null
  }
}

function isTokenExpired(token) {
  const payload = parseJwtPayload(token)
  if (!payload || !payload.exp) return false
  return Date.now() >= payload.exp * 1000
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token && !isTokenExpired(state.token),
  },
  actions: {
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },

    async login(username, password, captcha) {
      const data = await apiLogin({ username, password, captcha })
      // 后端返回 { token, user }
      const token = data?.token || data?.access_token
      this.setToken(token)
      this.user = data?.user || null
      return data
    },

    async fetchUser() {
      if (!this.token) return null
      try {
        const user = await apiMe()
        this.user = user
        return user
      } catch (e) {
        this.logout()
        return null
      }
    },

    async getCaptcha() {
      return apiGetCaptcha()
    },

    logout() {
      this.setToken('')
      this.user = null
    },
  },
})
