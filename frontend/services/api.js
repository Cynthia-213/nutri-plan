/**
 * API 服务 - UniApp 版本
 * 使用 uni.request 替代 axios
 */
import request from '../utils/request'

export default {
  // Auth endpoints
  async login(data) {
    // 将对象转换为 URL 编码格式（UniApp 兼容）
    const params = Object.keys(data)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
      .join('&')
    
    return request.post(
      '/users/login/token',
      params,
      {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    )
  },

  // User endpoints
  createUser(data) {
    return request.post('/users/register', data)
  },
  
  getMe() {
    return request.get('/users/me')
  },
  
  updateMe(data) {
    return request.put('/users/me', data)
  },

  changePassword(data) {
    return request.post('/users/change-password', data)
  },

  // Food endpoints
  getFoods(query, skip = 0, limit = 20) {
    return request.get('/foods/', {
      search: query,
      skip: skip,
      limit: limit
    })
  },

  createFood(data) {
    return request.post('/foods/', data)
  },
  
  // Exercise endpoints
  getExercises() {
    return request.get('/exercises/')
  },

  // Tracking endpoints
  logFood(data) {
    return request.post('/tracking/food-log/', data)
  },
  
  logExercise(data) {
    return request.post('/tracking/exercise-log/', data)
  },
  
  getDailySummary(date) {
    return request.get(`/tracking/daily-summary/?date=${date}`)
  },
  
  generateAISummary(date) {
    return request.post(`/tracking/ai-summary/?date=${date}`)
  },
  
  getEnergySummary(params) {
    return request.get('/tracking/energy-summary/', params)
  },

  // Recommendation endpoint
  getMenuSuggestions() {
    return request.get('/recommendations/')
  },

  // Blog endpoints
  getBlogs(skip = 0, limit = 20) {
    return request.get('/blogs/', { skip, limit })
  },

  getMyBlogs(skip = 0, limit = 20) {
    return request.get('/blogs/me', { skip, limit })
  },

  getBlogDetail(blogId) {
    return request.get(`/blogs/${blogId}`)
  },

  createBlog(data) {
    return request.post('/blogs/', data)
  },

  updateBlog(blogId, data) {
    return request.patch(`/blogs/${blogId}`, data)
  },

  hideBlog(blogId) {
    return request.patch(`/blogs/${blogId}`, { is_public: false })
  },

  likeBlog(blogId) {
    return request.post(`/blogs/${blogId}/like`)
  },

  getBlogComments(blogId, skip = 0, limit = 50) {
    return request.get(`/blogs/${blogId}/comments`, { skip, limit })
  },

  createBlogComment(blogId, data) {
    return request.post(`/blogs/${blogId}/comments`, data)
  },

  getUploadUrl(filename) {
    return request.get('/blogs/upload-url', { filename })
  },

  deleteBlog(blogId) {
    return request.delete(`/blogs/${blogId}`)
  },

  // Ranking endpoints
  getRankings(params) {
    return request.get('/rankings/', params)
  },

  getMyRanking(params) {
    return request.get('/rankings/my-ranking', params)
  },

  // Notification endpoints
  getNotifications(params) {
    return request.get('/notifications/', params)
  },

  getUnreadCount() {
    return request.get('/notifications/unread-count')
  },

  markNotificationRead(notificationId) {
    return request.patch(`/notifications/${notificationId}/read`)
  },

  markAllNotificationsRead() {
    return request.post('/notifications/mark-all-read')
  }
}
