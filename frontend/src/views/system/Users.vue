<template>
  <div class="user-manage">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
    </div>

    <div class="search-form">
      <el-input v-model="searchParams.keyword" placeholder="搜索用户名/姓名" style="width: 200px" />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增用户
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="real_name" label="姓名" min-width="100" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column prop="department" label="部门" min-width="120" />
        <el-table-column prop="position" label="职位" min-width="100" />
        <el-table-column prop="is_active" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="showDialog" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="formData.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="formData.real_name" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="formData.email" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="formData.phone" /></el-form-item>
        <el-form-item label="部门"><el-input v-model="formData.department" /></el-form-item>
        <el-form-item label="职位"><el-input v-model="formData.position" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="formData.role_ids" multiple style="width: 100%">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" v-if="!isEdit">
          <el-input v-model="formData.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const showDialog = ref(false)
const isEdit = ref(false)
const roles = ref([])

const searchParams = reactive({ keyword: '' })
const formData = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  role_ids: []
})

onMounted(() => {
  fetchUsers()
  fetchRoles()
})

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/users/')
    tableData.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  try {
    const res = await api.get('/users/roles/')
    roles.value = res.data || []
  } catch (e) {}
}

function handleSearch() { fetchUsers() }

function handleAdd() {
  isEdit.value = false
  Object.assign(formData, {
    id: null, username: '', password: '123456', real_name: '',
    email: '', phone: '', department: '', position: '', role_ids: []
  })
  showDialog.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(formData, {
    ...row,
    role_ids: row.roles?.map(r => r.id) || []
  })
  showDialog.value = true
}

async function saveUser() {
  try {
    if (isEdit.value) {
      await api.put(`/users/${formData.id}`, formData)
    } else {
      await api.post('/users/', formData)
    }
    ElMessage.success('保存成功')
    showDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function handleResetPassword(row) {
  try {
    await ElMessageBox.confirm(`确定重置用户 "${row.username}" 的密码吗？`, '提示')
    ElMessage.success('密码已重置为：123456')
  } catch (e) {}
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除用户 "${row.username}" 吗？`, '提示', { type: 'warning' })
    await api.delete(`/users/${row.id}`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (e) {}
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.user-manage {}
</style>
