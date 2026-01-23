<template>
  <view class="app-safe-area">
    <view class="summary-app-container">
      <view class="app-header">
        <view class="header-left">
          <text class="app-title">每日总结</text>
        </view>

        <picker
          mode="date"
          :value="selectedDate"
          @change="onDateChange"
          class="date-picker"
        >
          <view class="date-display">
            {{ selectedDate || '选择日期' }}
          </view>
        </picker>
      </view>

      <scroll-view v-if="summary" class="app-scroll-content" scroll-y>
        <!-- hero -->
        <view class="hero-section">
          <view class="energy-hero-card">
            <text class="hero-label">今日净摄入 (kcal)</text>
            <text class="hero-val">{{ summary.net_calories.toFixed(0) }}</text>

            <view class="hero-stats-row">
              <view class="h-stat">
                <text class="h-label">饮食摄入</text>
                <text class="h-val intake">+{{ summary.total_intake_kcal.toFixed(0) }}</text>
              </view>
              <view class="h-divider"></view>
              <view class="h-stat">
                <text class="h-label">运动消耗</text>
                <text class="h-val burn">-{{ summary.total_exercise_burned.toFixed(0) }}</text>
              </view>
            </view>

            <view class="bmr-tdee-bar">
              <text>BMR: {{ summary.bmr }}</text>
              <text class="dot">·</text>
              <text>TDEE: {{ summary.tdee }}</text>
            </view>
          </view>
        </view>

        <!-- AI -->
        <view class="ai-section">
          <view class="ai-app-card" :class="{ 'is-loading': aiLoading }">
            <view v-if="aiLoading" class="ai-loading-state">
              <view class="ai-header-row">
                <text class="ai-spark-anim">✨</text>
                <text class="ai-title">AI 正在深度分析...</text>
              </view>
              <view class="custom-skeleton">
                <view class="sk-line short"></view>
                <view class="sk-line long"></view>
                <view class="sk-line medium"></view>
              </view>
            </view>

            <view v-else>
              <view class="ai-header-row">
                <view class="ai-header-left">
                  <text class="ai-spark">✨</text>
                  <text class="ai-title">AI 健康评估建议</text>
                </view>
                <text
                  v-if="summary.ai_summary"
                  class="re-gen-btn"
                  @tap="generateAIAnalysis"
                >
                  重新分析
                </text>
              </view>

              <view class="ai-body">
                <view v-if="summary.ai_summary" class="ai-text-box">
                  {{ summary.ai_summary }}
                </view>
                <view v-else class="ai-empty-state">
                  <text>整合 {{ (summary.food_log?.length || 0) + (summary.exercise_log?.length || 0) }} 项记录</text>
                  <button class="app-btn-primary" @tap="generateAIAnalysis">
                    生成智能报告
                  </button>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- nutrient -->
        <view class="nutrient-section">
          <text class="section-title">营养配比</text>
          <view class="nutrient-card">
            <view
              class="nut-row"
              v-for="n in [
                {name:'蛋白质', val:summary.total_protein_g, tar:summary.recommended_protein_g, color:'#838B8B'},
                {name:'脂肪', val:summary.total_fat_g, tar:summary.recommended_fat_g, color:'#A5A5A5'},
                {name:'碳水', val:summary.total_carbs_g, tar:summary.recommended_carbs_g, color:'#D1D1D1'}
              ]"
              :key="n.name"
            >
              <view class="nut-meta">
                <text class="n-name">{{ n.name }}</text>
                <text class="n-val"><text class="bold">{{ n.val.toFixed(1) }}</text> / {{ n.tar.toFixed(0) }}g</text>
              </view>
              <view class="progress-bar">
                <view
                  class="progress-inner"
                  :style="{
                    width: calcPercent(n.val, n.tar) + '%',
                    background: n.color
                  }"
                ></view>
              </view>
            </view>
          </view>
        </view>

        <!-- detail -->
        <view class="detail-section">
          <text class="section-title">食物明细</text>
          <view class="app-list">
            <view class="app-list-item" v-for="f in summary.food_log" :key="f.id">
              <view class="item-info">
                <text class="item-title">{{ f.food.description_zh || f.food.description_en }}</text>
                <text class="item-sub">{{ f.serving_grams }} 克</text>
              </view>
              <text class="item-value">{{ f.total_calories }} kcal</text>
            </view>
            <view v-if="!summary.food_log?.length" class="empty-list">今日暂无饮食记录</view>
          </view>
        </view>

        <!-- exercise detail -->
        <view class="detail-section">
          <text class="section-title">运动明细</text>
          <view class="app-list">
            <view class="app-list-item" v-for="e in summary.exercise_log" :key="e.exercise_name + e.duration_minutes">
              <view class="item-info">
                <text class="item-title">{{ e.exercise_name }}</text>
                <text class="item-sub">{{ e.duration_minutes }} 分钟</text>
              </view>
              <text class="item-value exercise">{{ e.calories_burned }} kcal</text>
            </view>
            <view v-if="!summary.exercise_log?.length" class="empty-list">今日暂无运动记录</view>
          </view>
        </view>

        <!-- trend -->
        <view class="trend-section">
          <text class="section-title">周期趋势</text>
          <view class="chart-app-card">
            <view class="chart-controls">
              <view class="segmented">
                <view
                  class="seg-btn"
                  :class="{ active: energySummaryPeriod === 'daily' }"
                  @tap="changePeriod('daily')"
                >日</view>
                <view
                  class="seg-btn"
                  :class="{ active: energySummaryPeriod === 'monthly' }"
                  @tap="changePeriod('monthly')"
                >月</view>
              </view>
              <view class="segmented">
                <view
                  class="seg-btn"
                  :class="{ active: energySummaryType === 'intake' }"
                  @tap="changeType('intake')"
                >摄入</view>
                <view
                  class="seg-btn"
                  :class="{ active: energySummaryType === 'expenditure' }"
                  @tap="changeType('expenditure')"
                >消耗</view>
              </view>
            </view>
            <view class="chart-scroll-container">
              <scroll-view 
                class="chart-scroll-view" 
                scroll-x="true" 
                :scroll-left="scrollLeft" 
                :scroll-with-animation="false"
                :enable-back-to-top="false"
              >
                <view class="canvas-container" :style="{ width: (chartTotalWidth || 750) + 'px', minWidth: '100%' }">
                  <canvas
                    canvas-id="trendChart"
                    id="trendChart"
                    class="trend-canvas"
                    :style="{ width: (chartTotalWidth || 750) + 'px', height: canvasHeight + 'px' }"
                  ></canvas>
                </view>
              </scroll-view>
              <view v-if="!energyTrendData.length" class="empty-trend">
                <text>暂无趋势数据</text>
              </view>
            </view>
          </view>
        </view>

        <!-- footer -->
        <view class="app-footer">＊数据仅供参考，请结合实际感受</view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import api from '@/services/api'

const selectedDate = ref(new Date().toISOString().split('T')[0])
const summary = ref(null)
const aiLoading = ref(false)
const energySummaryPeriod = ref('daily')
const energySummaryType = ref('intake')
const energyTrendData = ref([])
const canvasHeight = ref(480)
const chartTotalWidth = ref(0)
const scrollLeft = ref(0)
const pointSpacing = 30
const padding = { top: 60, right: 40, bottom: 60, left: 60 }
const bmrValue = ref(0) // BMR 基准值

const onDateChange = (e) => {
  selectedDate.value = e.detail.value
  getSummary()
  getTrendData()
}

const calcPercent = (cur, tar) => (tar ? Math.min(Math.round((cur / tar) * 100), 100) : 0)

const getSummary = async () => {
  try {
    const res = await api.getDailySummary(selectedDate.value)
    // request.js 直接返回 data，不是 res.data
    summary.value = res || null
  } catch (error) {
    console.error('获取每日总结失败:', error)
    summary.value = null
    uni.showToast({ title: '同步失败', icon: 'none' })
  }
}

const generateAIAnalysis = async () => {
  if (aiLoading.value) return
  aiLoading.value = true
  try {
    const res = await api.generateAISummary(selectedDate.value, {
      timeout: 120000
    })
    // request.js 直接返回 data，不是 res.data
    if (summary.value && res) {
      summary.value.ai_summary = res.ai_summary || null
    }
  } catch (error) {
    console.error('生成AI分析失败:', error)
    uni.showToast({ 
      title: error?.response?.data?.detail || '生成超时，请稍后再试', 
      icon: 'none',
      duration: 2000
    })
  } finally {
    aiLoading.value = false
  }
}

const getTrendData = async () => {
  try {
    const selectedDateObj = new Date(selectedDate.value)
    const year = selectedDateObj.getFullYear()
    const month = selectedDateObj.getMonth()
    let allPeriods = []
    let startDate, endDate

    if (energySummaryPeriod.value === 'daily') {
      // 1. 生成当月完整天数 (1号 到 最后一天)
      const daysInMonth = new Date(year, month + 1, 0).getDate()
      startDate = `${year}-${String(month + 1).padStart(2, '0')}-01`
      endDate = `${year}-${String(month + 1).padStart(2, '0')}-${daysInMonth}`
      
      for (let i = 1; i <= daysInMonth; i++) {
        allPeriods.push(`${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`)
      }
    } else {
      // 2. 生成当年完整月份 (1月 到 12月)
      startDate = `${year}-01-01`
      endDate = `${year}-12-31`
      for (let i = 1; i <= 12; i++) {
        allPeriods.push(`${year}-${String(i).padStart(2, '0')}`)
      }
    }

    const res = await api.getEnergySummary({
      period_type: energySummaryPeriod.value,
      energy_type: energySummaryType.value,
      start_date: startDate,
      end_date: endDate
    })

    // 保存 BMR 值用于绘制基准线
    bmrValue.value = res?.bmr || 0

    const apiData = res?.data || []
    const dataMap = new Map()
    apiData.forEach(item => {
      const key = energySummaryPeriod.value === 'monthly' ? item.period.substring(0, 7) : item.period
      dataMap.set(key, item.total_calories)
    })

    // 补全数据：无数据点设为 0
    energyTrendData.value = allPeriods.map(period => ({
      period,
      total_calories: dataMap.get(period) || 0
    }))

    // 动态计算 Canvas 总宽度
    chartTotalWidth.value = padding.left + padding.right + (allPeriods.length - 1) * pointSpacing
    
    await nextTick()
    // 给 DOM 渲染留出一点微量时间
    setTimeout(() => {
      drawChart()
      // 自动滚动到最后选中的日期附近
      focusCurrentDate()
    }, 100)
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}
const drawChart = () => {
  if (!energyTrendData.value.length) return
  
  const ctx = uni.createCanvasContext('trendChart')
  const width = chartTotalWidth.value
  const height = canvasHeight.value / (750 / uni.getSystemInfoSync().windowWidth) // 像素转换
  const chartHeight = height - padding.top - padding.bottom
  
  // 1. 清除画布并绘制背景
  ctx.clearRect(0, 0, width, height)
  ctx.setFillStyle('#ffffff')
  ctx.fillRect(0, 0, width, height)

  // 2. 计算最大值 - 必须包含 BMR 值，确保基准线始终可见
  const dataValues = energyTrendData.value.map(d => d.total_calories)
  const dataMax = dataValues.length > 0 ? Math.max(...dataValues) : 0
  
  // 计算最大值：数据最大值、BMR值、以及一个最小值（1000）中的最大值，再乘以1.2留出边距
  const maxValue = Math.max(
    dataMax,
    bmrValue.value || 0,
    1000 // 最小基准值，避免除0
  ) * 1.2

  const minValue = 0

  const valueRange = maxValue - minValue

  // 映射物理坐标 - 使用调整后的值范围
  const points = energyTrendData.value.map((item, i) => {
    const normalizedValue = ((item.total_calories - minValue) / valueRange)
    return {
      x: padding.left + i * pointSpacing,
      y: height - padding.bottom - normalizedValue * chartHeight,
      val: item.total_calories,
      label: energySummaryPeriod.value === 'daily' ? (i + 1).toString() : (i + 1)
    }
  })

  // 3. 绘制 X 轴基线与网格线
  ctx.setLineDash([4, 4])
  ctx.setStrokeStyle('#f1f5f9')
  const gridCount = 4
  for(let i=0; i<=gridCount; i++) {
    const gy = padding.top + (chartHeight / gridCount) * i
    ctx.beginPath()
    ctx.moveTo(padding.left, gy)
    ctx.lineTo(width - padding.right, gy)
    ctx.stroke()
  }
  
  // 4. 绘制 BMR 基准线
  if (bmrValue.value > 0) {
      const bmrNormalized = ((bmrValue.value - minValue) / valueRange)
      const bmrY = height - padding.bottom - bmrNormalized * chartHeight
      
      // --- 1. 绘制基准线 ---
      ctx.setLineDash([4, 4])          // 缩短虚线间距，看起来更精致
      ctx.setStrokeStyle('rgba(255, 107, 107, 0.4)') // 使用透明度，避免抢走数据主线的视觉重心
      ctx.setLineWidth(1)              // 细线更具高级感
      ctx.beginPath()
      ctx.moveTo(padding.left, bmrY)
      ctx.lineTo(width - padding.right, bmrY)
      ctx.stroke()
      ctx.setLineDash([])              // 立即重置虚线

      // --- 2. 绘制 BMR 标签背景（胶囊状徽标） ---
      const labelText = `BMR ${Math.round(bmrValue.value)}`
      ctx.setFontSize(10)
      const textWidth = ctx.measureText ? ctx.measureText(labelText).width : 50 // 兼容性处理
      const badgeW = textWidth + 12
      const badgeH = 18
      const badgeX = padding.left + 5
      const badgeY = bmrY - badgeH / 2 // 垂直居中于基准线

      // 绘制圆角矩形背景
      ctx.setFillStyle('rgba(255, 107, 107, 0.9)') // 稍微深一点的红色背景
      
      // 自定义圆角矩形逻辑
      const r = 4 // 圆角半径
      ctx.beginPath()
      ctx.moveTo(badgeX + r, badgeY)
      ctx.lineTo(badgeX + badgeW - r, badgeY)
      ctx.arc(badgeX + badgeW - r, badgeY + r, r, 1.5 * Math.PI, 2 * Math.PI)
      ctx.lineTo(badgeX + badgeW, badgeY + badgeH - r)
      ctx.arc(badgeX + badgeW - r, badgeY + badgeH - r, r, 0, 0.5 * Math.PI)
      ctx.lineTo(badgeX + r, badgeY + badgeH)
      ctx.arc(badgeX + r, badgeY + badgeH - r, r, 0.5 * Math.PI, Math.PI)
      ctx.lineTo(badgeX, badgeY + r)
      ctx.arc(badgeX + r, badgeY + r, r, Math.PI, 1.5 * Math.PI)
      ctx.closePath()
      ctx.fill()

      // --- 3. 绘制文字 ---
      ctx.setFillStyle('#ffffff')      // 白色文字对比度更高
      ctx.setTextAlign('left')
      ctx.fillText(labelText, badgeX + 6, badgeY + 13) // 微调文字对齐
  }

  // 5. 绘制阴影面积
  if (points.length > 0) {
    const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom)
    gradient.addColorStop(0, 'rgba(131, 139, 139, 0.25)')
    gradient.addColorStop(1, 'rgba(131, 139, 139, 0)')
    
    ctx.beginPath()
    ctx.moveTo(points[0].x, height - padding.bottom)
    points.forEach(p => ctx.lineTo(p.x, p.y))
    ctx.lineTo(points[points.length - 1].x, height - padding.bottom)
    ctx.closePath()
    ctx.setFillStyle(gradient)
    ctx.fill()
  }

  // 6. 绘制折线
  ctx.setLineDash([])
  ctx.setStrokeStyle('#838B8B')
  ctx.setLineWidth(3)
  ctx.setLineJoin('round')
  ctx.beginPath()
  points.forEach((p, i) => {
    if (i === 0) ctx.moveTo(p.x, p.y)
    else ctx.lineTo(p.x, p.y)
  })
  ctx.stroke()

  // 7. 绘制数据点与文字标签
  points.forEach((p, i) => {
    // 只在有数据时绘制实心点
    if (p.val > 0) {
      ctx.setFillStyle('#838B8B')
      ctx.beginPath()
      ctx.arc(p.x, p.y, 4, 0, 2 * Math.PI)
      ctx.fill()
    }
    
    // X轴文字 (日期)
    const showLabel = energySummaryPeriod.value === 'daily' ? (i % 2 === 0) : true
    if (showLabel) {
      ctx.setFontSize(12)
      ctx.setFillStyle('#94a3b8')
      ctx.setTextAlign('center')
      ctx.fillText(p.label, p.x, height - 15)
    }
  })

  ctx.draw()
}

// 自动聚焦：如果是查看当月，自动滚到今天的位置
const focusCurrentDate = () => {
  const today = new Date().getDate();
  const dateObj = new Date(selectedDate.value);
  const month = dateObj.getMonth();

  if (energySummaryPeriod.value === 'daily') {
    // 聚焦到当前日期（减2是为了让当前日期显示在中间偏左一点）
    scrollLeft.value = Math.max(0, (today - 2) * pointSpacing);
  } else {
    // 修复：将 width 改为 chartTotalWidth.value
    scrollLeft.value = chartTotalWidth.value; 
  }
};

const changePeriod = (val) => {
  if (energySummaryPeriod.value === val) return
  energySummaryPeriod.value = val
  getTrendData()
}

const changeType = (val) => {
  if (energySummaryType.value === val) return
  energySummaryType.value = val
  getTrendData()
}

onMounted(() => {
  getSummary()
  getTrendData()
})
</script>

<style scoped lang="scss">
.app-safe-area {
  background-color: #f8fafc;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  min-height: 100vh;
}

.summary-app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  padding: 32rpx 40rpx;
  padding-top: calc(32rpx + env(safe-area-inset-top) + 20rpx);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  position: sticky;
  top: 30rpx;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
  margin-bottom: 8rpx;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.back-icon-btn {
  background: none;
  border: none;
  padding: 16rpx;
  margin-left: -16rpx;
  color: #1e293b;
  min-width: 88rpx;
  min-height: 88rpx;
}

.back-icon {
  font-size: 44rpx;
  font-weight: bold;
  line-height: 1;
}

.app-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1e293b;
}

.date-picker {
  min-width: 200rpx;
  flex-shrink: 0;
}

.date-display {
  font-size: 28rpx;
  color: #475569;
  padding: 16rpx 24rpx;
  background: #fff;
  border-radius: 16rpx;
  border: 2rpx solid #e2e8f0;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  white-space: nowrap;
  text-align: center;
}

.app-scroll-content {
  flex: 1;
}

.hero-section {
  padding: 0 32rpx 32rpx;
}

.energy-hero-card {
  background: #ffffff;
  border-radius: 56rpx;
  padding: 60rpx 40rpx;
  text-align: center;
  box-shadow: 0 20rpx 50rpx rgba(0,0,0,0.03);
}

.hero-label {
  font-size: 26rpx;
  color: #94a3b8;
  font-weight: 500;
  display: block;
}

.hero-val {
  font-size: 104rpx;
  font-weight: 800;
  color: #1e293b;
  margin: 20rpx 0;
  letter-spacing: -2rpx;
  display: block;
}

.hero-stats-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 64rpx;
  margin: 40rpx 0;
}

.h-stat {
  display: flex;
  flex-direction: column;
}

.h-label {
  font-size: 22rpx;
  color: #94a3b8;
  margin-bottom: 8rpx;
}

.h-val {
  font-size: 36rpx;
  font-weight: 700;
}

.intake {
  color: #334155;
}

.burn {
  color: #838B8B;
}

.h-divider {
  width: 2rpx;
  height: 56rpx;
  background: #f1f5f9;
}

.bmr-tdee-bar {
  display: inline-flex;
  align-items: center;
  gap: 16rpx;
  background: #f8fafc;
  padding: 12rpx 32rpx;
  border-radius: 40rpx;
  font-size: 22rpx;
  color: #94a3b8;
}

.dot {
  color: #cbd5e1;
}

.ai-section {
  padding: 0 32rpx 32rpx;
}

.ai-app-card {
  background: #ffffff;
  border-radius: 48rpx;
  padding: 40rpx;
  border-left: 10rpx solid #838B8B;
  box-shadow: 0 8rpx 30rpx rgba(0,0,0,0.02);
}

.ai-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.ai-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #838B8B;
}

.ai-spark {
  font-size: 32rpx;
  margin-right: 8rpx;
}

.ai-spark-anim {
  display: inline-block;
  animation: spark 2s infinite ease-in-out;
  font-size: 32rpx;
  margin-right: 8rpx;
}

@keyframes spark {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.2); opacity: 1; }
}

.ai-text-box {
  font-size: 28rpx;
  line-height: 1.7;
  color: #475569;
  white-space: pre-line;
}

.ai-empty-state {
  text-align: center;
  padding: 40rpx 0;
}

.app-btn-primary {
  background: #838B8B;
  color: white;
  border: none;
  padding: 20rpx 48rpx;
  border-radius: 24rpx;
  font-weight: 600;
  width: 100%;
  margin-top: 24rpx;
}

.re-gen-btn {
  color: #838B8B;
  font-size: 28rpx;
  padding: 8rpx 16rpx;
}

.custom-skeleton {
  margin-top: 24rpx;
}

.sk-line {
  height: 24rpx;
  background: #f1f5f9;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.short {
  width: 60%;
}

.long {
  width: 100%;
}

.medium {
  width: 80%;
}

.nutrient-section {
  padding: 0 32rpx 48rpx;
}

.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24rpx;
  padding-left: 8rpx;
  display: block;
}

.nutrient-card {
  background: #fff;
  border-radius: 40rpx;
  padding: 40rpx;
}

.nut-row {
  margin-bottom: 36rpx;
}

.nut-meta {
  display: flex;
  justify-content: space-between;
  font-size: 26rpx;
  margin-bottom: 16rpx;
}

.n-name {
  color: #475569;
}

.n-val {
  color: #94a3b8;
}

.bold {
  font-weight: 700;
  color: #475569;
}

.progress-bar {
  width: 100%;
  height: 18rpx;
  background: #f1f5f9;
  border-radius: 18rpx;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  border-radius: 18rpx;
  transition: width 0.3s ease;
}

.detail-section {
  padding: 0 32rpx 48rpx;
}

.app-list {
  background: #fff;
  border-radius: 40rpx;
  overflow: hidden;
}

.app-list-item {
  padding: 32rpx 40rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2rpx solid #f8fafc;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.item-title {
  font-size: 28rpx;
  color: #1e293b;
  font-weight: 500;
}

.item-sub {
  font-size: 24rpx;
  color: #94a3b8;
}

.item-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #475569;
}

.item-value.exercise {
  color: #838B8B;
}

.empty-list {
  padding: 60rpx;
  text-align: center;
  color: #cbd5e1;
  font-size: 28rpx;
}

.trend-section {
  padding: 0 32rpx 48rpx;
}

.chart-app-card {
  background: #fff;
  border-radius: 20px;
  padding: 20px;
}

.chart-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.segmented {
  display: flex;
  background: #f1f5f9;
  border-radius: 24rpx;
  overflow: hidden;
}

.seg-btn {
  padding: 12rpx 28rpx;
  font-size: 26rpx;
  color: #475569;
}

.seg-btn.active {
  background: #838B8B;
  color: #fff;
}

.chart-scroll-container {
  width: 100%;
  height: 480rpx;
  position: relative;
}

.chart-scroll-view {
  width: 100%;
  height: 480rpx;
}

.canvas-container {
  height: 480rpx;
  position: relative;
  display: block;
}

.trend-canvas {
  width: 100%;
  height: 480rpx;
  display: block;
}

.empty-trend {
  padding: 60rpx;
  text-align: center;
  color: #cbd5e1;
  font-size: 28rpx;
}

.app-footer {
  text-align: center;
  color: #cbd5e1;
  font-size: 22rpx;
  padding-bottom: 40rpx;
}
</style>