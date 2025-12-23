<template>
  <el-container class="layout">
    <el-header class="header">
      <el-menu
        mode="horizontal"
        :router="true"
        class="menu"
        :ellipsis="false"
        :default-active="$route.path"
      >
        <el-menu-item index="/">首页</el-menu-item>

        <template v-if="isLoggedIn">
          <el-menu-item index="/food">食物追踪</el-menu-item>
          <el-menu-item index="/exercise">运动追踪</el-menu-item>
          <el-menu-item index="/summary">每日总结</el-menu-item>
          <el-menu-item index="/recommendations">菜单建议</el-menu-item>
        </template>

        <div class="flex-grow"></div>

        <template v-if="isLoggedIn">
          <el-menu-item index="/users/me" class="right-item">
            我的
          </el-menu-item>
          <el-menu-item @click="logout" class="right-item logout-btn">
            登出
          </el-menu-item>
        </template>
      </el-menu>
    </el-header>

    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isLoggedIn = ref(false)

const checkLoginStatus = () => {
  const token = localStorage.getItem('token')
  isLoggedIn.value = !!token
}

const logout = () => {
  localStorage.removeItem('token')
  isLoggedIn.value = false
  router.push('/login')
}

onMounted(() => {
  checkLoginStatus()
})

watch(() => route.path, () => {
  checkLoginStatus()
})
</script>

<style>
/* 1. 全局基础重置 */
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #F2F4F4;
}

#app {
  height: 100%;
}

.layout {
  height: 100vh;
}

/* 2. 导航栏容器 */
.header {
  padding: 0;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.menu {
  width: 100%;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e6e6e6 !important;
  /* 解决 Element Plus 默认蓝色变量 */
  --el-menu-active-color: #838B8B !important;
  --el-menu-hover-text-color: #838B8B !important;
  --el-menu-hover-bg-color: rgba(131, 139, 139, 0.05) !important;
}

/* 3. 布局占位 */
.flex-grow {
  flex-grow: 1;
}

/* 4. 菜单项样式定制 */
.el-menu--horizontal > .el-menu-item {
  color: #838B8B !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

/* 悬停状态 */
.el-menu--horizontal > .el-menu-item:hover {
  background-color: rgba(131, 139, 139, 0.05) !important;
  color: #838B8B !important;
}

/* 激活（选中）状态 */
.el-menu--horizontal > .el-menu-item.is-active {
  color: #838B8B !important;
  border-bottom: 2px solid #838B8B !important;
  background-color: transparent !important;
  font-weight: bold;
}

/* 消除点击后的蓝色聚焦框 */
.el-menu--horizontal > .el-menu-item:focus {
  background-color: transparent !important;
  color: #838B8B !important;
}

/* 右侧项微调 */
.right-item {
  padding: 0 15px;
}

/* 5. 主体内容区域 */
.main {
  padding: 20px;
  background-color: #F2F4F4;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

/* 滚动条美化 */
.main::-webkit-scrollbar {
  width: 6px;
}
.main::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 10px;
}
.main::-webkit-scrollbar-track {
  background: transparent;
}
</style>