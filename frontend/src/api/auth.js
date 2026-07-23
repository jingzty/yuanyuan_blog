import request from './request'

export function login(data) {
  return request.post('/auth/login', data)
}

export function getCaptcha() {
  return request.get('/auth/captcha')
}

export function me() {
  return request.get('/auth/me')
}

export function logout() {
  return request.post('/auth/logout')
}

export function changePassword(data) {
  return request.post('/auth/change-password', data)
}
