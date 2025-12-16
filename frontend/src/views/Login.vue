<template>
  <div>
    <h1>Login</h1>
    <el-form :model="form" label-width="120px" @submit.prevent="onSubmit">
      <el-form-item label="Username">
        <el-input v-model="form.username"></el-input>
      </el-form-item>
      <el-form-item label="Password">
        <el-input type="password" v-model="form.password"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit">Login</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const form = reactive({
  username: '',
  password: ''
})

const onSubmit = async () => {
  try {
    const formData = new FormData();
    formData.append('username', form.username);
    formData.append('password', form.password);

    const response = await api.login(formData)
    localStorage.setItem('token', response.data.access_token)
    router.push('/')
  } catch (error) {
    console.error(error)
    // Handle error
  }
}
</script>
