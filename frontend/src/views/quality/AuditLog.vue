<template>
  <div class="audit-log">
    <div class="page-header">
      <h2 class="page-title">审计追踪日志</h2>
    </div>

    <div class="search-form">
      <el-input v-model="searchParams.user_name" placeholder="操作人" style="width: 150px" />
      <el-select v-model="searchParams.operation_type" placeholder="操作类型" clearable style="width: 130px">
        <el-option v-for="item in operationTypes" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="searchParams.operation_module" placeholder="操作模块" clearable style="width: 130px">
        <el-option v-for="item in modules" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="-"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width: 240px"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleExport">导出</el-button>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="user_name" label="操作人" min-width="100" />
        <el-table-column prop="operation_type" label="操作类型" min-width="100" />
        <el-table-column prop="operation_module" label="操作模块" min-width="100" />
        <el-table-column prop="operation_content" label="操作内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" min-width="120" />
        <el-table-column prop="created_at" label="操作时间" min-width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="操作详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="操作人">{{ currentLog.user_name }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">{{ currentLog.operation_type }}</el-descriptions-item>
        <el-descriptions-item label="操作模块">{{ currentLog.operation_module }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip_address }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ formatDate(currentLog.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ currentLog.request_method }}</el-descriptions-item>
        <el-descriptions-item label="请求URL" :span="2">{{ currentLog.request_url }}</el-descriptions-item>
        <el-descriptions-item label="操作内容" :span="2">{{ currentLog.operation_content }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

import { exportToCSV } from '@/utils/export'

const loading = ref(false)
const tableData = ref([])
const showDetailDialog = ref(false)
const currentLog = ref({})
const dateRange = ref([])

const searchParams = reactive({ user_name: '', operation_type: '', operation_module: '' })
const pagination = reactive({ page: 1, total: 0 })

const operationTypes = ref([
  { value: '登录', label: '登录' },
  { value: '新增', label: '新增' },
  { value: '修改', label: '修改' },
  { value: '删除', label: '删除' },
  { value: '审核', label: '审核' }
])

const modules = ref([
  { value: '样品管理', label: '样品管理' },
  { value: '任务管理', label: '任务管理' },
  { value: '报告管理', label: '报告管理' },
  { value: '用户管理', label: '用户管理' }
])

onMounted(() => { fetchData(); fetchOptions() })

async function fetchData() {
  loading.value = true
  try {
    const params = { skip: (pagination.page - 1) * 10, limit: 10, ...searchParams }
    const res = await api.get('/audit/logs/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchOptions() {
  try {
    const [typesRes, modulesRes] = await Promise.all([
      api.get('/audit/operation-types/'),
      api.get('/audit/modules/')
    ])
    operationTypes.value = typesRes.data.items || operationTypes.value
    modules.value = modulesRes.data.items || modules.value
  } catch (e) {}
}

function handleSearch() { pagination.page = 1; fetchData() }
function handleExport() {
  const columns = [
    { label: '操作人', prop: 'user_name' },
    { label: '操作类型', prop: 'operation_type' },
    { label: '操作模块', prop: 'operation_module' },
    { label: '操作内容', prop: 'operation_content' },
    { label: 'IP地址', prop: 'ip_address' },
    { label: '操作时间', prop: 'created_at', type: 'datetime' }
  ]
  exportToCSV(tableData.value, columns, '审计日志.csv')
}

function handleView(row) {
  currentLog.value = row
  showDetailDialog.value = true
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}
</script>

<style lang="scss" scoped>
.audit-log {
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
}
</style>
