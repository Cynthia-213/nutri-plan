<template>
  <div class="login-wrapper">
    <div class="bg-decoration"></div>
    
    <div class="login-card">
      <div class="login-header">
        <h2>健康管理系统</h2>
        <p>欢迎回来，请登录您的账号</p>
      </div>

      <el-form :model="form" @submit.prevent="onSubmit" label-position="top">
        <el-form-item label="用户名">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名"
            size="large"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="密码">
          <el-input 
            type="password" 
            v-model="form.password" 
            placeholder="请输入密码"
            show-password
            size="large"
          ></el-input>
        </el-form-item>

        <div class="login-options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <el-button link type="info">忘记密码？</el-button>
        </div>

        <el-button 
          class="submit-btn" 
          type="primary" 
          native-type="submit"
          size="large"
        >
          立即登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

// 页面加载时：检查是否有记住的用户名
onMounted(() => {
  const savedUsername = localStorage.getItem('remembered_username')
  if (savedUsername) {
    form.username = savedUsername
    rememberMe.value = true
  }
})

const onSubmit = async () => {
  try {
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)

    const response = await api.login(params)

    // 存储 Token，保持登录态
    localStorage.setItem('token', response.data.access_token)
    
    // 处理“记住我”：存储用户名
    if (rememberMe.value) {
      localStorage.setItem('remembered_username', form.username)
    } else {
      localStorage.removeItem('remembered_username')
    }

    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  }
}
</script>

<style scoped>
/* 背景容器：使用渐变色让页面更有质感 */
.login-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  overflow: hidden;
}

/* 装饰背景圆圈 */
.bg-decoration {
  position: absolute;
  width: 600px;
  height: 600px;
  background: #838B8B;
  opacity: 0.05;
  border-radius: 50%;
  top: -200px;
  right: -100px;
}

/* 登录卡片 */
.login-card {
  z-index: 1;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #2c3e50;
  font-size: 24px;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

/* 1. 修改未选中时的边框色悬停效果 */
:deep(.el-checkbox__input:hover .el-checkbox__inner) {
  border-color: #838B8B !important;
}

/* 2. 修改勾选后的背景色和边框色 */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #838B8B !important;
  border-color: #838B8B !important;
}

/* 3. 修改勾选后的文字颜色 */
:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #838B8B !important;
}

/* 4. 修改聚焦（Tab选中）时的边框 */
:deep(.el-checkbox__input.is-focus .el-checkbox__inner) {
  border-color: #838B8B !important;
}

:deep(.el-input) {
  --el-input-focus-border-color: #838B8B;
  --el-color-primary: #838B8B; /* 这行能覆盖大部分组件的激活色 */
}

.el-button.link {
  color: #838B8B !important;
}
.el-button.link:hover {
  opacity: 0.8;
}
.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.submit-btn {
  width: 100%;
  height: 48px;
  background-color: #838B8B !important;
  border-color: #838B8B !important;
  font-size: 16px;
  font-weight: bold;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background-color: #6e7575 !important; /* 悬停时深一点 */
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(131, 139, 139, 0.3);
}
</style>