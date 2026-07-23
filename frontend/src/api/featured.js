import request from './request'

export function list(params) {
  return request.get('/featured', { params })
}

export function stats() {
  return request.get('/featured/stats')
}

export function create(data) {
  return request.post('/featured', data)
}

export function update(id, data) {
  return request.put(`/featured/${id}`, data)
}

export function remove(id) {
  return request.delete(`/featured/${id}`)
}
