<template>
  <div>
    <h1>User Registration and Profile</h1>
    <el-form :model="form" label-width="120px">
      <el-form-item label="Username">
        <el-input v-model="form.username"></el-input>
      </el-form-item>
      <el-form-item label="Email">
        <el-input v-model="form.email"></el-input>
      </el-form-item>
      <el-form-item label="Password">
        <el-input type="password" v-model="form.password"></el-input>
      </el-form-item>
      <el-form-item label="Gender">
        <el-radio-group v-model="form.gender">
          <el-radio label="male">Male</el-radio>
          <el-radio label="female">Female</el-radio>
          <el-radio label="other">Other</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="Birthdate">
        <el-date-picker v-model="form.birthdate" type="date" placeholder="Pick a day"></el-date-picker>
      </el-form-item>
      <el-form-item label="Height (cm)">
        <el-input-number v-model="form.height_cm" :min="1"></el-input-number>
      </el-form-item>
      <el-form-item label="Weight (kg)">
        <el-input-number v-model="form.weight_kg" :min="1"></el-input-number>
      </el-form-item>
      <el-form-item label="Activity Level">
        <el-select v-model="form.activity_level" placeholder="Select">
          <el-option label="Sedentary" value="sedentary"></el-option>
          <el-option label="Lightly Active" value="lightly_active"></el-option>
          <el-option label="Moderately Active" value="moderately_active"></el-option>
          <el-option label="Very Active" value="very_active"></el-option>
          <el-option label="Extra Active" value="extra_active"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Goal">
        <el-select v-model="form.goal" placeholder="Select">
          <el-option label="Maintain Weight" value="maintain"></el-option>
          <el-option label="Lose Weight" value="lose_weight"></el-option>
          <el-option label="Gain Muscle" value="gain_muscle"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">Create</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import api from '../services/api'

const form = reactive({
  username: '',
  email: '',
  password: '',
  gender: '',
  birthdate: '',
  height_cm: 0,
  weight_kg: 0,
  activity_level: 'sedentary',
  goal: 'maintain'
})

const onSubmit = async () => {
  try {
    const response = await api.createUser(form)
    console.log(response.data)
    // Handle success (e.g., show a message, redirect)
  } catch (error) {
    console.error(error)
    // Handle error
  }
}
</script>
