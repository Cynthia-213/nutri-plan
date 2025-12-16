<template>
  <div>
    <h1>AI Menu Suggestions</h1>
    <el-button type="primary" @click="getSuggestions" :loading="loading">Get Suggestions</el-button>

    <div v-if="suggestions">
      <h2>Menu for a Day</h2>
      <el-card>
        <h3>Breakfast</h3>
        <p>{{ suggestions.breakfast }}</p>
      </el-card>
      <el-card>
        <h3>Lunch</h3>
        <p>{{ suggestions.lunch }}</p>
      </el-card>
      <el-card>
        <h3>Dinner</h3>
        <p>{{ suggestions.dinner }}</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const loading = ref(false)
const suggestions = ref(null)

const getSuggestions = async () => {
  loading.value = true
  try {
    const response = await api.getMenuSuggestions()
    suggestions.value = response.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.el-card {
  margin-bottom: 20px;
}
</style>
