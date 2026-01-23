/**
 * UniApp 请求封装
 * 使用 uni.request 替代 axios
 */

const BASE_URL = 'http://192.168.31.248:8000/api'

// 请求拦截器
const request = (options) => {
  return new Promise((resolve, reject) => {
    // 获取 token
    const token = uni.getStorageSync('token')
    
    // 设置请求头
    const header = {
      'Content-Type': 'application/json',
      ...options.header
    }
    
    // 如果有 token，添加到请求头
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }
    
    // 发起请求
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: header,
      timeout: options.timeout || 10000,
      success: (res) => {
        const { statusCode, data } = res

        // ✅ 统一成功判断：2xx 状态码（包括 200, 201, 204 等）
        if (statusCode >= 200 && statusCode < 300) {
          // 如果后端返回的数据格式是 { code, data, message }
          if (data && typeof data === 'object' && data.code !== undefined) {
            if (data.code === 0 || data.code === 200) {
              resolve(data.data ?? data)
            } else {
              uni.showToast({
                title: data.message || '请求失败',
                icon: 'none'
              })
              reject(data)
            }
          } else {
            // ✅ FastAPI / RESTful：直接返回 data
            resolve(data)
          }
          return
        }

        // ✅ 401：未登录 / token 失效
        if (statusCode === 401) {
          uni.removeStorageSync('token')
          const pages = getCurrentPages()
          const currentPage = pages[pages.length - 1]
          if (currentPage?.route !== 'pages/login/login') {
            uni.reLaunch({
              url: '/pages/login/login'
            })
          }
          reject(res)
          return
        }

        // ❌ 其他 HTTP 错误
        uni.showToast({
          title: `请求失败 (${statusCode})`,
          icon: 'none'
        })
        reject(res)
      },
      fail: (err) => {
        uni.showToast({
          title: '网络错误，请检查网络连接',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// 导出请求方法
export default {
  get(url, params = {}, config = {}) {
    let queryString = Object.keys(params).map(key => 
      `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`
    ).join('&')
    
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString
    }
    
    return request({
      url,
      method: 'GET',
      ...config
    })
  },
  
  post(url, data = {}, header = {}) {
    return request({
      url,
      method: 'POST',
      data,
      header
    })
  },
  
  put(url, data = {}) {
    return request({
      url,
      method: 'PUT',
      data
    })
  },
  
  patch(url, data = {}) {
    return request({
      url,
      method: 'PATCH',
      data
    })
  },
  
  delete(url, data = {}) {
    return request({
      url,
      method: 'DELETE',
      data
    })
  }
}
