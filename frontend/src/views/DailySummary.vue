<template>
  <div>
    <h1>Daily Summary</h1>
    <el-date-picker v-model="selectedDate" type="date" placeholder="Pick a day" @change="getSummary"></el-date-picker>

    <div v-if="summary">
      <h2>Summary for {{ selectedDate }}</h2>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card>
            <div slot="header">Calories</div>
            <div>Intake: {{ summary.total_intake_kcal.toFixed(2) }} kcal</div>
            <div>Expenditure: {{ summary.total_burned_kcal.toFixed(2) }} kcal</div>
            <div>Balance: {{ summary.net_calories.toFixed(2) }} kcal</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <div slot="header">Macronutrients</div>
            <div>Protein: {{ summary.total_protein_g.toFixed(2) }} g</div>
            <div>Fat: {{ summary.total_fat_g.toFixed(2) }} g</div>
            <div>Carbohydrates: {{ summary.total_carbs_g.toFixed(2) }} g</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
             <div slot="header">Recommendations</div>
            <div>Target Calories: {{ summary.recommended_daily_kcal.toFixed(2) }} kcal</div>
            <div>Protein: {{ summary.recommended_protein_g.toFixed(2) }} g</div>
            <div>Fat: {{ summary.recommended_fat_g.toFixed(2) }} g</div>
            <div>Carbohydrates: {{ summary.recommended_carbs_g.toFixed(2) }} g</div>
          </el-card>
        </el-col>
      </el-row>

      <h3>Logged Foods</h3>
      <el-table :data="summary.food_log" style="width: 100%">
        <el-table-column prop="food.description" label="Food"></el-table-column>
        <el-table-column prop="serving_grams" label="Serving (g)"></el-table-column>
        <el-table-column prop="total_calories" label="Calories (kcal)"></el-table-column>
      </el-table>

      <h3>Logged Exercises</h3>
      <el-table :data="summary.exercise_log" style="width: 100%">
        <el-table-column prop="exercise_name" label="Exercise"></el-table-column>
        <el-table-column prop="duration_minutes" label="Duration (min)"></el-table-column>
        <el-table-column prop="calories_burned" label="Calories Burned (kcal)"></el-table-column>
      </el-table>
    </div>

    <el-divider></el-divider>

    <h1>Energy Summary</h1>
    <el-form :inline="true" @submit.prevent="getEnergySummary">
      <el-form-item label="Date Range">
        <el-date-picker
          v-model="energySummaryDateRange"
          type="daterange"
          range-separator="To"
          start-placeholder="Start date"
          end-placeholder="End date"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="Period">
        <el-select v-model="energySummaryPeriod" placeholder="Select period">
          <el-option label="Daily" value="daily"></el-option>
          <el-option label="Monthly" value="monthly"></el-option>
          <el-option label="Yearly" value="yearly"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Type">
        <el-select v-model="energySummaryType" placeholder="Select type">
          <el-option label="Intake" value="intake"></el-option>
          <el-option label="Expenditure" value="expenditure"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="getEnergySummary">Get Summary</el-button>
      </el-form-item>
    </el-form>

    <div v-if="energySummary">
      <h3>Energy Summary Results</h3>
      <el-table :data="energySummary.data" style="width: 100%">
        <el-table-column prop="period" label="Period"></el-table-column>
        <el-table-column prop="total_calories" label="Total Calories (kcal)"></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

// Existing daily summary refs
const selectedDate = ref(new Date().toISOString().split('T')[0])
const summary = ref(null)

// Energy summary refs
const energySummaryDateRange = ref([])
const energySummaryPeriod = ref('daily')
const energySummaryType = ref('intake')
const energySummary = ref(null)

const getSummary = async () => {
  try {
    const response = await api.getDailySummary(selectedDate.value)
    summary.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const getEnergySummary = async () => {
  if (!energySummaryDateRange.value || energySummaryDateRange.value.length !== 2) {
    // Handle error: date range is not selected
    console.error("Please select a date range.");
    return;
  }
  try {
    const params = {
      start_date: energySummaryDateRange.value[0],
      end_date: energySummaryDateRange.value[1],
      period_type: energySummaryPeriod.value,
      energy_type: energySummaryType.value,
    }
    const response = await api.getEnergySummary(params)
    energySummary.value = response.data
  } catch (error) {
    console.error(error)
  }
}

// Fetch daily summary on component mount
getSummary()
</script>
