<template>
  <div class="permission-manage">
    <div class="page-header">
      <h2 class="page-title">权限管理</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <div class="page-card">
          <div class="card-header">
            <span>角色列表</span>
            <el-button type="primary" size="small" @click="handleAddRole">新增角色</el-button>
          </div>
          <el-menu :default-active="currentRole?.id?.toString()" @select="handleRoleSelect">
            <el-menu-item v-for="role in roles" :key="role.id" :index="role.id.toString()">
              <el-icon><UserFilled /></el-icon>
              <span>{{ role.name }}</span>
              <el-tag size="small" style="margin-left: auto">{{ role.code }}</el-tag>
            </el-menu-item>
          </el-menu>
        </div>
      </el-col>

      <el-col :span="16">
        <div class="page-card" v-if="currentRole">
          <div class="card-header">
            <span>{{ currentRole.name }} - 权限配置</span>
            <el-button type="primary" size="small" @click="handleSavePermissions">保存配置</el-button>
          </div>

          <el-tree
            ref="treeRef"
            :data="permissionTree"
            :props="{ label: 'name', children: 'children' }"
            show-checkbox
            node-key="id"
            default-expand-all
            :default-checked-keys="checkedPermissions"
          />
        </div>

        <el-empty v-else description="请从左侧选择角色" />
      </el-col>
    </el-row>

    <!-- 新增角色弹窗 -->
    <el-dialog v-model="showRoleDialog" title="新增角色" width="400px">
      <el-form :model="roleForm" label-width="80px">
        <el-form-item label="角色名称"><el-input v-model="roleForm.name" /></el-form-item>
        <el-form-item label="角色编码"><el-input v-model="roleForm.code" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="roleForm.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'

const roles = ref([])
const currentRole = ref(null)
const permissionTree = ref([])
const checkedPermissions = ref([])
const showRoleDialog = ref(false)
const treeRef = ref()

const roleForm = reactive({ name: '', code: '', description: '' })

onMounted(() => {
  fetchRoles()
  fetchPermissions()
})

async function fetchRoles() {
  try {
    const res = await api.get('/users/roles/')
    roles.value = res.data || []
    if (roles.value.length) {
      handleRoleSelect(roles.value[0].id.toString())
    }
  } catch (e) {}
}

async function fetchPermissions() {
  try {
    const res = await api.get('/users/permissions/')
    permissionTree.value = res.data.items || []
  } catch (e) {
    console.error('获取权限树失败', e)
  }
}

async function handleRoleSelect(roleId) {
  const role = roles.value.find(r => r.id === parseInt(roleId))
  currentRole.value = role
  // 获取角色权限
  try {
    const res = await api.get(`/users/roles/${role.id}/permissions`)
    checkedPermissions.value = res.data.items || []
    // 重新设置选中状态
    treeRef.value?.setCheckedKeys(checkedPermissions.value)
  } catch (e) {
    console.error('获取角色权限失败', e)
    checkedPermissions.value = []
    treeRef.value?.setCheckedKeys([])
  }
}

function handleAddRole() {
  roleForm.name = ''
  roleForm.code = ''
  roleForm.description = ''
  showRoleDialog.value = true
}

async function saveRole() {
  try {
    await api.post('/users/roles/', roleForm)
    ElMessage.success('角色创建成功')
    showRoleDialog.value = false
    fetchRoles()
  } catch (e) {
    ElMessage.error('角色创建失败')
  }
}

async function handleSavePermissions() {
  if (!currentRole.value) return
  const checkedKeys = treeRef.value?.getCheckedKeys() || []
  const halfCheckedKeys = treeRef.value?.getHalfCheckedKeys() || []
  const allChecked = [...checkedKeys, ...halfCheckedKeys]
  
  try {
    await api.put(`/users/roles/${currentRole.value.id}/permissions`, {
      permission_ids: allChecked
    })
    ElMessage.success('权限配置保存成功')
  } catch (e) {
    ElMessage.error('权限配置保存失败')
  }
}
</script>

<style lang="scss" scoped>
.permission-manage {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    font-weight: 600;
  }

  .el-menu {
    border: none;
  }
}
</style>
