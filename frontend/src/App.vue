<template>
  <router-view />
</template>

<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 初始化时检查登录状态
if (localStorage.getItem('token')) {
  userStore.initUser()
}
</script>

<style>
#app {
  width: 100%;
  height: 100%;
}
</style>
