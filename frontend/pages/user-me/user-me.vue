<template>
  <view class="app-safe-area">
    <view class="user-me-container">
      <view v-if="loading" class="loading-wrapper">
        <text>加载中...</text>
      </view>

      <scroll-view v-else class="profile-scroll" scroll-y>
        <view class="profile-layout">
          <!-- 用户信息卡片 -->
          <view class="sidebar-card">
            <view class="avatar-section">
              <view class="user-avatar">{{ user.username?.charAt(0).toUpperCase() || 'U' }}</view>
              <text class="username">{{ user.username }}</text>
              <view class="email-tag">{{ user.email }}</view>
            </view>
            <view class="info-list">
              <view class="info-item">
                <text class="label">性别</text>
                <text class="value">{{ translateGender(user.gender) }}</text>
              </view>
              <view class="info-item">
                <text class="label">生日</text>
                <text class="value">{{ user.birthdate || '未设置' }}</text>
              </view>
            </view>
          </view>

          <!-- 健康档案详情卡片 -->
          <view class="detail-content">
            <view class="card-header">
              <text class="card-title">健康档案详情</text>
            </view>
            
            <view class="stat-grid">
              <view class="stat-box">
                <text class="stat-label">身高</text>
                <view class="stat-main">
                  <text class="stat-value">{{ user.height_cm || '--' }}</text>
                  <text class="stat-unit">cm</text>
                </view>
              </view>
              <view class="stat-box">
                <text class="stat-label">体重</text>
                <view class="stat-main">
                  <text class="stat-value">{{ user.weight_kg || '--' }}</text>
                  <text class="stat-unit">kg</text>
                </view>
              </view>
              <view class="stat-box">
                <text class="stat-label">活动水平</text>
                <text class="stat-value-text">{{ translateActivity(user.activity_level) }}</text>
              </view>
              <view class="stat-box">
                <text class="stat-label">健身目标</text>
                <text class="stat-value-text">{{ translateGoal(user.goal) }}</text>
              </view>
              <view class="stat-box">
                <text class="stat-label">身份</text>
                <text class="stat-value-text">{{ translateIdentity(user.identity) }}</text>
              </view>
            </view>

            <view class="health-dashboard" v-if="bmiValue">
              <view class="dashboard-divider"></view>
              <view class="dashboard-item">
                <view class="dash-left">
                  <text class="dash-label">当前 BMI 指数</text>
                  <view class="dash-main">
                    <text class="dash-value">{{ bmiValue }}</text>
                    <view class="status-tag" :style="{ backgroundColor: bmiStatus.color }">
                      <text>{{ bmiStatus.text }}</text>
                    </view>
                  </view>
                </view>
                <view class="dash-right">
                  <text class="dash-tips">标准范围：18.5 ~ 23.9</text>
                  <view class="bmi-bar">
                    <view class="bmi-pointer" :style="{ left: bmiPosition + '%' }"></view>
                  </view>
                </view>
              </view>
            </view>
          </view>

          <!-- 编辑资料和退出登录按钮 -->
          <view class="action-section">
            <button class="btn-action btn-edit" @tap="openEditDialog">
              <text class="action-text">编辑资料</text>
            </button>
            <button class="btn-action btn-password" @tap="openPasswordDialog">
              <text class="action-text">修改密码</text>
            </button>
            <button class="btn-action btn-logout" @tap="handleLogout">
              <text class="action-text">退出登录</text>
            </button>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 编辑对话框 -->
    <view v-if="editDialogVisible" class="popup-mask" @tap="closeEditDialog">
      <view class="popup-content" @tap.stop>
        <view class="popup-header">
          <text class="popup-title">修改个人资料</text>
          <text class="popup-close" @tap="closeEditDialog">×</text>
        </view>

        <scroll-view class="popup-body" scroll-y>
          <!-- 性别 -->
          <view class="form-item">
            <text class="label">性别</text>
            <picker
              mode="selector"
              :range="genderOptions"
              range-key="label"
              :value="genderIndex"
              @change="onGenderChange"
              class="picker-field"
            >
              <view class="picker-display">
                {{ genderOptions[genderIndex]?.label || '请选择' }}
              </view>
            </picker>
          </view>

          <!-- 生日 -->
          <view class="form-item">
            <text class="label">生日</text>
            <picker
              mode="date"
              :value="editForm.birthdate"
              @change="onDateChange"
              class="picker-field"
            >
              <view class="picker-display">
                {{ editForm.birthdate || '选择日期' }}
              </view>
            </picker>
          </view>

          <!-- 身高 / 体重 -->
          <view class="form-row">
            <view class="form-item form-item-half">
              <text class="label">身高 (cm)</text>
              <input
                type="number"
                v-model.number="editForm.height_cm"
                placeholder="请输入身高"
                class="input-field"
              />
            </view>
            <view class="form-item form-item-half">
              <text class="label">体重 (kg)</text>
              <input
                type="number"
                v-model.number="editForm.weight_kg"
                placeholder="请输入体重"
                class="input-field"
              />
            </view>
          </view>

          <!-- 活动水平 -->
          <view class="form-item">
            <text class="label">活动水平</text>
            <picker
              mode="selector"
              :range="activityOptions"
              range-key="label"
              :value="activityIndex"
              @change="onActivityChange"
              class="picker-field"
            >
              <view class="picker-display">
                {{ activityOptions[activityIndex]?.label || '请选择活动水平' }}
              </view>
            </picker>
          </view>

          <!-- 健身目标 -->
          <view class="form-item">
            <text class="label">健身目标</text>
            <picker
              mode="selector"
              :range="goalOptions"
              range-key="label"
              :value="goalIndex"
              @change="onGoalChange"
              class="picker-field"
            >
              <view class="picker-display">
                {{ goalOptions[goalIndex]?.label || '请选择' }}
              </view>
            </picker>
          </view>

          <!-- 身份 -->
          <view class="form-item">
            <text class="label">身份</text>
            <picker
              mode="selector"
              :range="identityOptions"
              range-key="label"
              :value="identityIndex"
              @change="onIdentityChange"
              class="picker-field"
            >
              <view class="picker-display">
                {{ identityOptions[identityIndex]?.label || '请选择身份' }}
              </view>
            </picker>
          </view>
        </scroll-view>

        <view class="popup-footer">
          <button class="btn-cancel" @tap="closeEditDialog">取消</button>
          <button class="btn-save" @tap="handleUpdate" :loading="submitting">
            保存修改
          </button>
        </view>
      </view>
    </view>

    <!-- 修改密码对话框 -->
    <view v-if="passwordDialogVisible" class="popup-mask" @tap="closePasswordDialog">
      <view class="popup-content" @tap.stop>
        <view class="popup-header">
          <text class="popup-title">修改密码</text>
          <text class="popup-close" @tap="closePasswordDialog">×</text>
        </view>

        <view class="popup-body">
          <view class="form-item">
            <text class="label">旧密码</text>
            <input
              type="password"
              v-model="passwordForm.old_password"
              placeholder="请输入旧密码"
              class="input-field"
            />
          </view>

          <view class="form-item">
            <text class="label">新密码</text>
            <input
              type="password"
              v-model="passwordForm.new_password"
              placeholder="请输入新密码"
              class="input-field"
            />
          </view>

          <view class="form-item">
            <text class="label">确认新密码</text>
            <input
              type="password"
              v-model="passwordForm.confirm_password"
              placeholder="请再次输入新密码"
              class="input-field"
            />
          </view>
        </view>

        <view class="popup-footer">
          <button class="btn-cancel" @tap="closePasswordDialog">取消</button>
          <button class="btn-save" @tap="handlePasswordChange" :loading="passwordSubmitting">
            确认修改
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '@/services/api'

const handleBack = () => {
  uni.navigateBack()
}

const loading = ref(true)
const submitting = ref(false)
const editDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const passwordSubmitting = ref(false)
const user = ref({})

const editForm = reactive({
  gender: '',
  birthdate: '',
  height_cm: null,
  weight_kg: null,
  activity_level: '',
  goal: '',
  identity: ''
})

const genderIndex = ref(0)
const activityIndex = ref(0)
const goalIndex = ref(0)
const identityIndex = ref(0)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const genderOptions = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' },
  { label: '保密', value: 'unwilling_to_disclose' }
]

const activityOptions = [
  { label: '久坐不动', value: 'sedentary' },
  { label: '轻度活跃', value: 'lightly_active' },
  { label: '中度活跃', value: 'moderately_active' },
  { label: '高度活跃', value: 'very_active' },
  { label: '极高强度', value: 'extra_active' }
]

const goalOptions = [
  { label: '保持体重', value: 'maintain' },
  { label: '减脂/减重', value: 'lose_weight' },
  { label: '增肌训练', value: 'gain_muscle' }
]

const identityOptions = [
  { label: '学生族', value: 'student' },
  { label: '职场办公人', value: 'office_worker' },
  { label: '自由职业/居家', value: 'flexible' },
  { label: '健身达人', value: 'fitness_pro' },
  { label: '康养人群', value: 'health_care' }
]

// 翻译函数
const translateGender = (g) => ({ male: '男', female: '女', unwilling_to_disclose: '保密' }[g] || '未设置')
const translateActivity = (a) => ({ sedentary: '久坐不动', lightly_active: '轻度活跃', moderately_active: '中度活跃', very_active: '高度活跃', extra_active: '极高强度' }[a] || '未设置')
const translateGoal = (goal) => ({ maintain: '保持体重', lose_weight: '减脂/减重', gain_muscle: '增肌训练' }[goal] || '未设置')
const translateIdentity = (identity) => {
  const map = {
    'student': '学生族',
    'office_worker': '职场办公人',
    'flexible': '自由职业/居家',
    'fitness_pro': '健身达人',
    'health_care': '康养人群'
  }
  return map[identity] || '未设置'
}

// BMI 计算逻辑
const bmiValue = computed(() => {
  if (!user.value.height_cm || !user.value.weight_kg) return null
  const heightM = user.value.height_cm / 100
  return (user.value.weight_kg / (heightM * heightM)).toFixed(1)
})

const bmiStatus = computed(() => {
  const val = parseFloat(bmiValue.value)
  if (!val) return { text: '--', color: '#94a3b8' }
  if (val < 18.5) return { text: '偏瘦', color: '#838B8B' }
  if (val < 24) return { text: '标准', color: '#2ecc71' }
  if (val < 28) return { text: '过重', color: '#e67e22' }
  return { text: '肥胖', color: '#e74c3c' }
})

const bmiPosition = computed(() => {
  const val = parseFloat(bmiValue.value)
  if (!val) return 0
  const pos = ((val - 15) / (35 - 15)) * 100
  return Math.min(Math.max(pos, 5), 95)
})

const fetchUserData = async () => {
  try {
    loading.value = true
    const response = await api.getMe()
    // request.js 直接返回 data，不是 response.data
    if (response) {
      user.value = response
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    uni.showToast({
      title: '获取资料失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

const openEditDialog = () => {
  Object.assign(editForm, {
    gender: user.value.gender,
    birthdate: user.value.birthdate,
    height_cm: user.value.height_cm,
    weight_kg: user.value.weight_kg,
    activity_level: user.value.activity_level,
    goal: user.value.goal,
    identity: user.value.identity || 'office_worker'
  })
  
  // 设置索引
  genderIndex.value = genderOptions.findIndex(g => g.value === editForm.gender)
  activityIndex.value = activityOptions.findIndex(a => a.value === editForm.activity_level)
  goalIndex.value = goalOptions.findIndex(g => g.value === editForm.goal)
  identityIndex.value = identityOptions.findIndex(i => i.value === editForm.identity)
  if (identityIndex.value === -1) identityIndex.value = 1 // 默认职场办公人
  
  editDialogVisible.value = true
}

const closeEditDialog = () => {
  editDialogVisible.value = false
}

const openPasswordDialog = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordDialogVisible.value = true
}

const closePasswordDialog = () => {
  passwordDialogVisible.value = false
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

const onGenderChange = (e) => {
  genderIndex.value = e.detail.value
  editForm.gender = genderOptions[e.detail.value].value
}

const onDateChange = (e) => {
  editForm.birthdate = e.detail.value
}

const onActivityChange = (e) => {
  activityIndex.value = e.detail.value
  editForm.activity_level = activityOptions[e.detail.value].value
}

const onGoalChange = (e) => {
  goalIndex.value = e.detail.value
  editForm.goal = goalOptions[e.detail.value].value
}

const onIdentityChange = (e) => {
  identityIndex.value = e.detail.value
  editForm.identity = identityOptions[e.detail.value].value
}

const handleUpdate = async () => {
  try {
    submitting.value = true
    await api.updateMe(editForm)
    uni.showToast({
      title: '资料更新成功',
      icon: 'success'
    })
    closeEditDialog()
    await fetchUserData()
  } catch (error) {
    uni.showToast({
      title: '更新失败',
      icon: 'none'
    })
  } finally {
    submitting.value = false
  }
}

const handlePasswordChange = async () => {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
    uni.showToast({
      title: '请填写完整信息',
      icon: 'none'
    })
    return
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    uni.showToast({
      title: '两次输入的新密码不一致',
      icon: 'none'
    })
    return
  }

  if (passwordForm.new_password.length < 6) {
    uni.showToast({
      title: '新密码长度至少6位',
      icon: 'none'
    })
    return
  }

  passwordSubmitting.value = true
  try {
    await api.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    uni.showToast({
      title: '密码修改成功',
      icon: 'success'
    })
    closePasswordDialog()
  } catch (error) {
    console.error('修改密码失败:', error)
    const errorMessage = error?.response?.data?.detail || error?.message || '修改密码失败'
    uni.showToast({
      title: errorMessage,
      icon: 'none',
      duration: 2000
    })
  } finally {
    passwordSubmitting.value = false
  }
}

// 退出登录
const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    confirmText: '退出',
    cancelText: '取消',
    confirmColor: '#e74c3c',
    success: (res) => {
      if (res.confirm) {
        // 清除本地存储的 token 和用户信息
        uni.removeStorageSync('token')
        uni.removeStorageSync('remembered_username')
        
        uni.showToast({
          title: '已退出登录',
          icon: 'success',
          duration: 1500
        })
        
        // 延迟跳转，让提示显示
        setTimeout(() => {
          uni.reLaunch({
            url: '/pages/home/home'
          })
        }, 500)
      }
    }
  })
}

onMounted(fetchUserData)
</script>

<style scoped lang="scss">
.app-safe-area {
  background-color: #f8fafc;
  min-height: 100vh;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  display: flex;
  flex-direction: column;
}

.user-me-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 32rpx 40rpx;
  padding-top: calc(32rpx + env(safe-area-inset-top) + 20rpx);
  background: transparent;
  position: absolute;
  top: 30rpx;
  left: 0;
  right: 0;
  z-index: 100;
}

.back-icon-btn {
  background: none;
  border: none;
  padding: 0;
  color: #1e293b;
  min-width: 64rpx;
  min-height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 56rpx;
  font-weight: bold;
  line-height: 1;
}

.header-spacer {
  display: none;
}

.loading-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-scroll {
  flex: 1;
}

.profile-layout {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  padding: 32rpx;
  max-width: 100%;
  box-sizing: border-box;
  align-items: center;
}

.sidebar-card {
  width: 100%;
  max-width: 100%;
  background: #fff;
  border-radius: 40rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8rpx 40rpx rgba(0,0,0,0.03);
  text-align: center;
  box-sizing: border-box;
}

.user-avatar {
  width: 160rpx;
  height: 160rpx;
  background-color: #838B8B;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64rpx;
  font-weight: bold;
  margin: 0 auto 32rpx;
}

.username {
  font-size: 44rpx;
  color: #2d3436;
  margin-bottom: 16rpx;
  display: block;
}

.email-tag {
  color: #838B8B;
  border: 2rpx solid #838B8B;
  padding: 8rpx 24rpx;
  border-radius: 40rpx;
  font-size: 24rpx;
  display: inline-block;
  margin-bottom: 48rpx;
}

.info-list {
  border-top: 2rpx solid #f0f0f0;
  padding-top: 40rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
  font-size: 28rpx;
  padding: 16rpx 0;
  gap: 16rpx;
}

.label {
  color: #94a3b8;
}

.value {
  color: #2d3436;
  font-weight: 500;
}

.detail-content {
  width: 100%;
  max-width: 100%;
  background: #fff;
  border-radius: 40rpx;
  padding: 48rpx 40rpx;
  box-shadow: 0 8rpx 40rpx rgba(0,0,0,0.03);
  box-sizing: border-box;
}

.card-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 40rpx;
}

.card-title {
  color: #838B8B;
  font-size: 36rpx;
  font-weight: 700;
}

.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

.stat-box {
  background: #f8fafc;
  padding: 36rpx;
  border-radius: 30rpx;
  box-sizing: border-box;
  min-width: 0;
  overflow: hidden;
  text-align: center;
}

.stat-label {
  font-size: 24rpx;
  color: #94a3b8;
  display: block;
  margin-bottom: 16rpx;
}

.stat-main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8rpx;
}

.stat-value {
  font-size: 52rpx;
  font-weight: bold;
  color: #2d3436;
}

.stat-unit {
  font-size: 24rpx;
  color: #94a3b8;
}

.stat-value-text {
  font-size: 34rpx;
  font-weight: 600;
  color: #838B8B;
  text-align: center;
  word-break: break-word;
  overflow-wrap: break-word;
}

.dashboard-divider {
  height: 2rpx;
  background: #f0f0f0;
  margin: 32rpx 0 40rpx;
}

.dashboard-item {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  background: #fcfcfc;
  padding: 40rpx;
  border-radius: 30rpx;
}

.dash-main {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-top: 8rpx;
}

.dash-value {
  font-size: 72rpx;
  font-weight: 800;
  color: #2d3436;
}

.status-tag {
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  color: white;
}

.dash-right {
  width: 100%;
}

.dash-tips {
  font-size: 24rpx;
  color: #94a3b8;
  margin-bottom: 20rpx;
  display: block;
}

.bmi-bar {
  height: 16rpx;
  background: linear-gradient(to right, #3498db, #2ecc71, #f1c40f, #e74c3c);
  border-radius: 8rpx;
  position: relative;
}

.bmi-pointer {
  position: absolute;
  top: -8rpx;
  width: 4rpx;
  height: 32rpx;
  background: #2d3436;
  transition: left 0.5s;
}

/* 弹窗样式 */
.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.popup-content {
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  max-height: 85vh;
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
  box-sizing: border-box;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 32rpx;
  border-bottom: 2rpx solid #f0f0f0;
  box-sizing: border-box;
}

.popup-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1e293b;
  text-align: center;
  flex: 1;
}

.popup-close {
  font-size: 60rpx;
  color: #94a3b8;
  line-height: 1;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.popup-body {
  flex: 1;
  padding: 40rpx 32rpx;
  max-height: 60vh;
  box-sizing: border-box;
}

.form-item {
  margin-bottom: 40rpx;
  width: 100%;
  box-sizing: border-box;
}

.form-row {
  display: flex;
  gap: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

.form-item-half {
  flex: 1;
  min-width: 0;
  box-sizing: border-box;
}

.label {
  font-weight: 600;
  color: #475569;
  margin-bottom: 16rpx;
  font-size: 28rpx;
  display: block;
  text-align: left;
}

.input-field {
  width: 100%;
  min-height: 96rpx;
  border-radius: 24rpx;
  font-size: 32rpx;
  padding: 24rpx 32rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  box-sizing: border-box;
  text-align: left;
  
  &:focus {
    border-color: #838B8B;
    background: #fff;
  }
}

.picker-field {
  width: 100%;
  min-height: 96rpx;
  border-radius: 24rpx;
  padding: 24rpx 32rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}

.picker-display {
  font-size: 32rpx;
  color: #333;
  text-align: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.popup-footer {
  display: flex;
  gap: 24rpx;
  padding: 40rpx;
  border-top: 2rpx solid #f0f0f0;
}

.btn-cancel {
  flex: 1;
  height: 88rpx;
  border: 2rpx solid #e2e8f0;
  color: #475569;
  border-radius: 24rpx;
  background: transparent;
  font-size: 32rpx;
}

.btn-save {
  flex: 1;
  height: 88rpx;
  background-color: #838B8B;
  color: white;
  border: none;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 600;
}

/* 操作按钮区域 */
.action-section {
  width: 100%;
  max-width: 100%;
  padding: 32rpx 0 80rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.btn-action {
  width: 100%;
  height: 96rpx;
  background: #ffffff;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border: none;
}

.btn-edit {
  border: 2rpx solid #838B8B;
  color: #838B8B;
}

.btn-edit:active {
  background: #f8fafc;
  transform: scale(0.98);
}

.btn-password {
  border: 2rpx solid #3b82f6;
  color: #3b82f6;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.1);
}

.btn-password:active {
  background: #eff6ff;
  transform: scale(0.98);
}

.btn-logout {
  border: 2rpx solid #fee2e2;
  color: #ef4444;
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.1);
}

.btn-logout:active {
  background: #fef2f2;
  transform: scale(0.98);
}

.action-text {
  font-size: 32rpx;
}
</style>
