import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  const permissions = ref(JSON.parse(localStorage.getItem('permissions') || '[]'))

  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => userInfo.value?.real_name || userInfo.value?.username || '')

  // 登录
  async function login(loginData) {
    try {
      const res = await api.post('/auth/login', loginData)
      const { access_token, user } = res.data
      
      token.value = access_token
      userInfo.value = user
      permissions.value = user.permissions || []
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('userInfo', JSON.stringify(user))
      localStorage.setItem('permissions', JSON.stringify(user.permissions || []))
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '登录失败'
      }
    }
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    permissions.value = []
    
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('permissions')
    
    router.push('/login')
  }

  // 初始化用户信息
  function initUser() {
    const savedToken = localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('userInfo')
    const savedPermissions = localStorage.getItem('permissions')
    
    if (savedToken) {
      token.value = savedToken
    }
    if (savedUserInfo) {
      userInfo.value = JSON.parse(savedUserInfo)
    }
    if (savedPermissions) {
      permissions.value = JSON.parse(savedPermissions)
    }
  }

  // 检查权限
  function hasPermission(code) {
    return permissions.value.some(p => p.code === code)
  }

  return {
    token,
    userInfo,
    permissions,
    isLoggedIn,
    userName,
    login,
    logout,
    initUser,
    hasPermission
  }
})
