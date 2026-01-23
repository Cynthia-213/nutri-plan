<template>
  <view class="app-safe-area">
    <view class="app-container">
      <view class="app-header">
        <view class="header-left">
          <text class="app-title">食物追踪</text>
        </view>
        <text class="add-new-link" @tap="handleAddFood">添加食物</text>
      </view>

      <view class="sticky-search">
        <view class="search-wrapper">
          <text class="search-icon">🔍</text>
          <input
            v-model="searchQuery"
            placeholder="输入食物名称...支持中英文搜索"
            confirm-type="search"
            @confirm="handleSearch"
            @input="onInput" 
            class="search-input"
          />
        </view>
      </view>

      <scroll-view class="app-content-scroll" scroll-y>
        <view v-if="loading" class="loading-wrapper">
          <view class="loading-spinner"></view>
          <text class="loading-text">正在寻找美味...</text>
        </view>
        
        <view v-else-if="foods.length > 0" class="food-list">
          <view v-for="food in foods" :key="food.id" class="food-card">
            <view class="card-main">
              <view class="food-info">
                <text class="name-zh">{{ food.description_zh || food.description_en }}</text>
                <text class="name-en">{{ food.description_en }}</text>
                <view class="nutrient-tags">
                  <text class="cal-tag">{{ food.energy_kcal }} <text class="unit-small">kcal / 100g</text></text>
                  <view class="source-tag" :class="getTagClass(food.source)">
                    <text>{{ getSourceDisplayName(food.source) }}</text>
                  </view>
                </view>
              </view>
              <view class="circle-add-btn" @tap="logFood(food)" hover-class="btn-hover">
                <text class="plus-icon">+</text>
              </view>
            </view>

            <view class="card-footer">
              <view class="nutrient-stats">
                <view class="stat-box">
                  <text class="stat-label">蛋白质</text>
                  <text class="stat-value prot">{{ food.protein_g }}g</text>
                </view>
                <view class="stat-box">
                  <text class="stat-label">脂肪</text>
                  <text class="stat-value fat">{{ food.fat_g }}g</text>
                </view>
                <view class="stat-box">
                  <text class="stat-label">碳水</text>
                  <text class="stat-value carb">{{ food.carbohydrate_g }}g</text>
                </view>
              </view>
              <view class="single-serving-box">
                <input type="number" v-model.number="food.serving" class="serving-input" />
                <text class="serving-unit">克</text>
              </view>
            </view>
          </view>
          
          <view class="pagination-wrapper">
            <view class="page-arrow" :class="{ disabled: currentPage === 1 }" @tap="prevPage">◀</view>
            <text class="page-info">{{ currentPage }} / {{ totalPages }}</text>
            <view class="page-arrow" :class="{ disabled: currentPage >= totalPages }" @tap="nextPage">▶</view>
          </view>
        </view>

        <view v-else-if="!loading && hasSearched && foods.length === 0" class="empty-state">
          <text class="empty-text">未能找到“{{ searchQuery }}”</text>
          <text class="empty-sub">换个词试试，或者手动添加</text>
        </view>

      </scroll-view>
    </view>

    <!-- 选择餐别弹窗 -->
    <view v-if="showMealTypeModal" class="modal-overlay" @tap="closeMealTypeModal">
      <view class="meal-type-modal" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">选择餐别</text>
          <view class="modal-close-btn" @tap="closeMealTypeModal">×</view>
        </view>
        <view class="modal-body">
          <!-- <text class="meal-type-food-name">{{ selectedFood?.description_zh || selectedFood?.description_en || '' }}</text> -->
          <view class="meal-type-options">
            <view
              v-for="meal in mealTypes"
              :key="meal.value"
              class="meal-type-item"
              :class="{ active: selectedMealType === meal.value }"
              @tap="selectMealType(meal.value)"
            >
              <text class="meal-icon">{{ meal.icon }}</text>
              <text class="meal-label">{{ meal.label }}</text>
            </view>
          </view>
          <view class="meal-type-footer">
            <button class="btn-cancel" @tap="closeMealTypeModal">取消</button>
            <button class="btn-confirm" @tap="confirmLogFood" :disabled="!selectedMealType">
              确认记录
            </button>
          </view>
        </view>
      </view>
    </view>

    <!-- 添加食物弹窗 -->
    <view v-if="showAddModal" class="modal-overlay" @tap="closeAddModal">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">添加新食物</text>
          <view class="modal-close-btn" @tap="closeAddModal">×</view>
        </view>
        <scroll-view class="modal-body" scroll-y>
          <view class="form-group">
            <text class="form-label">食物名称（中文）<text class="required">*</text></text>
            <input
              v-model="newFood.description_zh"
              placeholder="请输入食物中文名称"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">食物名称（英文）</text>
            <input
              v-model="newFood.description_en"
              placeholder="请输入食物英文名称（可选）"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">热量（kcal/100g）</text>
            <input
              type="number"
              v-model.number="newFood.energy_kcal"
              placeholder="0"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">蛋白质（g/100g）</text>
            <input
              type="number"
              v-model.number="newFood.protein_g"
              placeholder="0"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">脂肪（g/100g）</text>
            <input
              type="number"
              v-model.number="newFood.fat_g"
              placeholder="0"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">碳水（g/100g）</text>
            <input
              type="number"
              v-model.number="newFood.carbohydrate_g"
              placeholder="0"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">膳食纤维（g/100g）</text>
            <input
              type="number"
              v-model.number="newFood.fiber_total_dietary_g"
              placeholder="0"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">糖（g/100g）</text>
            <input
              type="number"
              v-model.number="newFood.sugars_g"
              placeholder="0"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">铁（mg/100g）</text>
            <input
              type="number"
              v-model.number="newFood.fe_mg"
              placeholder="0"
              class="form-input"
            />
          </view>
          <view class="form-group">
            <text class="form-label">钠（mg/100g）</text>
            <input
              type="number"
              v-model.number="newFood.na_mg"
              placeholder="0"
              class="form-input"
            />
          </view>
        
        </scroll-view>
        <view class="modal-footer">
          <view class="modal-btn modal-btn-cancel" @tap="closeAddModal">取消</view>
          <view class="modal-btn modal-btn-submit" @tap="submitAddFood" :class="{ disabled: submitting }">
            {{ submitting ? '提交中...' : '提交' }}
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

const hasSearched = ref(false) 
const searchQuery = ref('')
const foods = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showAddModal = ref(false)
const submitting = ref(false)
const newFood = ref({
  description_zh: '',
  description_en: '',
  energy_kcal: null,
  protein_g: null,
  fat_g: null,
  carbohydrate_g: null
})

// 餐别选择相关
const showMealTypeModal = ref(false)
const selectedFood = ref(null)
const selectedMealType = ref('')
const mealTypes = [
  { value: 'breakfast', label: '早餐', icon: '🌅' },
  { value: 'lunch', label: '午餐', icon: '☀️' },
  { value: 'dinner', label: '晚餐', icon: '🌙' },
  { value: 'snack', label: '零食', icon: '🍪' }
]

const sourceMap = {
  'fndd': 'FNDD 美国食品库',
  'foundation': 'USDA 基础营养库',
  'CDC China': 'CDC 中国食物成分表',
  'user': '用户自定义'
}

const getSourceDisplayName = (source) => sourceMap[source] || source

const getTagClass = (source) => {
  if (source === 'CDC China') return 'tag-success'
  if (source === 'user') return 'tag-warning'
  return 'tag-info'
}

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const onInput = () => {
  if (!searchQuery.value) {
    hasSearched.value = false
    foods.value = []
  }
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  currentPage.value = 1
  fetchFoods()
}

const fetchFoods = async () => {
  if (!searchQuery.value) return
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await api.getFoods(searchQuery.value, skip, pageSize.value)
    hasSearched.value = true 
    if (response && response.items) {
      foods.value = response.items.map(f => ({ ...f, serving: 100 }))
      total.value = response.total || 0
    }
  } catch (error) {
    console.error('获取列表失败:', error)
    hasSearched.value = true
    foods.value = []
  } finally {
    loading.value = false
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchFoods()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchFoods()
  }
}

const logFood = (food) => {
  // 显示餐别选择弹窗
  selectedFood.value = food
  selectedMealType.value = ''
  showMealTypeModal.value = true
}

const selectMealType = (mealType) => {
  selectedMealType.value = mealType
}

const closeMealTypeModal = () => {
  showMealTypeModal.value = false
  selectedFood.value = null
  selectedMealType.value = ''
}

const confirmLogFood = async () => {
  if (!selectedMealType.value || !selectedFood.value) return
  
  try {
    await api.logFood({
      food_id: selectedFood.value.id,
      serving_grams: selectedFood.value.serving,
      log_date: new Date().toISOString().split('T')[0],
      meal_type: selectedMealType.value
    })
    uni.showToast({
      title: '已记录',
      icon: 'success',
      duration: 1500
    })
    closeMealTypeModal()
  } catch (e) {
    uni.showToast({ title: '记录失败', icon: 'none' })
  }
}

const handleAddFood = () => {
  showAddModal.value = true
  // 重置表单
  newFood.value = {
    description_zh: '',
    description_en: '',
    energy_kcal: null,
    protein_g: null,
    fat_g: null,
    carbohydrate_g: null
  }
}

const closeAddModal = () => {
  showAddModal.value = false
}

const submitAddFood = async () => {
  // 验证必填字段
  if (!newFood.value.description_zh || !newFood.value.description_zh.trim()) {
    uni.showToast({
      title: '请输入食物名称',
      icon: 'none'
    })
    return
  }

  submitting.value = true
  try {
    // 构建请求数据，只包含有值的字段
    const foodData = {
      description_zh: newFood.value.description_zh.trim(),
      source: 'user'
    }
    
    // 添加可选字段
    if (newFood.value.description_en && newFood.value.description_en.trim()) {
      foodData.description_en = newFood.value.description_en.trim()
    }
    if (newFood.value.energy_kcal !== null && newFood.value.energy_kcal !== '') {
      foodData.energy_kcal = Number(newFood.value.energy_kcal)
    }
    if (newFood.value.protein_g !== null && newFood.value.protein_g !== '') {
      foodData.protein_g = Number(newFood.value.protein_g)
    }
    if (newFood.value.fat_g !== null && newFood.value.fat_g !== '') {
      foodData.fat_g = Number(newFood.value.fat_g)
    }
    if (newFood.value.carbohydrate_g !== null && newFood.value.carbohydrate_g !== '') {
      foodData.carbohydrate_g = Number(newFood.value.carbohydrate_g)
    }

    // 调用后端接口创建食物
    await api.createFood(foodData)
    
    uni.showToast({
      title: '添加成功',
      icon: 'success',
      duration: 1500
    })
    
    closeAddModal()
    
    // 如果当前有搜索，刷新列表
    if (searchQuery.value) {
      currentPage.value = 1
      fetchFoods()
    }
  } catch (error) {
    console.error('添加食物失败:', error)
    uni.showToast({
      title: error.response?.data?.detail || '添加失败，请重试',
      icon: 'none',
      duration: 2000
    })
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.app-safe-area {
  background-color: #f8fafc;
  min-height: 100vh;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
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

.app-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1e293b;
}

.add-new-link {
  color: #838B8B;
  font-weight: 600;
  font-size: 30rpx;
}

.sticky-search {
  padding: 16rpx 40rpx; /* 关键：确保搜索框左右间距与卡片对齐 */
  background: #f8fafc;
}

.search-wrapper {
  display: flex;
  align-items: center;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 24rpx 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.search-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
}

.search-input {
  flex: 1;
  font-size: 32rpx;
}

.app-content-scroll {
  flex: 1;
}

.food-list {
  padding: 20rpx 40rpx 40rpx; /* 关键：40rpx 侧边距确保对齐 */
  box-sizing: border-box;
}

.food-card {
  background: #ffffff;
  border-radius: 40rpx;
  padding: 32rpx;
  margin-bottom: 28rpx;
  box-shadow: 0 12rpx 32rpx rgba(0, 0, 0, 0.03);
  box-sizing: border-box;
}

.card-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.name-zh {
  font-size: 34rpx;
  font-weight: 800;
  color: #1e293b;
}

.name-en {
  font-size: 24rpx;
  color: #94a3b8;
  margin-top: 4rpx;
}

.nutrient-tags {
  display: flex;
  gap: 16rpx;
  margin-top: 20rpx;
  align-items: center;
}

.cal-tag {
  font-size: 28rpx;
  color: #838B8B;
  font-weight: 700;
  .unit-small { font-size: 20rpx; font-weight: 400; }
}

.source-tag {
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.tag-success { background: #f0fdf4; color: #16a34a; }
.tag-warning { background: #fffbeb; color: #d97706; }
.tag-info { background: #f8fafc; color: #64748b; }

.circle-add-btn {
  width: 90rpx;
  height: 90rpx;
  border-radius: 30rpx;
  background: #838B8B;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 20rpx rgba(131, 139, 139, 0.3);
  .plus-icon { color: white; font-size: 48rpx; }
}

.card-footer {
  border-top: 2rpx dashed #f1f5f9;
  padding-top: 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nutrient-stats {
  display: flex;
  gap: 32rpx;
}

.stat-box {
  display: flex;
  flex-direction: column;
  .stat-label { font-size: 20rpx; color: #94a3b8; margin-bottom: 4rpx; }
  .stat-value { font-size: 26rpx; font-weight: 700; color: #475569; }
}

/* 优化后的单长方形克数容器 */
.single-serving-box {
  background: #f1f5f9;
  height: 72rpx;
  padding: 0 24rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .serving-input {
    width: 80rpx;
    height: 100%;
    font-size: 32rpx;
    font-weight: 800;
    color: #1e293b;
    text-align: center;
  }
  
  .serving-unit {
    font-size: 24rpx;
    color: #64748b;
    margin-left: 4rpx;
    font-weight: 600;
  }
}

.loading-wrapper { padding: 100rpx 0; text-align: center; }
.empty-state, .search-tip { 
  display: flex; flex-direction: column; align-items: center; padding-top: 160rpx; 
}
.tip-circle {
  width: 140rpx; height: 140rpx; background: #fff; border-radius: 70rpx;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.05); margin-bottom: 30rpx;
}
.tip-icon { font-size: 60rpx; }
.tip-text { font-size: 32rpx; font-weight: 700; color: #1e293b; }
.tip-sub { font-size: 26rpx; color: #94a3b8; margin-top: 10rpx; }

.pagination-wrapper {
  display: flex; align-items: center; justify-content: center; gap: 40rpx; padding: 40rpx 0;
}
.page-arrow {
  width: 80rpx; height: 80rpx; background: #fff; border-radius: 40rpx;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); color: #838B8B;
  &.disabled { opacity: 0.3; }
}

/* 添加食物弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 40rpx;
  box-sizing: border-box;
}

.modal-content {
  background: #ffffff;
  border-radius: 32rpx;
  width: 100%;
  max-width: 680rpx;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.15);
  box-sizing: border-box;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 2rpx solid #f1f5f9;
  box-sizing: border-box;
  flex-shrink: 0;
}

.modal-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1e293b;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 56rpx;
  color: #94a3b8;
  line-height: 1;
  padding: 0;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  flex: 1;
  padding: 32rpx;
  max-height: calc(85vh - 200rpx);
  box-sizing: border-box;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 32rpx;
  width: 100%;
  box-sizing: border-box;
}

.form-group-half {
  flex: 1;
  margin-bottom: 32rpx;
  min-width: 0;
  box-sizing: border-box;
}

.form-row {
  display: flex;
  gap: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #475569;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.required {
  color: #ef4444;
  margin-left: 4rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  border: 2rpx solid #e2e8f0;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  color: #1e293b;
  box-sizing: border-box;
  background: #ffffff;
  max-width: 100%;
}

.form-input:focus {
  border-color: #838B8B;
  outline: none;
}

/* 餐别选择弹窗样式 */
.meal-type-modal {
  background: #ffffff;
  border-radius: 32rpx;
  width: 100%;
  max-width: 600rpx;
  display: flex;
  flex-direction: column;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.15);
  box-sizing: border-box;
  overflow: hidden;
}

.meal-type-food-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1e293b;
  text-align: center;
  margin-bottom: 40rpx;
  padding: 0 32rpx;
}

.meal-type-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
  padding: 0 32rpx;
  margin-bottom: 40rpx;
}

.meal-type-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40rpx 20rpx;
  background: #f8fafc;
  border: 3rpx solid #e2e8f0;
  border-radius: 24rpx;
  transition: all 0.3s;
}

.meal-type-item.active {
  background: #838B8B;
  border-color: #838B8B;
}

.meal-icon {
  font-size: 56rpx;
  margin-bottom: 16rpx;
}

.meal-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #475569;
}

.meal-type-item.active .meal-label {
  color: #ffffff;
}

.meal-type-footer {
  display: flex;
  gap: 24rpx;
  padding: 32rpx;
  border-top: 2rpx solid #f1f5f9;
  box-sizing: border-box;
}

.btn-cancel {
  flex: 1;
  height: 88rpx;
  background: #f1f5f9;
  color: #475569;
  border: none;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.btn-confirm {
  flex: 1;
  height: 88rpx;
  background: #838B8B;
  color: #ffffff;
  border: none;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.btn-confirm:disabled {
  background: #cbd5e1;
  color: #94a3b8;
  opacity: 0.6;
}

.modal-footer {
  display: flex;
  gap: 24rpx;
  padding: 32rpx;
  border-top: 2rpx solid #f1f5f9;
  box-sizing: border-box;
  flex-shrink: 0;
}

.modal-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-btn-cancel {
  background: #f1f5f9;
  color: #64748b;
}

.modal-btn-submit {
  background: #838B8B;
  color: #ffffff;
}

.modal-btn-submit.disabled {
  background: #cbd5e1;
  color: #94a3b8;
}
</style>