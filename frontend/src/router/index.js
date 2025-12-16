import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import FoodTracker from '../views/FoodTracker.vue'
import ExerciseTracker from '../views/ExerciseTracker.vue'
import DailySummary from '../views/DailySummary.vue'
import MenuSuggestion from '../views/MenuSuggestion.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
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
    path: '/food',
    name: 'FoodTracker',
    component: FoodTracker
  },
  {
    path: '/exercise',
    name: 'ExerciseTracker',
    component: ExerciseTracker
  },
  {
    path: '/summary',
    name: 'DailySummary',
    component: DailySummary
  },
  {
    path: '/recommendations',
    name: 'MenuSuggestion',
    component: MenuSuggestion
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
