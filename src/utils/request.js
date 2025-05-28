import axios from 'axios'
import router from '@/router'
import { Message } from 'element-ui'

const service = axios.create({
  baseURL: 'http://localhost:8000',  // 确保这个地址正确
  timeout: 15000 // 15秒
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          Message.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          if (router.currentRoute.path !== '/login') {
            router.push('/login')
          }
          break
        case 403:
          Message.error('没有权限执行此操作')
          break
        default:
          Message.error(error.response.data.message || '请求失败')
      }
    }
    return Promise.reject(error)
  }
)

export default service 