import request from './request'

export function list(params) {
  return request.get('/banners', { params })
}

export function stats() {
  return request.get('/banners/stats')
}

export function create(data) {
  return request.post('/banners', data)
}

export function update(id, data) {
  return request.put(`/banners/${id}`, data)
}

export function remove(id) {
  return request.delete(`/banners/${id}`)
}
