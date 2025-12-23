<template>
  <div class="user-me-container">
    <el-skeleton :loading="loading" animated>
      <template #default>
        <div class="profile-layout">
          <div class="sidebar-card">
            <div class="avatar-section">
              <div class="user-avatar">{{ user.username?.charAt(0).toUpperCase() || 'U' }}</div>
              <h2 class="username">{{ user.username }}</h2>
              <el-tag size="small" effect="plain" class="email-tag">{{ user.email }}</el-tag>
            </div>
            <div class="info-list">
              <div class="info-item">
                <span class="label">性别</span>
                <span class="value">{{ translateGender(user.gender) }}</span>
              </div>
              <div class="info-item">
                <span class="label">生日</span>
                <span class="value">{{ user.birthdate || '未设置' }}</span>
              </div>
            </div>
          </div>

          <div class="detail-content">
            <div class="card-header">
              <h3>健康档案详情</h3>
              <el-button size="small" class="btn-outline" @click="openEditDialog">
                编辑资料
              </el-button>
            </div>

            <el-row :gutter="20" class="stat-grid">
              <el-col :span="12">
                <div class="stat-box">
                  <span class="stat-label">身高</span>
                  <div class="stat-main">
                    <span class="stat-value">{{ user.height_cm || '--' }}</span>
                    <span class="stat-unit">cm</span>
                  </div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="stat-box">
                  <span class="stat-label">体重</span>
                  <div class="stat-main">
                    <span class="stat-value">{{ user.weight_kg || '--' }}</span>
                    <span class="stat-unit">kg</span>
                  </div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="stat-box">
                  <span class="stat-label">活动水平</span>
                  <span class="stat-value-text">{{ translateActivity(user.activity_level) }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="stat-box">
                  <span class="stat-label">健身目标</span>
                  <span class="stat-value-text">{{ translateGoal(user.goal) }}</span>
                </div>
              </el-col>
            </el-row>

            <div class="health-dashboard" v-if="bmiValue">
              <div class="dashboard-divider"></div>
              <div class="dashboard-item">
                <div class="dash-left">
                  <span class="dash-label">当前 BMI 指数</span>
                  <div class="dash-main">
                    <span class="dash-value">{{ bmiValue }}</span>
                    <el-tag 
                        :color="bmiStatus.color" 
                        effect="dark" 
                        size="small" 
                        class="status-tag"
                        style="border: none !important; outline: none !important;"
                        >
                        {{ bmiStatus.text }}
                    </el-tag>
                  </div>
                </div>
                <div class="dash-right">
                  <p class="dash-tips">标准范围：18.5 ~ 23.9</p>
                  <div class="bmi-bar">
                    <div class="bmi-pointer" :style="{ left: bmiPosition + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-skeleton>

    <el-dialog v-model="editDialogVisible" title="修改个人资料" width="500px" destroy-on-close>
      <el-form :model="editForm" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="editForm.gender" placeholder="请选择" style="width: 100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
                <el-option label="保密" value="unwilling_to_disclose" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生日">
              <el-date-picker v-model="editForm.birthdate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身高 (cm)">
              <el-input-number v-model="editForm.height_cm" :min="50" :max="250" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体重 (kg)">
              <el-input-number v-model="editForm.weight_kg" :min="20" :max="300" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="活动水平">
              <el-select v-model="editForm.activity_level" style="width: 100%">
                <el-option label="久坐不动" value="sedentary" />
                <el-option label="轻度活跃" value="lightly_active" />
                <el-option label="中度活跃" value="moderately_active" />
                <el-option label="高度活跃" value="very_active" />
                <el-option label="极高强度" value="extra_active" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="健身目标">
              <el-select v-model="editForm.goal" style="width: 100%">
                <el-option label="保持体重" value="maintain" />
                <el-option label="减脂/减重" value="lose_weight" />
                <el-option label="增肌训练" value="gain_muscle" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button class="btn-save" :loading="submitting" @click="handleUpdate">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../services/api'
import { ElMessage } from 'element-plus'

const loading = ref(true)
const submitting = ref(false)
const editDialogVisible = ref(false)
const user = ref({})

const editForm = reactive({
  gender: '',
  birthdate: '',
  height_cm: null,
  weight_kg: null,
  activity_level: '',
  goal: ''
})

// 翻译函数
const translateGender = (g) => ({ male: '男', female: '女', unwilling_to_disclose: '保密' }[g] || '未设置')
const translateActivity = (a) => ({ sedentary: '久坐不动', lightly_active: '轻度活跃', moderately_active: '中度活跃', very_active: '高度活跃', extra_active: '极高强度' }[a] || '未设置')
const translateGoal = (goal) => ({ maintain: '保持体重', lose_weight: '减脂/减重', gain_muscle: '增肌训练' }[goal] || '未设置')

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
  const pos = ((val - 15) / (35 - 15)) * 100 // 15-35范围映射
  return Math.min(Math.max(pos, 5), 95)
})

const fetchUserData = async () => {
  try {
    loading.value = true
    const response = await api.getMe()
    user.value = response.data
  } catch (error) {
    ElMessage.error('获取资料失败')
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
    goal: user.value.goal
  })
  editDialogVisible.value = true
}

const handleUpdate = async () => {
  try {
    submitting.value = true
    await api.updateMe(editForm)
    ElMessage.success('资料更新成功')
    editDialogVisible.value = false
    await fetchUserData()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchUserData)
</script>

<style scoped>
.user-me-container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
.profile-layout { display: flex; gap: 30px; align-items: flex-start; }

/* 左侧卡片 */
.sidebar-card { width: 280px; background: #fff; border-radius: 20px; padding: 40px 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); text-align: center; }
.user-avatar { width: 70px; height: 70px; background-color: #838B8B; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: bold; margin: 0 auto 20px; }
.username { font-size: 20px; color: #2d3436; margin-bottom: 8px; }
.email-tag { color: #838B8B !important; border-color: #838B8B !important; margin-bottom: 30px; }
.info-list { border-top: 1px solid #f0f0f0; padding-top: 20px; }
.info-item { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 13px; }
.info-item .label { color: #94a3b8; }
.info-item .value { color: #2d3436; font-weight: 500; }

/* 右侧内容 */
.detail-content { flex: 1; background: #fff; border-radius: 20px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.card-header h3 { color: #838B8B; margin: 0; font-size: 18px; }

/* 统计网格 */
.stat-box { background: #f8fafc; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
.stat-label { font-size: 12px; color: #94a3b8; display: block; margin-bottom: 8px; }
.stat-main { display: flex; align-items: baseline; gap: 4px; }
.stat-value { font-size: 24px; font-weight: bold; color: #2d3436; }
.stat-unit { font-size: 12px; color: #94a3b8; }
.stat-value-text { font-size: 16px; font-weight: 600; color: #838B8B; }
.stat-box.highlight { background: rgba(131, 139, 139, 0.05); }

/* BMI 仪表盘 */
.dashboard-divider { height: 1px; background: #f0f0f0; margin: 10px 0 25px; }
.dashboard-item { display: flex; justify-content: space-between; align-items: center; background: #fcfcfc; padding: 20px; border-radius: 15px; }
.dash-main { display: flex; align-items: center; gap: 12px; margin-top: 8px; }
.dash-value { font-size: 32px; font-weight: 800; color: #2d3436; }
.dash-right { width: 220px; }
.dash-tips { font-size: 12px; color: #94a3b8; text-align: right; margin-bottom: 10px; }
.bmi-bar { height: 6px; background: linear-gradient(to right, #3498db, #2ecc71, #f1c40f, #e74c3c); border-radius: 3px; position: relative; }
.bmi-pointer { position: absolute; top: -4px; width: 2px; height: 14px; background: #2d3436; transition: left 0.5s; }

/* 按钮样式 */
.btn-outline { border-color: #838B8B !important; color: #838B8B !important; }
.btn-save { background-color: #838B8B !important; color: white !important; border: none; }
</style>