<template>
  <el-container style="height: 100vh;">
    <el-header>
      <el-menu mode="horizontal" :router="true">
        <el-menu-item index="/">Home</el-menu-item>
        <el-menu-item index="/register">Register</el-menu-item>
        <el-menu-item index="/login">Login</el-menu-item>
        <el-menu-item index="/food">Food Tracker</el-menu-item>
        <el-menu-item index="/exercise">Exercise Tracker</el-menu-item>
        <el-menu-item index="/summary">Daily Summary</el-menu-item>
        <el-menu-item index="/recommendations">Menu Suggestion</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script setup>
</script>

<style>
body {
  margin: 0;
}
</style>
