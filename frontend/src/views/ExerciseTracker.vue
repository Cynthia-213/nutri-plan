<template>
  <div>
    <h1>Exercise Tracker</h1>
    <el-form :model="form" label-width="120px">
      <el-form-item label="Exercise">
        <el-select v-model="form.exercise_id" placeholder="Select exercise">
          <el-option v-for="exercise in exercises" :key="exercise.id" :label="exercise.name" :value="exercise.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Duration (min)">
        <el-input-number v-model="form.duration_minutes" :min="1"></el-input-number>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="logExercise">Log Exercise</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'

const exercises = ref([])
const form = reactive({
  exercise_id: null,
  duration_minutes: 30
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
  try {
     const logData = {
      exercise_id: form.exercise_id,
      duration_minutes: form.duration_minutes,
      log_date: new Date().toISOString().split('T')[0]
    }
    await api.logExercise(logData)
    // Handle success
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  getExercises()
})
</script>
