<template>
  <view class="app-safe-area">
    <view class="app-container">
      <view class="app-header">
        <view class="header-left">
          <text class="app-title">AI 配餐建议</text>
        </view>

        <view class="refresh-action" @tap="handleGenerate" v-if="!isGenerating">
          <text class="refresh-text">刷新</text>
        </view>
      </view>

      <scroll-view v-if="!loading" class="app-content-scroll" scroll-y>
        <view class="scroll-inner">
          <view class="dashboard-section">
            <view class="dashboard-card">
              <view class="stat-grid">
                <view class="stat-box">
                  <text class="stat-label">健身目标</text>
                  <text class="stat-val-text">{{ translateGoal(user?.goal) }}</text>
                </view>
                
                <view class="stat-box main-stat">
                  <text class="stat-label">今日建议</text>
                  <view class="stat-main">
                    <text class="stat-val">{{ dailyRecommendedKcal }}</text>
                    <text class="stat-unit">kcal</text>
                  </view>
                </view>

                <view class="stat-box">
                  <text class="stat-label">当前 BMI</text>
                  <text class="stat-val-text">{{ bmiValue }}</text>
                </view>
              </view>
            </view>
          </view>

          <view class="action-section">
            <button
              class="app-btn-primary"
              :disabled="isGenerating"
              @tap="handleGenerate"
              hover-class="btn-hover"
            >
              <view v-if="isGenerating" class="loading-dots">
                <text>精算中...</text>
              </view>
              <text v-else>生成今日建议</text>
            </button>
            <text class="disclaimer">* 配餐逻辑基于您的代谢数据计算，仅供参考</text>
          </view>

          <view v-if="menuResult" class="menu-list">
            <view
              v-for="(meal, index) in menuResult"
              :key="index"
              class="meal-card-mobile"
            >
              <view class="meal-card-header">
                <view class="meal-title-group">
                  <view class="meal-icon-bg">{{ meal.icon }}</view>
                  <text class="meal-type">{{ meal.type }}</text>
                </view>
                <view class="meal-energy-badge">
                  <text>{{ meal.totalKcal }} kcal</text>
                </view>
              </view>

              <view class="meal-body">
                <view
                  v-for="(food, fIdx) in meal.foods"
                  :key="fIdx"
                  class="food-row"
                >
                  <text class="food-name">{{ food.name }}</text>
                  <text class="food-weight">{{ food.weight }}g</text>
                </view>
              </view>

              <view class="ai-instruction">
                <view class="instr-header">
                  <text class="sparkle">✨</text>
                  <text>AI 建议</text>
                </view>
                <text class="instr-body">{{ meal.tip }}</text>
              </view>
            </view>
          </view>

          <view v-else-if="!isGenerating" class="empty-state">
            <view class="empty-icon">🍲</view>
            <text class="empty-text">点击上方按钮获取配餐建议</text>
          </view>
          
          <view class="safe-bottom-holder"></view>
        </view>
      </scroll-view>

      <view v-if="loading" class="loading-full">
        <view class="spinner"></view>
        <text>正在分析您的营养数据...</text>
      </view>
    </view>
  </view>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

const user = ref(null)
const dailySummary = ref(null)
const loading = ref(true)
const isGenerating = ref(false)
const menuResult = ref(null)

const dailyRecommendedKcal = computed(() => {
  return dailySummary.value?.recommended_daily_kcal?.toFixed(0) || '2000'
})

const bmiValue = computed(() => {
  if (!user.value?.height_cm || !user.value?.weight_kg) return '--'
  const h = user.value.height_cm / 100
  return (user.value.weight_kg / (h * h)).toFixed(1)
})

const translateGoal = (g) => ({ 
  maintain: '保持体重', 
  lose_weight: '减脂减重', 
  gain_muscle: '增肌训练' 
}[g] || '未设置')

const initData = async () => {
  loading.value = true
  try {
    const today = new Date().toISOString().split('T')[0]
    const [userRes, summaryRes] = await Promise.all([
      api.getMe(),
      api.getDailySummary(today)
    ])
    if (userRes) user.value = userRes
    if (summaryRes) dailySummary.value = summaryRes
  } catch (error) {
    uni.showToast({
      title: '加载数据失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  isGenerating.value = true
  try {
    const res = await api.getMenuSuggestions()
    const meals = Array.isArray(res?.meals) ? res.meals : []
    const iconMap = { '早餐': '🌅', '午餐': '☀️', '晚餐': '🌙' }

    menuResult.value = meals.map(meal => ({
      type: meal.name || '餐次',
      icon: iconMap[meal.name] || '🍽️',
      totalKcal: Math.round(meal.meal_kcal || 0),
      foods: (meal.items || []).map(item => ({
        name: item.name || `食物 #${item.id}`,
        weight: item.grams || 0
      })),
      tip: `本餐热量约 ${Math.round(meal.meal_kcal || 0)} kcal`
    }))

    uni.showToast({
      title: '建议已更新',
      icon: 'success'
    })
  } catch (error) {
    console.error('生成菜单失败', error)
    menuResult.value = null
    uni.showToast({
      title: error?.data?.detail || '生成失败，请稍后重试',
      icon: 'none'
    })
  } finally {
    isGenerating.value = false
  }
}

onMounted(initData)
</script>

<style scoped lang="scss">
.app-safe-area {
  background-color: #f8fafc;
  min-height: 100vh;
}

.app-container {
  --header-height: calc(env(safe-area-inset-top) + 150rpx);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
}


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
  gap: 12rpx;
}

.back-icon-btn {
  background: none;
  padding: 0;
  margin: 0;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  &::after { border: none; }
}

.back-icon {
  font-size: 60rpx;
  color: #1e293b;
  font-weight: 300;
}

.app-title {
  font-size: 40rpx;
  font-weight: 900;
  color: #1e293b;
  letter-spacing: -1rpx;
}

.refresh-text {
  font-size: 28rpx;
  color: #838B8B;
  font-weight: 600;
}

/* 布局对齐 */
.app-content-scroll {
  flex: 1;
  padding-top: var(--header-height);
}

.scroll-inner {
  padding: 0 40rpx;
}

/* Dashboard 卡片美化 */
.dashboard-section {
  padding: 20rpx 0 40rpx;
}

.dashboard-card {
  background: #ffffff;
  border-radius: 48rpx;
  padding: 48rpx 32rpx;
  box-shadow: 0 12rpx 40rpx rgba(0,0,0,0.03);
}

.stat-grid {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-stat {
  border-left: 2rpx solid #f1f5f9;
  border-right: 2rpx solid #f1f5f9;
  padding: 0 20rpx;
}

.stat-label {
  font-size: 20rpx;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2rpx;
  margin-bottom: 12rpx;
}

.stat-val-text {
  font-size: 30rpx;
  font-weight: 800;
  color: #475569;
}

.stat-main {
  display: flex;
  align-items: baseline;
}

.stat-val {
  font-size: 44rpx;
  font-weight: 900;
  color: #1e293b;
}

.stat-unit {
  font-size: 22rpx;
  color: #94a3b8;
  margin-left: 4rpx;
  font-weight: 600;
}

/* 操作按钮优化 */
.action-section {
  padding-bottom: 48rpx;
}

.app-btn-primary {
  width: 100%;
  height: 112rpx;
  background: #838B8B;
  color: white;
  border-radius: 32rpx;
  font-weight: 800;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16rpx 32rpx rgba(131, 139, 139, 0.25);
  transition: all 0.2s;
  border: none;
  &::after { border: none; }
}

.disclaimer {
  font-size: 22rpx;
  color: #cbd5e1;
  margin-top: 24rpx;
  text-align: center;
  display: block;
}

/* 建议列表卡片美化 */
.meal-card-mobile {
  background: #ffffff;
  border-radius: 48rpx;
  padding: 40rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.02);
  border-top: 2rpx solid #f8fafc;
}

.meal-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.meal-title-group {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.meal-icon-bg {
  width: 80rpx;
  height: 80rpx;
  background: #f1f5f9;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
}

.meal-type {
  font-size: 36rpx;
  font-weight: 900;
  color: #1e293b;
}

.meal-energy-badge {
  background: rgba(131, 139, 139, 0.1);
  padding: 8rpx 20rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #838B8B;
}

.meal-body {
  margin-bottom: 32rpx;
}

.food-row {
  display: flex;
  justify-content: space-between;
  padding: 28rpx 0;
  border-bottom: 1rpx solid #f1f5f9;
  &:last-child { border-bottom: none; }
}

.food-name {
  font-size: 30rpx;
  color: #334155;
  font-weight: 600;
}

.food-weight {
  font-size: 28rpx;
  color: #94a3b8;
  font-weight: 500;
}

/* AI 建议区域优化 */
.ai-instruction {
  background: #f8fafc;
  padding: 32rpx;
  border-radius: 36rpx;
  border: 1rpx solid #f1f5f9;
}

.instr-header {
  font-size: 24rpx;
  font-weight: 900;
  color: #838B8B;
  margin-bottom: 12rpx;
  display: flex;
  align-items: center;
}

.sparkle { margin-right: 12rpx; font-size: 28rpx; }

.instr-body {
  font-size: 26rpx;
  color: #64748b;
  line-height: 1.6;
}

/* 状态展示 */
.empty-state {
  text-align: center;
  padding: 120rpx 0;
}

.empty-icon { font-size: 80rpx; margin-bottom: 20rpx; }
.empty-text { color: #cbd5e1; font-size: 28rpx; font-weight: 500; }

.loading-full {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 200rpx;
  color: #94a3b8;
  font-size: 28rpx;
}

.btn-hover {
  transform: scale(0.97);
  opacity: 0.9;
}

.safe-bottom-holder {
  height: 60rpx;
}
</style>