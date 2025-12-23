<template>
  <div class="tracker-container">
    <el-alert
      title="温馨提示：本平台提供的食物营养数据、能量计算及建议仅供参考，不作为医疗诊断依据。"
      type="info"
      :closable="false"
      show-icon
      class="data-disclaimer"
    />
    <div class="header-section">
      <h1 class="page-title">食物追踪</h1>
      <p class="page-subtitle">记录每一餐的营养，掌控健康生活。</p>
    </div>

    <div class="search-card">
      <el-form :inline="true" class="search-form" @submit.prevent>
        <el-form-item label="快速搜索">
          <el-input 
            v-model="searchQuery" 
            placeholder="输入食物名称" 
            clearable
            @keyup.enter="handleSearch"
            class="custom-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button class="btn-primary" @click="handleSearch">搜索食物</el-button>
          <el-button class="btn-outline" @click="dialogVisible = true">添加新食物</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-card">
      <el-table v-loading="loading" :data="foods" style="width: 100%" stripe>
        <el-table-column fixed label="食物名称" min-width="180">
          <template #default="scope">
            <div class="food-name-cell">
              <span class="zh">{{ scope.row.description_zh || scope.row.description_en }}</span>
              <span class="en" v-if="scope.row.description_zh">{{ scope.row.description_en }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="energy_kcal" label="热量" width="100" align="center">
          <template #default="scope">
            <span class="nutrient-value">{{ scope.row.energy_kcal }}</span>
            <span class="unit"> kcal</span>
          </template>
        </el-table-column>

        <el-table-column label="主要营养成分 (每100g)" align="center">
          <el-table-column prop="protein_g" label="蛋白质" width="80" />
          <el-table-column prop="fat_g" label="脂肪" width="80" />
          <el-table-column prop="carbohydrate_g" label="碳水" width="80" />
        </el-table-column>
        <el-table-column label="数据来源" width="140" align="center">
          <template #default="scope">
            <el-tag :type="getTagType(scope.row.source)" effect="plain" size="small">
              {{ getSourceDisplayName(scope.row.source) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="记录份量" width="160" align="center">
          <template #default="scope">
            <el-input-number 
              v-model="scope.row.serving" 
              :min="1" 
              size="small"
              controls-position="right"
              class="serving-input"
            />
            <span class="unit-text"> 克</span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" label="操作" width="100" align="center">
          <template #default="scope">
            <el-button class="btn-action" size="small" @click="logFood(scope.row)">记录</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 状态变量
const searchQuery = ref('')
const foods = ref([])
const loading = ref(false)
const dialogVisible = ref(false)

// 分页变量
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const sourceMap = {
  'fndd': '美国食品数据库',
  'foundation': '美国基础营养库',
  'CDC China': '中国食物成分表',
  'user': '用户自定义'
}

const getTagType = (source) => {
  switch (source) {
    case 'fndd':
    case 'foundation':
      return 'info'
    case 'CDC China':
      return 'success'
    case 'user':
      return 'warning'
    default:
      return 'default'
  }
}

const getSourceDisplayName = (source) => sourceMap[source] || source;

// 获取数据
const fetchFoods = async () => {
  if (!searchQuery.value) return
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    // 这里的参数对应后端的 search, skip, limit
    const response = await api.getFoods(searchQuery.value, skip, pageSize.value)
    
    // 对应后端的新结构 {"total": x, "items": []}
    foods.value = response.data.items.map(f => ({ ...f, serving: 100 }))
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取食物列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchFoods()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchFoods()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchFoods()
}

const logFood = async (food) => {
  try {
    await api.logFood({
      food_id: food.id,
      serving_grams: food.serving,
      log_date: new Date().toISOString().split('T')[0]
    })
    ElMessage.success(`已记录 ${food.description_zh || food.description_en}`)
  } catch (e) {
    ElMessage.error('记录失败')
  }
}

onMounted(() => fetchFoods())
</script>

<style scoped>
.tracker-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.header-section { margin-bottom: 30px; }
.page-title { font-size: 28px; font-weight: 700; color: #2d3436; }
.page-subtitle { color: #838B8B; font-size: 14px; }

.search-card { background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 24px; }
.table-card { background: white; border-radius: 16px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }

/* 分页容器靠右 */
.pagination-wrapper {
  margin-top: 25px;
  display: flex;
  justify-content: flex-end;
}

.food-name-cell { display: flex; flex-direction: column; }
.food-name-cell .zh { font-weight: 600; color: #2d3436; }
.food-name-cell .en { font-size: 12px; color: #94a3b8; }

/* 颜色覆盖：高级灰主题 */
.btn-primary { background-color: #838B8B !important; border-color: #838B8B !important; color: white !important; }
.btn-outline { border: 1px solid #838B8B !important; color: #838B8B !important; }
.btn-action { background-color: #838B8B !important; color: white !important; border: none; }

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #838B8B !important;
}
:deep(.el-table th) { background-color: #f8f9fa !important; color: #838B8B; font-weight: bold; }
</style>