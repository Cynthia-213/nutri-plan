<template>
  <div class="home-container">
    <div class="bg-blob"></div>
    
    <main class="content-card">
      <div v-if="isLoggedIn" class="hero-section fade-in">
        <div class="icon-header">👋</div>
        <h1>欢迎回来，健康达人</h1>
        <p class="subtitle">今天也是充满活力的一天。您的每一份记录都在见证更好的自己。</p>
      </div>

      <div v-else class="hero-section fade-in">
        <div class="brand-logo">Nutri-Plan</div>
        <h1>您的私人健康助理</h1>
        <p class="subtitle">通过科学的计算，帮助您精准掌控每一卡路里的摄入与消耗。</p>
        
        <div class="auth-group">
          <button @click="login" class="btn btn-primary">立即登录</button>
          <button @click="register" class="btn btn-outline">加入我们</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const isLoggedIn = ref(false);
const router = useRouter();

const checkLoginStatus = () => {
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token;
};

const login = () => router.push('/login');
const register = () => router.push('/register');

onMounted(() => {
  checkLoginStatus();
});
</script>

<style scoped>
/* 容器与背景 */
.home-container {
  min-height: 90vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background-color: #f9fafb;
  position: relative;
  overflow: hidden;
}

.bg-blob {
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(131, 139, 139, 0.1) 0%, rgba(255,255,255,0) 70%);
  top: -100px;
  right: -100px;
  z-index: 0;
}

/* 主卡片设计 */
.content-card {
  position: relative;
  z-index: 1;
  background: white;
  padding: 60px 40px;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
  max-width: 600px;
  width: 100%;
  text-align: center;
}

/* 文本样式 */
h1 {
  color: #2d3436;
  font-size: 2.2em;
  font-weight: 700;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.subtitle {
  color: #636e72;
  font-size: 1.1em;
  line-height: 1.6;
  margin-bottom: 40px;
}

/* 按钮基础样式 */
.btn {
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  margin: 0 8px;
}

.btn-primary {
  background-color: #838B8B;
  color: white;
}

.btn-primary:hover {
  background-color: #6e7575;
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(131, 139, 139, 0.3);
}

.btn-outline {
  background-color: transparent;
  color: #838B8B;
  border: 2px solid #838B8B;
}

.btn-outline:hover {
  background-color: #f1f3f3;
  transform: translateY(-2px);
}

/* 已登录后的导航网格 */
.nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 20px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 10px;
  background: #f8f9fa;
  border-radius: 16px;
  text-decoration: none;
  color: #444;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: #eeefef;
  transform: scale(1.05);
}

.nav-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

/* 装饰性元素 */
.icon-header { font-size: 48px; margin-bottom: 10px; }
.brand-logo {
  color: #838B8B;
  font-weight: 800;
  font-size: 1.2em;
  margin-bottom: 20px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 简单入场动画 */
.fade-in {
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>