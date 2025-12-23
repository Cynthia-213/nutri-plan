<template>
  <div class="register-container">
    <div>
      <h1>用户注册与个人信息</h1>
      <el-form :model="form" label-width="120px">
        <el-form-item label="用户名">
          <el-input v-model="form.username"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" v-model="form.password"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
            <el-radio label="unwilling_to_disclose">不愿透露</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker
            v-model="form.birthdate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
          />
        </el-form-item>

        <el-form-item label="身高 (cm)">
          <el-input-number v-model="form.height_cm" :min="1"></el-input-number>
        </el-form-item>
        <el-form-item label="体重 (kg)">
          <el-input-number v-model="form.weight_kg" :min="1"></el-input-number>
        </el-form-item>
        <el-form-item label="活动水平">
          <el-select v-model="form.activity_level" placeholder="选择">
            <el-option label="久坐" value="sedentary"></el-option>
            <el-option label="轻度活跃" value="lightly_active"></el-option>
            <el-option label="中度活跃" value="moderately_active"></el-option>
            <el-option label="非常活跃" value="very_active"></el-option>
            <el-option label="极度活跃" value="extra_active"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="目标">
          <el-select v-model="form.goal" placeholder="选择">
            <el-option label="维持身材" value="maintain"></el-option>
            <el-option label="减重" value="lose_weight"></el-option>
            <el-option label="增肌" value="gain_muscle"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit">创建</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
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

const router = useRouter()

const onSubmit = async () => {
  try {
    const response = await api.createUser(form)
    console.log(response.data)
    router.push('/login')
    // Handle success (e.g., show a message, redirect)
  } catch (error) {
    console.error(error)
    // Handle error
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%; /* Fill the parent container */
  padding: 20px; /* Add some padding around the content */
  box-sizing: border-box; /* Include padding in the element's total width and height */
}

.register-container > div {
  background: #fff; /* Optional: add a background to the content box */
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  max-width: 500px; /* Limit the width of the form for better readability */
  width: 100%; /* Ensure it's responsive */
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

/* Adjust form item spacing if needed */
.el-form-item {
  margin-bottom: 20px;
}
</style>
