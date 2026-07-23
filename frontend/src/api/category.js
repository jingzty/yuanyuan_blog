import request from './request'

export function list(params) {
  return request.get('/categories', { params })
}

export function create(data) {
  return request.post('/categories', data)
}

export function update(id, data) {
  return request.put(`/categories/${id}`, data)
}

export function remove(id) {
  return request.delete(`/categories/${id}`)
}
