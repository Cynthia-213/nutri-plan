<template>
  <div class="summary-container">
    <div class="header-section">
      <h2 class="page-title">每日总结</h2>
      <el-date-picker
        v-model="selectedDate"
        type="date"
        placeholder="选择日期"
        value-format="YYYY-MM-DD"
        @change="getSummary"
        :clearable="false"
        class="custom-date-picker"
      />
    </div>

    <div v-if="summary" class="content-layout">
      <div class="section-label">数据结算：{{ selectedDate }}</div>
      
      <el-row :gutter="24" class="overview-grid">
        <el-col :span="8">
          <el-card shadow="never" class="stat-card">
            <template #header><div class="card-header">能量平衡概览</div></template>
            <div class="energy-main">
              <div class="main-val">{{ summary.net_calories.toFixed(0) }}</div>
              <div class="main-unit">净摄入 (kcal)</div>
            </div>
            
            <div class="metabolism-info">
              <div class="met-item">
                <span class="met-label">基础代谢 BMR</span>
                <span class="met-val">{{ summary.bmr }}</span>
              </div>
              <div class="met-item">
                <span class="met-label">日总消耗 TDEE</span>
                <span class="met-val">{{ summary.tdee }}</span>
              </div>
            </div>

            <div class="energy-footer">
              <div class="footer-item">
                <span class="f-label">饮食摄入</span>
                <span class="f-val intake">{{ summary.total_intake_kcal.toFixed(0) }}</span>
              </div>
              <div class="footer-item">
                <span class="f-label">运动消耗</span>
                <span class="f-val burn">{{ summary.total_burned_kcal.toFixed(0) }}</span>
              </div>
            </div>
            <div class="disclaimer">＊算法推算，仅供参考</div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="never" class="stat-card">
            <template #header><div class="card-header">宏量营养素 (g)</div></template>
            <div class="nutrient-wrapper">
              <div class="prog-item">
                <div class="prog-info">
                  <span class="p-label">蛋白质</span>
                  <span class="p-data"><b>{{ summary.total_protein_g.toFixed(1) }}</b> / {{ summary.recommended_protein_g.toFixed(0) }}</span>
                </div>
                <el-progress :percentage="calcPercent(summary.total_protein_g, summary.recommended_protein_g)" color="#838B8B" :stroke-width="8" :show-text="false" />
              </div>
              <div class="prog-item">
                <div class="prog-info">
                  <span class="p-label">脂肪</span>
                  <span class="p-data"><b>{{ summary.total_fat_g.toFixed(1) }}</b> / {{ summary.recommended_fat_g.toFixed(0) }}</span>
                </div>
                <el-progress :percentage="calcPercent(summary.total_fat_g, summary.recommended_fat_g)" color="#a5a5a5" :stroke-width="8" :show-text="false" />
              </div>
              <div class="prog-item">
                <div class="prog-info">
                  <span class="p-label">碳水</span>
                  <span class="p-data"><b>{{ summary.total_carbs_g.toFixed(1) }}</b> / {{ summary.recommended_carbs_g.toFixed(0) }}</span>
                </div>
                <el-progress :percentage="calcPercent(summary.total_carbs_g, summary.recommended_carbs_g)" color="#d1d1d1" :stroke-width="8" :show-text="false" />
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="never" class="stat-card">
            <template #header><div class="card-header">系统推荐目标</div></template>
            <div class="recommend-list">
              <div class="rec-item"><span>每日热量建议</span><el-tag size="small" class="custom-tag">{{ summary.recommended_daily_kcal.toFixed(0) }} kcal</el-tag></div>
              <div class="rec-item"><span>建议蛋白质</span><span>{{ summary.recommended_protein_g.toFixed(0) }} g</span></div>
              <div class="rec-item"><span>建议脂肪</span><span>{{ summary.recommended_fat_g.toFixed(0) }} g</span></div>
              <div class="rec-item"><span>建议碳水</span><span>{{ summary.recommended_carbs_g.toFixed(0) }} g</span></div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <div class="ai-summary-box">
        <el-card 
          shadow="never" 
          class="ai-card" 
          v-loading="aiLoading"
          element-loading-text="AI 正在深度分析数据..."
          element-loading-background="rgba(255, 255, 255, 0.7)"
        >
          <div class="ai-content">
            <div class="ai-header-row">
              <div class="ai-header-left">
                <span class="ai-spark">✨</span>
                <span class="ai-title">AI 健康分析报告</span>
              </div>
              <el-button 
                v-if="summary.ai_summary" 
                link 
                class="re-gen-btn" 
                @click="generateAIAnalysis"
              >
                重新分析
              </el-button>
            </div>

            <div class="ai-body">
              <div v-if="summary.ai_summary" class="ai-text-container">
                <p class="ai-text">{{ summary.ai_summary }}</p>
              </div>
              <div v-else class="ai-empty-prompt">
                <p class="prompt-msg">系统已整合今日 {{ summary.food_log.length + summary.exercise_log.length }} 项记录，点击按钮获取深度评估与建议</p>
                <el-button class="btn-primary-gray" @click="generateAIAnalysis">
                  生成健康建议报告
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <el-row :gutter="24" class="detail-section">
        <el-col :span="12">
          <h3 class="table-title">🍎 食物摄入明细</h3>
          <el-table :data="summary.food_log" stripe class="styled-table">
            <el-table-column prop="food.description_zh" label="名称" min-width="120" />
            <el-table-column prop="serving_grams" label="重量(g)" width="90" align="center" />
            <el-table-column prop="total_calories" label="热量" width="90" align="right" />
          </el-table>
        </el-col>
        <el-col :span="12">
          <h3 class="table-title">🏃 运动消耗明细</h3>
          <el-table :data="summary.exercise_log" stripe class="styled-table">
            <el-table-column prop="exercise_name" label="项" />
            <el-table-column prop="duration_minutes" label="时长(min)" width="90" align="center" />
            <el-table-column prop="calories_burned" label="消耗" width="90" align="right" />
          </el-table>
        </el-col>
      </el-row>
    </div>

    <el-divider class="main-divider">周期趋势分析</el-divider>

    <div class="trend-section">
      <el-card shadow="never" class="chart-card">
        <div class="chart-filter">
          <div class="filter-left">
            <el-radio-group v-model="energySummaryPeriod" @change="getTrendData" size="small">
              <el-radio-button label="daily">日趋势</el-radio-button>
              <el-radio-button label="monthly">月趋势</el-radio-button>
            </el-radio-group>
            <el-radio-group v-model="energySummaryType" @change="getTrendData" size="small" class="type-select">
              <el-radio-button label="intake">摄入</el-radio-button>
              <el-radio-button label="expenditure">消耗</el-radio-button>
            </el-radio-group>
          </div>
          <span class="filter-hint">{{ dateRangeText }}</span>
        </div>
        <div ref="chartRef" class="chart-canvas"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import api from '../services/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const selectedDate = ref(new Date().toISOString().split('T')[0])
const summary = ref(null)
const chartRef = ref(null)
let myChart = null
const energySummaryPeriod = ref('daily')
const energySummaryType = ref('intake')
const energyTrendData = ref([])
const aiLoading = ref(false) // 新增：AI分析加载状态

const dateRangeText = computed(() => 
  energySummaryPeriod.value === 'daily' ? '最近 30 天数据' : '最近 12 个月数据'
)

const calcPercent = (cur, tar) => tar ? Math.min(Math.round((cur / tar) * 100), 100) : 0

const getSummary = async () => {
  try {
    // 修改：默认不强制生成 AI 分析，加快初始加载速度
    const response = await api.getDailySummary(selectedDate.value, false)
    summary.value = response.data
  } catch (error) {
    ElMessage.error("获取数据失败")
  }
}

// 新增：手动触发 AI 生成逻辑
const generateAIAnalysis = async () => {
  if (aiLoading.value) return
  aiLoading.value = true
  try {
    // 调用接口并传递 true 以强制生成 AI 重写内容
    const response = await api.getDailySummary(selectedDate.value, true)
    summary.value.ai_summary = response.data.ai_summary
    ElMessage.success("AI 分析已生成")
  } catch (error) {
    ElMessage.error("分析生成失败，请稍后重试")
  } finally {
    aiLoading.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value) return
  if (!myChart) myChart = echarts.init(chartRef.value)
  const option = {
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderRadius: 8, boxShadow: '0 2px 12px rgba(0,0,0,0.1)' },
    grid: { left: '4%', right: '4%', bottom: '5%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: energyTrendData.value.map(d => d.period),
      axisLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: [{
      data: energyTrendData.value.map(d => d.total_calories),
      type: 'line',
      smooth: true,
      showSymbol: false,
      itemStyle: { color: '#838B8B' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(131, 139, 139, 0.15)' },
          { offset: 1, color: 'rgba(131, 139, 139, 0)' }
        ])
      }
    }]
  }
  myChart.setOption(option)
}

const getTrendData = async () => {
  const end = new Date()
  const start = new Date()
  if (energySummaryPeriod.value === 'daily') start.setDate(end.getDate() - 30)
  else start.setFullYear(end.getFullYear() - 1)

  try {
    const response = await api.getEnergySummary({
      period_type: energySummaryPeriod.value,
      energy_type: energySummaryType.value,
      start_date: start.toISOString().split('T')[0],
      end_date: end.toISOString().split('T')[0]
    })
    energyTrendData.value = response.data.data
    nextTick(() => renderChart())
  } catch (e) { console.error(e) }
}

onMounted(() => { getSummary(); getTrendData(); window.addEventListener('resize', () => myChart?.resize()); })
</script>

<style scoped>
.summary-container { max-width: 1160px; margin: 40px auto; padding: 0 30px; font-family: "PingFang SC", sans-serif; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.page-title { font-size: 26px; font-weight: 600; color: #1e293b; margin: 0; }
.section-label { font-size: 13px; color: #64748b; margin-bottom: 20px; letter-spacing: 0.5px; }

/* 卡片升级 */
.stat-card { border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important; padding: 5px; }
.card-header { font-size: 14px; color: #64748b; font-weight: 500; }

.energy-main { text-align: center; padding: 25px 0 15px; }
.main-val { font-size: 42px; font-weight: 700; color: #0f172a; line-height: 1; }
.main-unit { font-size: 12px; color: #94a3b8; margin-top: 8px; font-weight: 500; }

.metabolism-info { display: flex; background: #f8fafc; border-radius: 14px; margin: 20px 0; padding: 12px 0; }
.met-item { flex: 1; text-align: center; border-right: 1px solid #e2e8f0; }
.met-item:last-child { border-right: none; }
.met-label { font-size: 10px; color: #94a3b8; display: block; margin-bottom: 4px; }
.met-val { font-size: 15px; font-weight: 600; color: #475569; }

.energy-footer { display: flex; justify-content: space-between; padding: 10px 10px 0; }
.footer-item { display: flex; flex-direction: column; }
.f-label { font-size: 11px; color: #94a3b8; }
.f-val { font-size: 16px; font-weight: 700; margin-top: 2px; }
.intake { color: #475569; }
.burn { color: #838B8B; }

.nutrient-wrapper { padding: 15px 5px; }
.prog-item { margin-bottom: 22px; }
.prog-info { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 12px; }
.p-label { font-weight: 600; color: #475569; }
.p-data { color: #94a3b8; }
.p-data b { color: #1e293b; }

.recommend-list { padding: 10px 0; }
.rec-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f8fafc; font-size: 13px; color: #475569; }
.custom-tag { background: #f1f5f9 !important; color: #838B8B !important; border: none !important; font-weight: 600; }

/* AI 建议区域修改 */
.ai-summary-box { margin: 30px 0; }
.ai-card { border-radius: 18px; background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%); border-left: 5px solid #838B8B !important; position: relative; }
.ai-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.ai-header-left { display: flex; align-items: center; }
.ai-spark { font-size: 18px; margin-right: 8px; }
.ai-title { font-size: 15px; font-weight: 700; color: #838B8B; }
.re-gen-btn { color: #838B8B !important; font-size: 12px; font-weight: 500; }

.ai-empty-prompt { text-align: center; padding: 20px 0; }
.prompt-msg { font-size: 13px; color: #94a3b8; margin-bottom: 16px; }
.btn-primary-gray { 
  background-color: #838B8B !important; 
  color: white !important; 
  border: none !important; 
  border-radius: 10px;
  padding: 10px 20px;
}
.btn-primary-gray:hover { opacity: 0.9; box-shadow: 0 4px 12px rgba(131, 139, 139, 0.2); }

.ai-text { font-size: 14px; color: #334155; line-height: 1.8; margin: 0; white-space: pre-line; }

/* 图表区域 */
.chart-card { border-radius: 24px; border: 1px solid #f1f5f9; padding: 20px; }
.chart-filter { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding: 0 10px; }
.type-select { margin-left: 20px; }
.chart-canvas { width: 100%; height: 400px; }
.filter-hint { font-size: 13px; color: #94a3b8; font-weight: 500; }

:deep(.el-radio-button) {
  --el-radio-button-checked-bg-color: #838B8B; 
  --el-radio-button-checked-text-color: #ffffff; 
  --el-radio-button-checked-border-color: #838B8B; 
  margin-right: 8px;
}
:deep(.el-radio-button__inner) {
  border: none !important;
  background-color: #f4f4f5 !important;
  color: #909399 !important;
  border-radius: 10px !important;
  padding: 8px 16px;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
  box-shadow: none !important;
}
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #838B8B !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(131, 139, 139, 0.3) !important;
}
:deep(.el-table) { --el-table-header-bg-color: #f8fafc; color: #475569; border-radius: 12px; }

.table-title { font-size: 16px; font-weight: 700; color: #1e293b; margin: 20px 0 15px; }
.disclaimer { font-size: 10px; color: #cbd5e1; text-align: center; margin-top: 15px; font-style: italic; }
.main-divider { margin: 60px 0 40px; }
</style>