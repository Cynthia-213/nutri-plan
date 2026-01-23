<template>
  <view class="home-container">
    <view class="bg-blob"></view>

    <view class="content-card">
      <!-- 已登录 -->
      <view v-if="isLoggedIn" class="hero-section fade-in">
        <view class="icon-header">👋</view>
        <text class="title">欢迎回来，健康达人</text>
        <text class="subtitle">
          今天也是充满活力的一天。您的每一份记录都在见证更好的自己。
        </text>

        <view class="nav-grid">
          <view class="nav-item" @tap="go('/pages/daily-summary/daily-summary')">
            <view class="nav-icon">📊</view>
            <text>每日概览</text>
          </view>
          <view class="nav-item" @tap="go('/pages/food-tracker/food-tracker')">
            <view class="nav-icon">🍎</view>
            <text>饮食记录</text>
          </view>
          <view class="nav-item" @tap="go('/pages/exercise-tracker/exercise-tracker')">
            <view class="nav-icon">🏋️</view>
            <text>运动记录</text>
          </view>
          <view class="nav-item" @tap="go('/pages/menu-suggestion/menu-suggestion')">
            <view class="nav-icon">💡</view>
            <text>菜单建议</text>
          </view>
          <view class="nav-item" @tap="go('/pages/community/community')">
            <view class="nav-icon">🤝</view>
            <text>社区</text>
          </view>
          <view class="nav-item" @tap="go('/pages/ranking/ranking')">
            <view class="nav-icon">🏆</view>
            <text>排行榜</text>
          </view>
          <view class="nav-item" @tap="go('/pages/user-me/user-me')">
            <view class="nav-icon">👤</view>
            <text>个人中心</text>
          </view>
          <view class="nav-item notification-nav-item" @tap="goToNotifications">
            <view class="nav-icon">🔔</view>
            <text>通知</text>
            <view v-if="unreadCount > 0" class="nav-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</view>
          </view>
        </view>
      </view>

      <!-- 未登录 -->
      <view v-else class="hero-section fade-in">
        <text class="brand-logo">Nutri-Plan</text>
        <text class="title">您的私人健康助理</text>
        <text class="subtitle">
          通过科学的计算，帮助您精准掌控每一卡路里的摄入与消耗。
        </text>

        <view class="auth-group">
          <button class="btn btn-primary" @tap="go('/pages/login/login')">
            立即登录
          </button>
          <button class="btn btn-outline" @tap="go('/pages/register/register')">
            加入我们
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/services/api'

const isLoggedIn = ref(false)

// 通知相关
const unreadCount = ref(0)

/**
 * 检查登录状态
 */
const checkLoginStatus = () => {
  const token = uni.getStorageSync('token')
  isLoggedIn.value = !!token
}

/**
 * 页面跳转（兼容 tabBar / 普通页面）
 */
const go = (url) => {
  const tabPages = [
    '/pages/home/home'
  ]

  if (tabPages.includes(url)) {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}

const goToNotifications = () => {
  uni.navigateTo({
    url: '/pages/notifications/notifications'
  })
}

const loadUnreadCount = async () => {
  try {
    const res = await api.getUnreadCount()
    unreadCount.value = res?.unread_count || 0
  } catch (e) {
    console.error('加载未读通知数失败:', e)
  }
}

onMounted(() => {
  checkLoginStatus()
  if (isLoggedIn.value) {
    loadUnreadCount()
  }
})

onShow(() => {
  checkLoginStatus()
  if (isLoggedIn.value) {
    loadUnreadCount()
  }
})
</script>

<style scoped lang="scss">
.home-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: calc(env(safe-area-inset-top) + 40rpx)
           32rpx
           calc(env(safe-area-inset-bottom) + 40rpx);
  background-color: #f9fafb;
  position: relative;
  overflow: hidden;
}

.bg-blob {
  position: absolute;
  width: 800rpx;
  height: 800rpx;
  background: radial-gradient(
    circle,
    rgba(131, 139, 139, 0.12) 0%,
    rgba(255, 255, 255, 0) 70%
  );
  top: -300rpx;
  right: -300rpx;
}

.content-card {
  position: relative;
  z-index: 1;
  background: #ffffff;
  padding: 64rpx 48rpx;
  border-radius: 40rpx;
  box-shadow: 0 30rpx 70rpx rgba(0, 0, 0, 0.05);
  max-width: 800rpx;
  width: 100%;
  text-align: center;
}

.title {
  font-size: 44rpx;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 24rpx;
  display: block;
}

.subtitle {
  font-size: 28rpx;
  color: #636e72;
  line-height: 1.6;
  margin-bottom: 64rpx;
  display: block;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24rpx;
  margin-top: 48rpx;
}

.nav-item {
  background: #f8f9fa;
  border-radius: 32rpx;
  padding: 48rpx 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.nav-icon {
  font-size: 64rpx;
  margin-bottom: 16rpx;
}

.nav-item text {
  font-size: 26rpx;
  font-weight: 500;
}

.nav-item {
  position: relative;
}

.notification-nav-item {
  position: relative;
}

.nav-badge {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  min-width: 32rpx;
  height: 32rpx;
  background: #e74c3c;
  color: #fff;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  font-weight: bold;
  padding: 0 8rpx;
  border: 2rpx solid #fff;
}

.icon-header {
  font-size: 112rpx;
  margin-bottom: 32rpx;
}

.brand-logo {
  font-size: 52rpx;
  font-weight: 800;
  color: #838B8B;
  margin-bottom: 40rpx;
  letter-spacing: 4rpx;
}

.btn {
  min-height: 96rpx;
  padding: 28rpx 64rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  font-weight: 600;
  margin: 16rpx;
}

.btn-primary {
  background-color: #838B8B;
  color: #ffffff;
}

.btn-outline {
  background-color: transparent;
  color: #838B8B;
  border: 4rpx solid #838B8B;
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-group {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16rpx;
}

</style>