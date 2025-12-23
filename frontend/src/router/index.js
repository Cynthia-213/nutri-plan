import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import FoodTracker from '../views/FoodTracker.vue'
import ExerciseTracker from '../views/ExerciseTracker.vue'
import DailySummary from '../views/DailySummary.vue'
import MenuSuggestion from '../views/MenuSuggestion.vue'
import UserMe from '../views/UserMe.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/users/me',
    name: 'UserMe',
    component: UserMe,
    meta: { requiresAuth: true }
  },
  {
    path: '/food',
    name: 'FoodTracker',
    component: FoodTracker,
    meta: { requiresAuth: true }
  },
  {
    path: '/exercise',
    name: 'ExerciseTracker',
    component: ExerciseTracker,
    meta: { requiresAuth: true }
  },
  {
    path: '/summary',
    name: 'DailySummary',
    component: DailySummary,
    meta: { requiresAuth: true }
  },
  {
    path: '/recommendations',
    name: 'MenuSuggestion',
    component: MenuSuggestion,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// --- 全局路由守卫逻辑 ---
router.beforeEach((to, from, next) => {
  // 从本地存储获取 token
  const token = localStorage.getItem('token')

  // 如果用户要去「需要权限」的页面，但没有 token
  if (to.meta.requiresAuth && !token) {
    // 强制跳转到登录页
    next('/login')
  } 
  // 如果用户要去「登录/注册」页，但已经有「token」
  else if ((to.path === '/login' || to.path === '/register') && token) {
    // 直接跳转到首页，无需重复登录
    next('/')
  } 
  // 3. 其他情况正常放行
  else {
    next()
  }
})

export default router