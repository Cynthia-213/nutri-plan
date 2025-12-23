<template>
  <div class="menu-suggestions-container">
    <div class="header-section">
      <div class="title-wrapper">
        <h1 class="page-title">AI 智能菜单建议</h1>
        <el-tag size="small" effect="plain" class="disclaimer-tag">数据仅供参考</el-tag>
      </div>
      <p class="page-subtitle">根据您的健康档案与今日代谢状态，定制科学配餐方案。</p>
    </div>

    <el-card class="dashboard-card" shadow="never" v-loading="loading">
      <div class="dashboard-flex">
        <div class="stat-group">
          <div class="stat-item">
            <span class="stat-label">健身目标</span>
            <span class="stat-value-text">{{ translateGoal(user?.goal) }}</span>
          </div>
          <el-divider direction="vertical" />
          <div class="stat-item">
            <span class="stat-label">今日建议摄入</span>
            <div class="stat-main">
              <span class="stat-value">{{ dailyRecommendedKcal }}</span>
              <span class="stat-unit">kcal</span>
            </div>
          </div>
          <el-divider direction="vertical" />
          <div class="stat-item">
            <span class="stat-label">当前 BMI</span>
            <span class="stat-value">{{ bmiValue }}</span>
          </div>
        </div>

        <div class="control-group">
          <el-button 
            class="btn-ai-generate" 
            :loading="isGenerating"
            @click="handleGenerate"
          >
            <el-icon v-if="!isGenerating"><MagicStick /></el-icon>
            {{ isGenerating ? '正在生成...' : '获取建议菜单' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <transition name="el-zoom-in-top">
      <div v-if="menuResult" class="result-layout">
        <el-row :gutter="24">
          <el-col :span="8" v-for="(meal, index) in menuResult" :key="index">
            <el-card class="meal-card" shadow="hover">
              <div class="meal-header">
                <span class="meal-type">{{ meal.type }}</span>
                <span class="meal-energy">{{ meal.totalKcal }} kcal</span>
              </div>
              <div class="meal-content">
                <div v-for="(food, fIdx) in meal.foods" :key="fIdx" class="food-line">
                  <span class="food-name">{{ food.name }}</span>
                  <span class="food-weight">{{ food.weight }}g</span>
                </div>
              </div>
              <div class="ai-comment-box">
                <div class="comment-header">✨ AI 营养指导</div>
                <p class="comment-body">{{ meal.tip }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div v-else-if="!isGenerating" class="empty-placeholder">
        <el-empty description="暂无方案，点击上方按钮开启智能排餐" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const user = ref(null)
const dailySummary = ref(null)
const loading = ref(true)
const isGenerating = ref(false)
const preference = ref('balanced')
const menuResult = ref(null)

const initData = async () => {
  loading.value = true
  try {
    const today = new Date().toISOString().split('T')[0]
    const [userRes, summaryRes] = await Promise.all([
      api.getMe(),
      api.getDailySummary(today)
    ])
    user.value = userRes.data
    dailySummary.value = summaryRes.data
  } catch (error) {
    ElMessage.error('无法加载健康数据')
  } finally {
    loading.value = false
  }
}

// 建议值：优先使用 DailySummary 的计算结果
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
  lose_weight: '减脂/减重', 
  gain_muscle: '增肌训练' 
}[g] || '未设置')

// 生成模拟数据
const handleGenerate = () => {
  isGenerating.value = true
  const baseKcal = parseInt(dailyRecommendedKcal.value)
  
  setTimeout(() => {
    menuResult.value = [
      {
        type: '早餐 🌅',
        totalKcal: Math.round(baseKcal * 0.25),
        foods: [{ name: '黑麦面包', weight: 80 }, { name: '无糖酸奶', weight: 150 }],
        tip: '低 GI 开启一天活力，避免早晨血糖大幅波动。'
      },
      {
        type: '午餐 ☀️',
        totalKcal: Math.round(baseKcal * 0.4),
        foods: [{ name: '龙利鱼排', weight: 150 }, { name: '五谷饭', weight: 120 }, { name: '西兰花', weight: 100 }],
        tip: '优质蛋白与复合碳水的完美配比，为下午工作续航。'
      },
      {
        type: '晚餐 🌙',
        totalKcal: Math.round(baseKcal * 0.35),
        foods: [{ name: '鸡丝沙拉', weight: 200 }, { name: '清炖豆腐', weight: 100 }],
        tip: '清淡易消化，睡前减少肠胃负担，更有利于代谢。'
      }
    ]
    isGenerating.value = false
    ElMessage.success('已为您生成专属菜单')
  }, 1200)
}

onMounted(initData)
</script>

<style scoped>
.menu-suggestions-container {
  max-width: 1100px;
  margin: 40px auto;
  padding: 0 20px;
}

/* 头部 */
.header-section { margin-bottom: 30px; }
.title-wrapper { display: flex; align-items: center; gap: 15px; }
.page-title { font-size: 28px; font-weight: 700; color: #1e293b; margin: 0; }
.disclaimer-tag { border-color: #e2e8f0 !important; color: #94a3b8 !important; }
.page-subtitle { color: #838B8B; font-size: 14px; margin-top: 10px; }

/* 看板卡片：参考 UserMe.vue 风格 */
.dashboard-card {
  border-radius: 20px;
  border: 1px solid #f1f5f9;
  margin-bottom: 40px;
}
.dashboard-flex { display: flex; justify-content: space-between; align-items: center; padding: 10px; }

.stat-group { display: flex; align-items: center; gap: 30px; }
.stat-item { display: flex; flex-direction: column; gap: 6px; }
.stat-label { font-size: 11px; color: #94a3b8; text-transform: uppercase; }
.stat-value { font-size: 24px; font-weight: 800; color: #2d3436; }
.stat-unit { font-size: 12px; color: #94a3b8; margin-left: 2px; }
.stat-value-text { font-size: 16px; font-weight: 600; color: #838B8B; }

/* 按钮与下拉框：参考 DailySummary.vue 的高级灰 */
.theme-select { width: 140px; }
:deep(.el-input__wrapper) { border-radius: 12px; height: 45px; }

.btn-ai-generate {
  background-color: #838B8B !important;
  border: none !important;
  color: white !important;
  height: 48px;
  padding: 0 25px;
  border-radius: 12px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(131, 139, 139, 0.3);
}

/* 建议结果卡片：参考 DailySummary.vue AI 分析样式 */
.meal-card {
  border-radius: 20px;
  border: 1px solid #f1f5f9;
  border-top: 5px solid #838B8B; /* 侧边强调色 */
}
.meal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.meal-type { font-weight: 700; color: #334155; font-size: 16px; }
.meal-energy { color: #838B8B; font-weight: 700; font-size: 13px; }

.food-line { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #f1f5f9; font-size: 14px; color: #475569; }
.food-weight { color: #94a3b8; }

.ai-comment-box { margin-top: 20px; background: #f8fafc; padding: 15px; border-radius: 14px; }
.comment-header { font-size: 11px; font-weight: 700; color: #838B8B; margin-bottom: 6px; }
.comment-body { font-size: 12px; color: #64748b; line-height: 1.6; margin: 0; }

.empty-placeholder { padding: 60px 0; }
</style>