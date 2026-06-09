<template>
  <div class="role-manage">
    <div class="page-header">
      <h2 class="page-title">角色管理</h2>
    </div>

    <div class="search-form">
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增角色
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="name" label="角色名称" min-width="150" />
        <el-table-column prop="code" label="角色编码" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handlePermission(row)">权限配置</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="showDialog" :title="isEdit ? '编辑角色' : '新增角色'" width="400px">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="角色名称"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="角色编码"><el-input v-model="formData.code" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="formData.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const showDialog = ref(false)
const isEdit = ref(false)

const formData = reactive({
  id: null,
  name: '',
  code: '',
  description: ''
})

onMounted(() => { fetchRoles() })

async function fetchRoles() {
  loading.value = true
  try {
    const res = await api.get('/users/roles/')
    tableData.value = res.data || []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  Object.assign(formData, { id: null, name: '', code: '', description: '' })
  showDialog.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(formData, row)
  showDialog.value = true
}

function handlePermission(row) {
  router.push('/quality/permission')
}

async function saveRole() {
  ElMessage.success('保存成功')
  showDialog.value = false
  fetchRoles()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除角色 "${row.name}" 吗？`, '提示', { type: 'warning' })
    ElMessage.success('删除成功')
    fetchRoles()
  } catch (e) {}
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.role-manage {}
</style>
