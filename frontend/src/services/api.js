import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
})

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default {
  // Auth endpoints
  login(data) {
    return apiClient.post(
      '/users/login/token',
      data,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
  },

  // User endpoints
  createUser(data) {
    return apiClient.post('/users/register', data)
  },
  getMe() {
    return apiClient.get('/users/me')
  },

  // Food endpoints
  getFoods(query, skip = 0, limit = 20) {
    return apiClient.get('/foods/', {
      params: {
        search: query,
        skip: skip,
        limit: limit
      }
    });
  },

  createFood(data) {
    return apiClient.post('/foods/', data)
  },
  updateMe(data) {
    return apiClient.put('/users/me', data)
  },
  
  // Exercise endpoints
  getExercises() {
    return apiClient.get('/exercises/')
  },

  // Tracking endpoints
  logFood(data) {
    return apiClient.post('/tracking/food-log/', data)
  },
  logExercise(data) {
    return apiClient.post('/tracking/exercise-log/', data)
  },
  getDailySummary(date, needAI = false) {
    return apiClient.get(`/tracking/daily-summary/?date=${date}&need_ai=${needAI}`)
  },
  getEnergySummary(params) {
    return apiClient.get('/tracking/energy-summary/', { params });
  },

  // Recommendation endpoint
  getMenuSuggestions() {
    return apiClient.get('/recommendations/')
  }
}

