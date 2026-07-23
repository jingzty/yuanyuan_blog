import request from './request'

export function list(params) {
  return request.get('/articles', { params })
}

export function get(id) {
  return request.get(`/articles/${id}`)
}

export function create(data) {
  return request.post('/articles', data)
}

export function update(id, data) {
  return request.put(`/articles/${id}`, data)
}

export function remove(id) {
  return request.delete(`/articles/${id}`)
}

export function batchRemove(ids) {
  return request.post('/articles/batch', { ids })
}

export function stats() {
  return request.get('/articles/stats')
}
