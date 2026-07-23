import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  withCredentials: true,
})

// 请求拦截器：注入 Authorization
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：拆包 response.data.data，错误统一 ElMessage
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 后端统一返回 { code, message, data }
    if (res && typeof res.code !== 'undefined') {
      if (res.code === 200 || res.code === 0) {
        return res.data
      }
      // 业务错误
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    // 兼容直接返回数据的情况
    return res
  },
  (error) => {
    const status = error.response?.status
    const message =
      error.response?.data?.message ||
      error.response?.data?.error ||
      error.message ||
      '网络错误'

    if (status === 401) {
      const isLoginPage = window.location.pathname === '/login'
      ElMessage.error(isLoginPage ? message : '登录已过期，请重新登录')
      localStorage.removeItem('token')
      if (!isLoginPage) {
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }

    if (status === 403) {
      ElMessage.error('没有权限执行此操作')
    } else if (status === 404) {
      ElMessage.error('资源不存在')
    } else if (status >= 500) {
      ElMessage.error('服务器错误，请稍后再试')
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  },
)

export default request
