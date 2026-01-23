<template>
  <scroll-view class="register-container" scroll-y>
    <view class="register-card">
      <view class="header-section">
        <text class="title">开启健康之旅</text>
        <text class="subtitle">请完善您的个人资料，以便我们为您制定排行</text>
      </view>

      <view class="section-title">账号设置</view>
      <view class="form-group">
        <view class="form-item">
          <input v-model="form.username" placeholder="用户名" class="input-field" />
        </view>
        <view class="form-item">
          <input v-model="form.email" type="email" placeholder="邮箱地址" class="input-field" />
        </view>
        <view class="form-item">
          <input type="password" v-model="form.password" placeholder="设置密码" class="input-field" />
        </view>
      </view>

      <view class="section-title">基本信息</view>
      <view class="form-group">
        <view class="form-item">
          <text class="inner-label">性别</text>
          <view class="radio-group">
            <label class="radio-item" :class="{ active: form.gender === 'male' }" @tap="form.gender = 'male'">
              <radio value="male" :checked="form.gender === 'male'" color="#838B8B" />
              <text>男</text>
            </label>
            <label class="radio-item" :class="{ active: form.gender === 'female' }" @tap="form.gender = 'female'">
              <radio value="female" :checked="form.gender === 'female'" color="#838B8B" />
              <text>女</text>
            </label>
          </view>
        </view>
        <view class="form-item">
          <text class="inner-label">出生日期</text>
          <picker mode="date" :value="form.birthdate" @change="onDateChange">
            <view class="picker-field">
              <text class="picker-display" :class="{ placeholder: !form.birthdate }">
                {{ form.birthdate || '请选择出生日期' }}
              </text>
            </view>
          </picker>
        </view>
      </view>

      <view class="section-title">身体指标</view>
      <view class="form-row">
        <view class="form-item half">
          <text class="inner-label">身高 (cm)</text>
          <input type="number" v-model.number="form.height_cm" placeholder="请输入身高" class="input-field" />
        </view>
        <view class="form-item half">
          <text class="inner-label">体重 (kg)</text>
          <input type="number" v-model.number="form.weight_kg" placeholder="请输入体重" class="input-field" />
        </view>
      </view>

      <view class="section-title">您的身份</view>
      <view class="identity-grid">
        <view 
          v-for="item in identityOptions" 
          :key="item.value"
          class="identity-card"
          :class="{ active: form.identity === item.value }"
          @tap="form.identity = item.value"
        >
          <view class="id-icon">{{ item.icon }}</view>
          <view class="id-content">
            <text class="id-label">{{ item.label }}</text>
            <text class="id-desc">{{ item.desc }}</text>
          </view>
          <view class="check-mark" v-if="form.identity === item.value">
            <icon type="success_no_circle" size="12" color="#fff"/>
          </view>
        </view>
      </view>

      <view class="section-title">活动水平</view>
      <view class="option-grid">
        <view 
          v-for="(item, index) in activityOptions" 
          :key="item.value"
          class="option-item"
          :class="{ active: activityIndex === index }"
          @tap="onActivityChangeDirect(index)"
        >
          <text class="option-label">{{ item.label }}</text>
        </view>
      </view>

      <view class="section-title">健身目标</view>
      <view class="identity-grid"> <view 
          v-for="(item, index) in goalOptions" 
          :key="item.value"
          class="identity-card"
          :class="{ active: goalIndex === index }"
          @tap="onGoalChangeDirect(index)"
        >
          <!-- <view class="id-icon">{{ item.icon }}</view> -->
          <view class="id-content">
            <text class="id-label">{{ item.label }}</text>
            <text class="id-desc">{{ item.desc }}</text>
          </view>
          <view class="check-mark" v-if="goalIndex === index">
            <icon type="success_no_circle" size="12" color="#fff"/>
          </view>
        </view>
      </view>

      <button
        class="submit-register-btn"
        @tap="onSubmit"
        :loading="submitting"
      >
        即刻加入
      </button>
    </view>
  </scroll-view>
</template>


<script setup>
import { reactive, ref } from 'vue'
import api from '@/services/api'

const form = reactive({
  username: '',
  email: '',
  password: '',
  gender: 'male', // 默认选择男性
  birthdate: '',
  height_cm: null,
  weight_kg: null,
  activity_level: 'sedentary',
  goal: 'maintain',
  identity: 'office_worker'
})

const submitting = ref(false)
const activityIndex = ref(0)
const goalIndex = ref(0)
const identityIndex = ref(1) // 默认选择职场办公人

const activityOptions = [
  { label: '久坐', value: 'sedentary' },
  { label: '轻度活跃', value: 'lightly_active' },
  { label: '中度活跃', value: 'moderately_active' },
  { label: '非常活跃', value: 'very_active' },
  { label: '极度活跃', value: 'extra_active' }
]

const goalOptions = [
  { label: '维持身材', value: 'maintain' },
  { label: '减重', value: 'lose_weight' },
  { label: '增肌', value: 'gain_muscle' },
  { label: '增重', value: 'gain_weight' }
]

const identityOptions = [
  { label: '学生族', value: 'student' },
  { label: '职场办公人', value: 'office_worker' },
  { label: '自由职业/居家', value: 'flexible' },
  { label: '健身达人', value: 'fitness_pro' },
  { label: '康养人群', value: 'health_care' }
]

const onDateChange = (e) => {
  form.birthdate = e.detail.value
}
// 直接点击修改活动水平
const onActivityChangeDirect = (index) => {
  activityIndex.value = index;
  form.activity_level = activityOptions[index].value;
};

// 直接点击修改目标
const onGoalChangeDirect = (index) => {
  goalIndex.value = index;
  form.goal = goalOptions[index].value;
};

const onSubmit = async () => {
  // 验证必填字段
  if (!form.username || !form.email || !form.password) {
    uni.showToast({
      title: '请填写账号信息',
      icon: 'none'
    })
    return
  }
  
  if (!form.gender) {
    uni.showToast({
      title: '请选择性别',
      icon: 'none'
    })
    return
  }
  
  if (!form.birthdate) {
    uni.showToast({
      title: '请选择出生日期',
      icon: 'none'
    })
    return
  }
  
  if (!form.height_cm || form.height_cm <= 0) {
    uni.showToast({
      title: '请输入有效的身高',
      icon: 'none'
    })
    return
  }
  
  if (!form.weight_kg || form.weight_kg <= 0) {
    uni.showToast({
      title: '请输入有效的体重',
      icon: 'none'
    })
    return
  }
  
  submitting.value = true
  try {
    // 确保数据类型正确，并转换日期格式
    const submitData = {
      username: form.username,
      email: form.email,
      password: form.password,
      gender: form.gender,
      birthdate: form.birthdate, // 日期格式：YYYY-MM-DD
      height_cm: parseFloat(form.height_cm),
      weight_kg: parseFloat(form.weight_kg),
      activity_level: form.activity_level,
      goal: form.goal,
      identity: form.identity
    }
    await api.createUser(submitData)
    // 注册成功后自动登录
    const loginRes = await api.login({
      username: form.username,
      password: form.password
    })
    if (loginRes && loginRes.access_token) {
      uni.setStorageSync('token', loginRes.access_token)
      uni.showToast({
        title: '注册成功',
        icon: 'success'
      })
      setTimeout(() => {
        uni.reLaunch({
          url: '/pages/home/home'
        })
      }, 1500)
    } else {
      uni.showToast({
        title: '注册成功，请登录',
        icon: 'success'
      })
      setTimeout(() => {
        uni.redirectTo({
          url: '/pages/login/login'
        })
      }, 1500)
    }
  } catch (error) {
    uni.showToast({
      title: '注册失败，请检查输入信息',
      icon: 'none'
    })
    console.error(error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">

.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  display: flex;
  flex-direction: column;
  /* 移除原本可能干扰的 padding，改由内部 card 控制或统一控制 */
  padding: calc(env(safe-area-inset-top) + 40rpx) 0 calc(env(safe-area-inset-bottom) + 40rpx);
}

.register-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20rpx);
  padding: 64rpx 40rpx; /* 稍微缩小内边距，给输入框留空间 */
  border-radius: 40rpx;
  box-shadow: 0 30rpx 70rpx rgba(0, 0, 0, 0.05);
  
  /* 居中逻辑修复 */
  width: 686rpx;      /* 保持标准的 750 设计稿下的居中宽度 */
  margin: 0 auto;     /* 严格水平居中 */
  
  border: 2rpx solid rgba(255, 255, 255, 0.3);
  box-sizing: border-box; /* 确保 padding 不撑开宽度 */
}

.title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 56rpx;
  font-size: 44rpx;
  font-weight: 700;
  display: block;
}

.form-group {
  margin-bottom: 20rpx;
  width: 100%;
  box-sizing: border-box;
}

.form-item {
  margin-bottom: 32rpx;
  width: 100%;
  box-sizing: border-box;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.form-row {
  display: flex;
  justify-content: space-between; /* 左右两端对齐 */
  gap: 20rpx;
  width: 100%;
}

.form-item-half {
  flex: 1; /* 平分空间 */
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

.picker-field {
  width: 100%;
  min-height: 96rpx;
  border-radius: 24rpx;
  padding: 24rpx 32rpx;
  background: #ffffff;
  border: 2rpx solid #e2e8f0;
  box-sizing: border-box;
  display: flex;
  align-items: center;
}

.picker-display {
  font-size: 32rpx;
  color: #333;
  line-height: 1.5;
  word-break: break-word;
  
  &.placeholder {
    color: #999;
  }
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  width: 100%;
}

.radio-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 20rpx 32rpx;
  background: #f8f9fa;
  border: 2rpx solid #e2e8f0;
  border-radius: 24rpx;
  flex: 1;
  min-width: 0;
  transition: all 0.2s;
  
  &.active {
    background: #e8f4f8;
    border-color: #838B8B;
  }
}

.radio-item text {
  font-size: 28rpx;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.submit-register-btn {
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

.submit-register-btn:active {
  background-color: #6e7575;
  transform: scale(0.98);
}
.header-section {
  text-align: center;
  margin-bottom: 60rpx;
  .subtitle {
    font-size: 24rpx;
    color: #94a3b8;
    margin-top: 10rpx;
  }
}
/* 活动水平网格：一行多个 */
.option-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 40rpx;
  width: 100%;
}

.option-item {
  flex: 1;
  min-width: 180rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border: 2rpx solid #f1f5f9;
  border-radius: 20rpx;
  transition: all 0.2s;
  
  .option-label {
    font-size: 26rpx;
    color: #64748b;
  }

  &.active {
    background: #eef2f2;
    border-color: #838B8B;
    .option-label {
      color: #838B8B;
      font-weight: bold;
    }
  }
}

/* 目标选择：更宽的单行样式 */
.goal-group {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.goal-card {
  display: flex;
  align-items: center;
  padding: 30rpx 40rpx;
  background: #f8fafc;
  border: 2rpx solid #f1f5f9;
  border-radius: 24rpx;
  font-size: 30rpx;
  color: #1e293b;
  position: relative;
  
  .goal-dot {
    width: 16rpx;
    height: 16rpx;
    border-radius: 50%;
    background: #cbd5e1;
    margin-right: 24rpx;
  }

  &.active {
    border-color: #838B8B;
    background: #ffffff;
    box-shadow: 0 8rpx 20rpx rgba(131, 139, 139, 0.08);
    .goal-dot {
      background: #838B8B;
      box-shadow: 0 0 10rpx rgba(131, 139, 139, 0.5);
    }
  }
}
.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
  margin: 40rpx 0 20rpx 10rpx;
  position: relative;
  &::before {
    content: '';
    position: absolute;
    left: -20rpx;
    top: 50%;
    transform: translateY(-50%);
    width: 8rpx;
    height: 24rpx;
    background: #838B8B;
    border-radius: 4rpx;
  }
}

/* 身份卡片网格系统 */
.identity-grid {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 60rpx;
}

.identity-card {
  display: flex;
  align-items: center;
  padding: 30rpx;
  background: #f8fafc;
  border: 3rpx solid #f1f5f9;
  border-radius: 24rpx;
  position: relative;
  transition: all 0.3s ease;

  &.active {
    background: #ffffff;
    border-color: #838B8B;
    box-shadow: 0 10rpx 30rpx rgba(131, 139, 139, 0.1);
  }

  .id-icon {
    font-size: 40rpx;
    margin-right: 24rpx;
  }

  .id-label {
    font-size: 30rpx;
    font-weight: 600;
    color: #1e293b;
    display: block;
  }

  .id-desc {
    font-size: 22rpx;
    color: #64748b;
  }

  .check-mark {
    position: absolute;
    right: 30rpx;
    width: 36rpx;
    height: 36rpx;
    background: #838B8B;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* 内置 Label 的输入框 */
.inner-label {
  font-size: 22rpx;
  color: #94a3b8;
  margin-bottom: 8rpx;
  padding-left: 10rpx;
}

</style>
