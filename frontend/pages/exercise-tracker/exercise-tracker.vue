<template>
  <view class="app-safe-area">
    <view class="app-container">
      <view class="app-header">
        <view class="header-left">
          <text class="app-title">运动追踪</text>
        </view>
      </view>

      <scroll-view class="app-content-scroll" scroll-y>
        <view class="scroll-inner">
          <view class="log-card">
            <view class="form-item">
              <text class="label">运动项目</text>
              <picker
                mode="selector"
                :range="exerciseOptions"
                range-key="name"
                @change="onExerciseChange"
                class="picker-field"
              >
                <view class="picker-display">
                  <text class="picker-text">{{ exerciseOptions[exerciseIndex]?.name || '选择运动类型' }}</text>
                  <text class="arrow-down">▼</text>
                </view>
              </picker>
            </view>

            <view class="form-row">
              <view class="form-item half">
                <text class="label">时长 (分钟)</text>
                <view class="input-wrapper">
                  <input
                    type="number"
                  v-model.number="form.duration_minutes"
                    placeholder="0"
                    class="input-field"
                  />
                </view>
              </view>
            <view class="form-item half">
              <text class="label">体重(kg)-可手动修改</text>
              <view class="input-wrapper">
                <input
                  type="number"
                  v-model.number="form.weight_kg"
                  placeholder="60"
                  class="input-field"
                />
              </view>
            </view>
            </view>
          <view class="form-item half">
            <text class="label">日期</text>
            <picker mode="date" :value="logDate" @change="onDateChange" class="picker-field">
              <view class="picker-display">
                <text class="picker-text">{{ logDate }}</text>
              </view>
            </picker>
          </view>

          <view class="form-item">
            <text class="label">消耗热量(kcal)-可手动修改</text>
            <view class="input-wrapper">
              <input
                type="number"
                v-model.number="form.calories_burned"
                @input="manualCalories.value = true"
                :placeholder="`已为你预估 ${estimatedCalories} kcal，可手动修改`"
                class="input-field"
              />
            </view>
          </view>

            <view class="form-item">
              <text class="label">备注 (可选)</text>
              <textarea
                v-model="notes"
                placeholder="记录今天的心情或感受..."
                class="textarea-field"
                fixed
              />
            </view>

            <button class="btn-primary-mobile" @tap="handleSubmit" :loading="submitting" hover-class="btn-hover">
              保存记录
            </button>
          </view>

          <view class="tips-section">
            <view class="tip-card">
              <text class="tip-icon">💡</text>
              <text class="tip-text">坚持每天 30 分钟有氧运动能更有效地达到减脂目标。</text>
            </view>
          </view>
          
          <view class="safe-bottom-pad"></view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import api from '@/services/api'

const exercises = ref([])
const exerciseIndex = ref(0)
const form = reactive({
  exercise_id: null,
  duration_minutes: 30,
  weight_kg: 60,
  calories_burned: null
})
const logDate = ref(new Date().toISOString().split('T')[0])
const notes = ref('')
const submitting = ref(false)
const userWeight = ref(null)
const manualCalories = ref(false) // 用户是否手动输入卡路里

const exerciseOptions = computed(() => {
  if (!Array.isArray(exercises.value)) return []
  return exercises.value.map(e => ({
    name: e.name,
    id: e.id,
    met_value: e.met_value || 0
  }))
})

const selectedExercise = computed(() => {
  if (!Array.isArray(exercises.value)) return null
  return exercises.value.find(e => e.id === form.exercise_id) || null
})

const estimatedCalories = computed(() => {
  if (!selectedExercise.value) return 0
  const met = selectedExercise.value.met_value || 0
  const weight = Number(form.weight_kg || userWeight.value) || 0
  const hours = Number(form.duration_minutes || 0) / 60
  if (!met || !weight || !hours) return 0
  return Math.round(met * weight * hours)
})

const getExercises = async () => {
  try {
    const response = await api.getExercises()
    // request.js 直接返回 data，不是 response.data
    exercises.value = Array.isArray(response) ? response : []
    if (exercises.value.length === 0) {
      uni.showToast({
        title: '暂无运动项目',
        icon: 'none'
      })
      return
    }
    // 进入页面即默认选中第一个运动，确保“预计消耗”可直接计算
    if (!form.exercise_id) {
      exerciseIndex.value = 0
      form.exercise_id = exercises.value[0].id
    } else {
      // 如果已存在 exercise_id（比如返回上一页），同步 index，避免显示与计算不一致
      const idx = exercises.value.findIndex(e => e.id === form.exercise_id)
      if (idx >= 0) exerciseIndex.value = idx
    }
  } catch (error) {
    console.error('获取运动列表失败:', error)
    exercises.value = []
    uni.showToast({
      title: '获取运动列表失败',
      icon: 'none'
    })
  }
}

const getUserProfile = async () => {
  try {
    const me = await api.getMe()
    if (me && me.weight_kg) {
      userWeight.value = Number(me.weight_kg)
      form.weight_kg = Number(me.weight_kg)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const onExerciseChange = (e) => {
  const index = e.detail.value
  if (Array.isArray(exercises.value) && exercises.value[index]) {
    exerciseIndex.value = index
    form.exercise_id = exercises.value[index].id
    // 切换运动时重置手动输入标记，重新用系统估算
    manualCalories.value = false
    form.calories_burned = null
  }
}

const onDateChange = (e) => {
  logDate.value = e.detail.value
}

// 当估算值变化且用户未手动输入时，自动填充表单消耗热量
watch(
  estimatedCalories,
  (val) => {
    // 未手动输入或当前值为 0 时，用系统估算值覆盖
    if (!manualCalories.value || form.calories_burned === null || form.calories_burned === '' || Number.isNaN(form.calories_burned) || form.calories_burned === 0) {
      form.calories_burned = val
    }
  },
  { immediate: true }
)

const handleSubmit = async () => {
  if (!form.exercise_id) {
    uni.showToast({
      title: '请选择运动项目',
      icon: 'none'
    })
    return
  }
  submitting.value = true
  try {
    const calories = form.calories_burned ?? estimatedCalories.value
    const weight = form.weight_kg || userWeight.value || 0
    const logData = {
      exercise_id: form.exercise_id,
      duration_minutes: form.duration_minutes,
      calories_burned: calories,
      log_date: logDate.value,
      weight_kg: weight
    }
    await api.logExercise(logData)
    uni.showToast({
      title: '运动记录已同步',
      icon: 'success'
    })
    // 重置
    form.exercise_id = null
    form.duration_minutes = 30
    form.weight_kg = 60
    form.calories_burned = null
    exerciseIndex.value = 0
    logDate.value = new Date().toISOString().split('T')[0]
    notes.value = ''
  } catch (error) {
    uni.showToast({
      title: '记录失败，请检查网络',
      icon: 'none'
    })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  getExercises()
  getUserProfile()
})
</script>

<style scoped lang="scss">
/* 基础容器优化 */
.app-safe-area {
  background-color: #f8fafc;
  min-height: 100vh;
  box-sizing: border-box;
}

.app-container {
  --header-height: calc(env(safe-area-inset-top) + 160rpx);
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* 头部导航对齐 */
.app-header {
  position: fixed;
  left: 0;
  right: 0;
  top: 30rpx;
  padding: 32rpx 40rpx;
  padding-top: calc(env(safe-area-inset-top) + 32rpx);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  z-index: 200;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.back-icon-btn {
  background: none;
  border: none;
  padding: 0;
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  &::after { border: none; }
}

.back-icon {
  font-size: 64rpx;
  color: #1e293b;
  font-weight: 300;
}

.app-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1e293b;
}

/* 滚动区域布局优化 */
.app-content-scroll {
  flex: 1;
  width: 100%;
  padding-top: var(--header-height);
}

.scroll-inner {
  padding: 0 40rpx; /* 侧边距统一为 40rpx，与头部对齐 */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  /* 关键：给底部足够留白，避免按钮被安全区/底部区域遮挡导致点不到 */
  padding-bottom: calc(200rpx + env(safe-area-inset-bottom));
}

/* 输入表单卡片 */
.log-card {
  background: #ffffff;
  border-radius: 48rpx;
  padding: 40rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.04);
  box-sizing: border-box;
}

.form-item {
  margin-bottom: 40rpx;
  &.half {
    flex: 1;
  }
}

.form-row {
  display: flex;
  gap: 32rpx; /* 左右输入框间距 */
}

.label {
  font-size: 28rpx;
  font-weight: 700;
  color: #475569;
  margin-bottom: 20rpx;
  display: block;
  margin-left: 4rpx;
}

/* 精简后的输入控件：去边框，浅色底 */
.picker-display, .input-wrapper, .textarea-field {
  background: #f8fafc; /* 使用极浅色作为底色 */
  border: 1rpx solid #f1f5f9;
  border-radius: 28rpx;
  padding: 0 32rpx;
  min-height: 104rpx;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.picker-display {
  justify-content: space-between;
}

.picker-text {
  font-size: 30rpx;
  color: #1e293b;
  font-weight: 600;
}

.arrow-down {
  font-size: 20rpx;
  color: #cbd5e1;
}

.input-field {
  width: 100%;
  height: 100%;
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
}

.textarea-field {
  width: 100%;
  height: 180rpx;
  padding: 24rpx 32rpx;
  font-size: 28rpx;
  line-height: 1.6;
}

/* 保存按钮 */
.btn-primary-mobile {
  width: 100%;
  height: 112rpx;
  background: #838B8B;
  color: white;
  border-radius: 32rpx;
  font-size: 32rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16rpx 32rpx rgba(131, 139, 139, 0.25);
  border: none;
  margin-top: 10rpx;
  &::after { border: none; }
}

.btn-hover {
  opacity: 0.85;
  transform: scale(0.98);
}

/* 底部提示卡片 */
.tips-section {
  padding: 40rpx 0;
}

.tip-card {
  display: flex;
  gap: 20rpx;
  background: rgba(131, 139, 139, 0.05);
  padding: 32rpx;
  border-radius: 32rpx;
  align-items: center;
}

.tip-icon { font-size: 32rpx; }
.tip-text {
  font-size: 24rpx;
  color: #94a3b8;
  line-height: 1.5;
  flex: 1;
}

.safe-bottom-pad {
  height: calc(200rpx + env(safe-area-inset-bottom)); /* 保证能滚到最底并点到按钮 */
}
</style>