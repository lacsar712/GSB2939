<template>
  <div class="sample-list">
    <div class="page-header">
      <h2 class="page-title">样品列表</h2>
    </div>

    <!-- 搜索表单 -->
    <div class="search-form">
      <el-input
        v-model="searchParams.keyword"
        placeholder="搜索样品编号/名称/客户"
        clearable
        style="width: 250px"
        @keyup.enter="handleSearch"
      />
      <el-select v-model="searchParams.status" placeholder="状态" clearable style="width: 150px">
        <el-option label="已登记" value="已登记" />
        <el-option label="检测中" value="检测中" />
        <el-option label="检测完成" value="检测完成" />
        <el-option label="已归档" value="已归档" />
      </el-select>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon> 搜索
      </el-button>
      <el-button @click="handleReset">重置</el-button>
      
      <div style="flex: 1; display: flex; justify-content: flex-end; align-items: center">
        <el-button type="primary" @click="$router.push('/sample/register')">
          <el-icon><Plus /></el-icon> 新增样品
        </el-button>
        <el-upload
          class="import-uploader"
          action="#"
          :http-request="handleImport"
          :show-file-list="false"
          accept=".xlsx,.xls"
          style="margin-left: 12px"
        >
          <el-button type="warning">
            <el-icon><Upload /></el-icon> 导入样品
          </el-button>
        </el-upload>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="page-card">
      <el-table
        :data="tableData"
        stripe
        v-loading="loading"
        @row-click="handleRowClick"
        style="cursor: pointer"
      >
        <el-table-column prop="sample_no" label="样品编号" min-width="150" />
        <el-table-column prop="name" label="样品名称" min-width="150" />
        <el-table-column prop="type" label="类型" min-width="100" />
        <el-table-column prop="customer_name" label="客户" min-width="120" />
        <el-table-column prop="quantity" label="数量" min-width="100">
          <template #default="{ row }">
            {{ row.quantity }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="登记时间" min-width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="handleView(row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button link type="primary" @click.stop="handlePrint(row)">
              <el-icon><Printer /></el-icon> 打印
            </el-button>
            <el-button link type="danger" @click.stop="handleDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 打印标签弹窗 -->
    <el-dialog v-model="printVisible" title="打印样品标签" width="360px" align-center destroy-on-close>
      <div style="display: flex; justify-content: center;">
        <SampleLabel :sample="currentSample" v-if="currentSample" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'
import SampleLabel from '@/components/SampleLabel.vue'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const printVisible = ref(false)
const currentSample = ref(null)

const searchParams = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
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
    const res = await api.get('/samples/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error('获取数据失败', error)
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
  searchParams.status = ''
  pagination.page = 1
  fetchData()
}

function handleRowClick(row) {
  router.push(`/sample/detail/${row.id}`)
}

function handleView(row) {
  router.push(`/sample/detail/${row.id}`)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除样品 "${row.sample_no}" 吗？`, '提示', {
      type: 'warning'
    })
    await api.delete(`/samples/${row.id}`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleImport(options) {
  const formData = new FormData()
  formData.append('file', options.file)
  
  try {
    loading.value = true
    const res = await api.post('/samples/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(`成功导入 ${res.data.count} 条数据`)
    fetchData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
    loading.value = false
  }
}

function handlePrint(row) {
  currentSample.value = row
  printVisible.value = true
}

function getStatusType(status) {
  const map = {
    '已登记': 'success',
    '检测中': 'primary',
    '检测完成': 'info',
    '已归档': 'info'
  }
  return map[status] || 'info'
}

function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}
</script>

<style lang="scss" scoped>
.sample-list {
  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
