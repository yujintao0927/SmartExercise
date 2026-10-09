import axios from 'axios'
import mockAdapter from '../mock/adapter'

// 接口已实现，切换到真实接口。如需回退 mock 联调，将 USE_MOCK 改为 true。
const USE_MOCK = false

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
