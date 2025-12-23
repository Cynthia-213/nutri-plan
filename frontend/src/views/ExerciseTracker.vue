<template>
  <div class="tracker-container">
    <div class="header-section">
      <h1 class="page-title">运动追踪</h1>
      <p class="page-subtitle">记录每一次汗水，见证身体的蜕变。</p>
    </div>

    <div class="content-body">
      <div class="log-card">
        <div class="card-header">
          <el-icon class="header-icon"><TrendCharts /></el-icon>
          <span>新增运动记录</span>
        </div>

        <el-form :model="form" label-position="top" class="custom-form">
          <el-form-item label="运动项目">
            <el-select 
              v-model="form.exercise_id" 
              placeholder="请选择您进行的运动" 
              style="width: 100%"
              size="large"
            >
              <el-option 
                v-for="exercise in exercises" 
                :key="exercise.id" 
                :label="exercise.name" 
                :value="exercise.id"
              >
                <span style="float: left">{{ exercise.name }}</span>
                <span style="float: right; color: #999; font-size: 12px">
                  {{ exercise.calories_per_hour }} kcal/h
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="持续时间 (分钟)">
            <el-input-number 
              v-model="form.duration_minutes" 
              :min="1" 
              :max="1440"
              size="large"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
          
          <el-form-item label="消耗卡路里 (可选)">
            <el-input-number
              v-model="form.calories_burned"
              :min="0"
              placeholder="留空则自动计算"
              size="large"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item>
            <el-button class="btn-primary" @click="logExercise" size="large">
              确认记录
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="tips-panel">
        <div class="tip-item">
          <h4>💡 小贴士</h4>
          <p>持之以恒的运动不仅能消耗卡路里，还能显著提升基础代谢。建议每周进行至少 150 分钟的中等强度运动。</p>
        </div>
        <div class="tip-item quote">
          <p>"运动是天然的抗抑郁剂。"</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../services/api'
import { ElMessage } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'

const exercises = ref([])
const form = reactive({
  exercise_id: null,
  duration_minutes: 30,
  calories_burned: null
})

const getExercises = async () => {
  try {
    const response = await api.getExercises()
    exercises.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const logExercise = async () => {
  if (!form.exercise_id) {
    ElMessage.warning('请选择运动项目')
    return
  }
  try {
     const logData = {
      exercise_id: form.exercise_id,
      duration_minutes: form.duration_minutes,
      calories_burned: form.calories_burned,
      log_date: new Date().toISOString().split('T')[0]
    }
    await api.logExercise(logData)
    ElMessage.success('运动记录成功！')
    // 重置表单
    form.exercise_id = null
    form.duration_minutes = 30
    form.calories_burned = null
  } catch (error) {
    ElMessage.error('记录失败，请重试')
  }
}

onMounted(() => {
  getExercises()
})
</script>

<style scoped>
.tracker-container {
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 20px;
}

.header-section { margin-bottom: 40px; }
.page-title { font-size: 28px; color: #2d3436; margin-bottom: 8px; font-weight: 700; }
.page-subtitle { color: #838B8B; font-size: 14px; }

.content-body {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

/* 卡片样式 */
.log-card {
  flex: 1;
  background: white;
  padding: 35px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
  color: #2d3436;
  font-weight: 600;
  font-size: 18px;
}

.header-icon { color: #838B8B; }

/* 表单定制 */
:deep(.el-form-item__label) {
  font-weight: 600;
  color: #636e72;
}

.energy-preview {
  background-color: #f8f9f9;
  padding: 15px;
  border-radius: 12px;
  text-align: center;
  color: #838B8B;
  margin-bottom: 25px;
  font-size: 14px;
}

.energy-preview strong {
  font-size: 20px;
  margin: 0 5px;
}

/* 按钮 */
.btn-primary {
  width: 100%;
  background-color: #838B8B !important;
  border-color: #838B8B !important;
  height: 50px;
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 1px;
}

.btn-primary:hover {
  background-color: #6e7575 !important;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(131, 139, 139, 0.3);
}

/* 右侧提示面板 */
.tips-panel {
  width: 300px;
}

.tip-item {
  background: rgba(131, 139, 139, 0.05);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
  border-left: 4px solid #838B8B;
}

.tip-item h4 { margin: 0 0 10px 0; color: #2d3436; }
.tip-item p { margin: 0; font-size: 13px; color: #636e72; line-height: 1.6; }

.quote {
  background: none;
  border: none;
  font-style: italic;
  text-align: center;
  color: #b2bec3;
}

@media (max-width: 768px) {
  .content-body { flex-direction: column; }
  .tips-panel { width: 100%; }
}
</style>