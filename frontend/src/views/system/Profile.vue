<template>
  <div class="profile-container">
    <div class="page-header">
      <h2 class="page-title">个人中心</h2>
    </div>

    <div class="profile-card">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ userInfo.real_name }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ userInfo.email || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ userInfo.phone || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ userInfo.department || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="职位">{{ userInfo.position || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag v-for="role in (userInfo.roles || [])" :key="role" size="small" class="role-tag">
              {{ typeof role === 'object' ? role.name : role }}
            </el-tag>
            <span v-if="!userInfo.roles || userInfo.roles.length === 0">暂无角色</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="actions">
          <!-- Future: Add Edit Profile or Change Password buttons here -->
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
}
.page-title {
  font-size: 24px;
  font-weight: 500;
  color: #303133;
  margin: 0;
}
.profile-card {
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.role-tag {
  margin-right: 5px;
}
.actions {
  margin-top: 20px;
  text-align: right;
}
</style>
