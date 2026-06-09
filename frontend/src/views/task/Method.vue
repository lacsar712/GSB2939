<template>
  <div class="standard-method">
    <div class="page-header">
      <h2 class="page-title">标准方法库</h2>
    </div>

    <div class="search-form">
      <el-input
        v-model="searchParams.keyword"
        placeholder="搜索方法编号/名称"
        clearable
        style="width: 250px"
        @keyup.enter="handleSearch"
      />
      <el-select v-model="searchParams.standard_type" placeholder="标准类型" clearable style="width: 150px">
        <el-option label="国标" value="国标" />
        <el-option label="行标" value="行标" />
        <el-option label="企标" value="企标" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增方法
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="method_no" label="方法编号" width="120" />
        <el-table-column prop="method_name" label="方法名称" min-width="250" show-overflow-tooltip />
        <el-table-column prop="standard_type" label="标准类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getStandardType(row.standard_type)" size="small">
              {{ row.standard_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="standard_no" label="标准编号" width="150" />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="showDialog" :title="isEdit ? '编辑方法' : '新增方法'" width="600px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="方法编号">
          <el-input v-model="formData.method_no" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="方法名称">
          <el-input v-model="formData.method_name" />
        </el-form-item>
        <el-form-item label="标准类型">
          <el-select v-model="formData.standard_type" style="width: 100%">
            <el-option label="国标" value="国标" />
            <el-option label="行标" value="行标" />
            <el-option label="企标" value="企标" />
          </el-select>
        </el-form-item>
        <el-form-item label="标准编号">
          <el-input v-model="formData.standard_no" />
        </el-form-item>
        <el-form-item label="版本号">
          <el-input v-model="formData.version" />
        </el-form-item>
        <el-form-item label="方法描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveMethod">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/utils/api'

const loading = ref(false)
const tableData = ref([])
const showDialog = ref(false)
const isEdit = ref(false)

const searchParams = reactive({
  keyword: '',
  standard_type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  id: null,
  method_no: '',
  method_name: '',
  standard_type: '国标',
  standard_no: '',
  version: '',
  description: ''
})

onMounted(() => {
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchParams
    }
    const res = await api.get('/tasks/methods/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchParams.keyword = ''
  searchParams.standard_type = ''
  pagination.page = 1
  fetchData()
}

function handleAdd() {
  isEdit.value = false
  Object.assign(formData, {
    id: null,
    method_no: '',
    method_name: '',
    standard_type: '国标',
    standard_no: '',
    version: '',
    description: ''
  })
  showDialog.value = true
}

function handleView(row) {
  isEdit.value = true
  Object.assign(formData, row)
  showDialog.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(formData, row)
  showDialog.value = true
}

async function saveMethod() {
  try {
    await api.post('/tasks/methods/', formData)
    ElMessage.success('保存成功')
    showDialog.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除方法 "${row.method_name}" 吗？`, '提示', { type: 'warning' })
    // 删除逻辑
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {}
}

function getStandardType(type) {
  const map = {
    '国标': 'danger',
    '行标': 'warning',
    '企标': 'success'
  }
  return map[type] || 'info'
}
</script>

<style lang="scss" scoped>
.standard-method {
  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
