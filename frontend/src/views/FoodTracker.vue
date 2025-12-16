<template>
  <div>
    <h1>Food Tracker</h1>
    <el-form :inline="true">
      <el-form-item label="Search Food">
        <el-input v-model="searchQuery" placeholder="Enter food name"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="searchFoods">Search</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="foods" style="width: 100%">
      <el-table-column prop="description" label="Food"></el-table-column>
      <el-table-column prop="calories_kcal" label="Calories (kcal/100g)"></el-table-column>
      <el-table-column prop="protein_g" label="Protein (g/100g)"></el-table-column>
      <el-table-column prop="fat_g" label="Fat (g/100g)"></el-table-column>
      <el-table-column prop="carbohydrate_g" label="Carbs (g/100g)"></el-table-column>
      <el-table-column label="Serving (g)">
        <template #default="scope">
          <el-input-number v-model="scope.row.serving" :min="1" size="small"></el-input-number>
        </template>
      </el-table-column>
      <el-table-column label="Action">
        <template #default="scope">
          <el-button size="small" type="primary" @click="logFood(scope.row)">Log</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const searchQuery = ref('')
const foods = ref([])

const searchFoods = async () => {
  try {
    const response = await api.getFoods(searchQuery.value)
    foods.value = response.data.map(food => ({ ...food, serving: 100 }))
  } catch (error) {
    console.error(error)
  }
}

const logFood = async (food) => {
  try {
    const logData = {
      food_id: food.id,
      serving_grams: food.serving,
      log_date: new Date().toISOString().split('T')[0] 
    }
    await api.logFood(logData)
    // Handle success
  } catch (error) {
    console.error(error)
  }
}
</script>
