import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
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
    return apiClient.post('/users/login/token', data)
  },

  // User endpoints
  createUser(data) {
    return apiClient.post('/users/register', data)
  },
  getMe() {
    return apiClient.get('/users/me')
  },

  // Food endpoints
  getFoods(query) {
    return apiClient.get(`/foods/?search=${query}`)
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
  getDailySummary(date) {
    return apiClient.get(`/tracking/daily-summary/?date=${date}`)
  },
  getEnergySummary(params) {
    return apiClient.get('/tracking/energy-summary/', { params });
  },

  // Recommendation endpoint
  getMenuSuggestions() {
    return apiClient.get('/recommendations/')
  }
}

