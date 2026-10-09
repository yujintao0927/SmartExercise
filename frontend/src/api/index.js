import axios from 'axios'
import mockAdapter from '../mock/adapter'

// 接口尚未全部实现，前端先用 mock 数据联调。
// 后端接口实现完成后，将 USE_MOCK 改为 false 即切换到真实接口。
const USE_MOCK = true

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  ...(USE_MOCK ? { adapter: mockAdapter } : {}),
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && window.location.pathname !== '/login') {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api
