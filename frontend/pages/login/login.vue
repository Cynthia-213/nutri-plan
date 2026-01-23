<template>
  <view class="login-wrapper">
    <view class="bg-decoration"></view>

    <view class="login-card">
      <view class="login-header">
        <text class="title">健康管理系统</text>
        <text class="subtitle">欢迎回来，请登录您的账号</text>
      </view>

      <!-- ⚠️ App 端不推荐用 form submit，直接按钮触发 -->
      <view class="form-item">
        <text class="label">用户名</text>
        <input
          v-model="form.username"
          placeholder="请输入用户名"
          class="input-field"
          confirm-type="next"
        />
      </view>

      <view class="form-item">
        <text class="label">密码</text>
        <input
          type="password"
          v-model="form.password"
          placeholder="请输入密码"
          class="input-field"
          confirm-type="done"
          @confirm="onSubmit"
        />
      </view>

      <view class="login-options">
        <text class="forgot-link" @tap="handleForgot">
          忘记密码？
        </text>
      </view>

      <!-- ✅ 主按钮直接 tap -->
      <button
        class="submit-btn"
        :loading="submitting"
        :disabled="submitting"
        @tap="onSubmit"
      >
        立即登录
      </button>
    </view>
  </view>
</template>


<script setup>
import { reactive, ref } from 'vue'
import api from '@/services/api'

const submitting = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const handleForgot = () => {
  uni.showToast({
    title: '功能开发中',
    icon: 'none'
  })
}

const onSubmit = async () => {
  if (submitting.value) return

  if (!form.username || !form.password) {
    uni.showToast({
      title: '请输入用户名和密码',
      icon: 'none'
    })
    return
  }

  submitting.value = true

  try {
    const params = {
      username: form.username,
      password: form.password
    }

    const res = await api.login(params)

    // 保存 token - 修复：request.js 直接返回 data，不是 res.data
    if (!res || !res.access_token) {
      throw new Error('登录响应格式错误')
    }

    uni.setStorageSync('token', res.access_token)

    uni.showToast({
      title: '登录成功',
      icon: 'success'
    })

    setTimeout(() => {
      uni.reLaunch({
        url: '/pages/home/home'
      })
    }, 500)
  } catch (err) {
    console.error('登录错误:', err)
    const errorMessage = err?.response?.data?.detail || err?.message || '登录失败，请检查账号或密码'
    uni.showToast({
      title: errorMessage,
      icon: 'none',
      duration: 2000
    })
  } finally {
    submitting.value = false
  }
}

</script>


<style scoped lang="scss">
/* 背景容器 - 移动端适配 */
.login-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: calc(env(safe-area-inset-top) + 40rpx) 32rpx calc(env(safe-area-inset-bottom) + 40rpx);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  overflow: hidden;
}

/* 装饰背景圆圈 - 移动端优化 */
.bg-decoration {
  position: absolute;
  width: 800rpx;
  height: 800rpx;
  background: #838B8B;
  opacity: 0.05;
  border-radius: 50%;
  top: -300rpx;
  right: -160rpx;
}

/* 登录卡片 - 移动端优化 */
.login-card {
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20rpx);
  padding: 64rpx 48rpx;
  border-radius: 40rpx;
  box-shadow: 0 30rpx 70rpx rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 800rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 56rpx;
}

.title {
  color: #2c3e50;
  font-size: 44rpx;
  margin-bottom: 16rpx;
  letter-spacing: 1rpx;
  display: block;
  font-weight: 700;
}

.subtitle {
  color: #909399;
  font-size: 28rpx;
  display: block;
}

.form-item {
  margin-bottom: 48rpx;
}

.label {
  font-weight: 600;
  color: #475569;
  margin-bottom: 16rpx;
  font-size: 28rpx;
  display: block;
}

.input-field {
  width: 100%;
  min-height: 96rpx;
  border-radius: 24rpx;
  font-size: 32rpx;
  padding: 24rpx 32rpx;
  background: #ffffff;
  border: 2rpx solid #e2e8f0;
  box-sizing: border-box;
}

.input-field:focus {
  border-color: #838B8B;
}

.login-options {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 48rpx;
}

.forgot-link {
  color: #838B8B;
  font-size: 28rpx;
  padding: 16rpx 8rpx;
}

.submit-btn {
  width: 100%;
  height: 104rpx;
  background-color: #838B8B;
  color: white;
  font-size: 34rpx;
  font-weight: bold;
  border-radius: 24rpx;
  border: none;
  margin-top: 16rpx;
}

.submit-btn:active {
  background-color: #6e7575;
  transform: scale(0.98);
}
</style>
