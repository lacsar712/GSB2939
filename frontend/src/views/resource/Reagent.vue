<template>
  <div class="reagent-manage">
    <div class="page-header">
      <h2 class="page-title">试剂管理</h2>
    </div>

    <!-- 预警卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :span="8">
        <div class="warning-card low-stock">
          <el-icon :size="24"><Warning /></el-icon>
          <div>
            <span class="count">{{ warnings.low_stock?.length || 0 }}</span>
            <span class="label">库存不足</span>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="warning-card expired">
          <el-icon :size="24"><CircleClose /></el-icon>
          <div>
            <span class="count">{{ warnings.expired?.length || 0 }}</span>
            <span class="label">已过期</span>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="warning-card soon-expired">
          <el-icon :size="24"><Clock /></el-icon>
          <div>
            <span class="count">{{ warnings.soon_expired?.length || 0 }}</span>
            <span class="label">即将过期</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <div class="search-form">
      <el-input v-model="searchParams.keyword" placeholder="搜索试剂编号/名称" style="width: 200px" />
      <el-select v-model="searchParams.category" placeholder="分类" clearable style="width: 120px">
        <el-option label="酸类" value="酸类" />
        <el-option label="碱类" value="碱类" />
        <el-option label="有机溶剂" value="有机溶剂" />
        <el-option label="指示剂" value="指示剂" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleExport">导出Excel</el-button>
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增试剂
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="reagent_no" label="试剂编号" width="130" />
        <el-table-column prop="name" label="试剂名称" min-width="150" />
        <el-table-column prop="specification" label="规格" width="100" />
        <el-table-column prop="manufacturer" label="生产厂家" width="150" show-overflow-tooltip />
        <el-table-column prop="quantity" label="库存" width="100">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.quantity <= row.warning_quantity }">
              {{ row.quantity }} {{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="expiry_date" label="有效期" width="110">
          <template #default="{ row }">
            <span :class="{ 'expired': row.is_expired }">
              {{ formatDate(row.expiry_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="存放位置" width="100" />
        <el-table-column prop="is_expired" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_expired ? 'danger' : 'success'" size="small">
              {{ row.is_expired ? '过期' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleIn(row)">入库</el-button>
            <el-button link type="primary" @click="handleOut(row)">出库</el-button>
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

    <!-- 新增弹窗 -->
    <el-dialog v-model="showDialog" title="新增试剂" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="试剂名称"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="规格型号"><el-input v-model="formData.specification" /></el-form-item>
        <el-form-item label="生产厂家"><el-input v-model="formData.manufacturer" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="formData.category" style="width: 100%">
            <el-option label="酸类" value="酸类" />
            <el-option label="碱类" value="碱类" />
            <el-option label="有机溶剂" value="有机溶剂" />
          </el-select>
        </el-form-item>
        <el-form-item label="库存数量"><el-input-number v-model="formData.quantity" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="formData.unit" style="width: 80px" /></el-form-item>
        <el-form-item label="有效期">
          <el-date-picker
            v-model="formData.expiry_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="存放位置"><el-input v-model="formData.location" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveReagent">确定</el-button>
      </template>
    </el-dialog>

    <!-- 出入库弹窗 -->
    <el-dialog v-model="showOperationDialog" :title="operationType" width="400px">
      <el-form :model="operationForm" label-width="80px">
        <el-form-item label="数量">
          <el-input-number v-model="operationForm.quantity" :min="0.1" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="operationForm.remarks" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showOperationDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmOperation">确定</el-button>
      </template>
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
const showDialog = ref(false)
const showOperationDialog = ref(false)
const operationType = ref('入库')
const currentReagent = ref(null)
const warnings = ref({ low_stock: [], expired: [], soon_expired: [] })

const searchParams = reactive({ keyword: '', category: '' })
const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({
  name: '', specification: '', manufacturer: '', category: '',
  quantity: 0, unit: 'mL', expiry_date: null, location: ''
})

const operationForm = reactive({ quantity: 1, remarks: '' })

onMounted(() => {
  fetchData()
  fetchWarnings()
})

async function fetchData() {
  loading.value = true
  try {
    const params = { skip: (pagination.page - 1) * 10, limit: 10, ...searchParams }
    const res = await api.get('/resources/reagents/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchWarnings() {
  try {
    const res = await api.get('/resources/reagents/warning')
    warnings.value = res.data
  } catch (e) {}
}

function handleSearch() { pagination.page = 1; fetchData() }
function handleExport() {
  const columns = [
    { label: '试剂名称', prop: 'name' },
    { label: '规格', prop: 'specification' },
    { label: '生产厂家', prop: 'manufacturer' },
    { label: '分类', prop: 'category' },
    { label: '数量', prop: 'quantity' },
    { label: '单位', prop: 'unit' },
    { label: '有效期', prop: 'expiry_date', type: 'date' },
    { label: '存放位置', prop: 'location' }
  ]
  exportToCSV(tableData.value, columns, '试剂清单.csv')
}

function handleAdd() {
  Object.assign(formData, {
    name: '', specification: '', manufacturer: '', category: '',
    quantity: 0, unit: 'mL', expiry_date: null, location: ''
  })
  showDialog.value = true
}

async function saveReagent() {
  try {
    await api.post('/resources/reagents/', formData)
    ElMessage.success('添加成功')
    showDialog.value = false
    fetchData()
    fetchWarnings()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

function handleIn(row) {
  currentReagent.value = row
  operationType.value = '入库'
  operationForm.quantity = 1
  operationForm.remarks = ''
  showOperationDialog.value = true
}

function handleOut(row) {
  currentReagent.value = row
  operationType.value = '出库'
  operationForm.quantity = 1
  operationForm.remarks = ''
  showOperationDialog.value = true
}

async function confirmOperation() {
  try {
    const newQuantity = operationType.value === '入库'
      ? currentReagent.value.quantity + operationForm.quantity
      : currentReagent.value.quantity - operationForm.quantity
    
    if (newQuantity < 0) {
      ElMessage.warning('库存不足')
      return
    }
    
    await api.put(`/resources/reagents/${currentReagent.value.id}`, null, {
      params: { quantity: newQuantity }
    })
    ElMessage.success('操作成功')
    showOperationDialog.value = false
    fetchData()
    fetchWarnings()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-'
}
</script>

<style lang="scss" scoped>
.reagent-manage {
  .warning-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border-radius: 8px;
    
    &.low-stock { background: #fff7e6; color: #fa8c16; }
    &.expired { background: #fff1f0; color: #f5222d; }
    &.soon-expired { background: #e6f7ff; color: #1890ff; }
    
    .count { display: block; font-size: 24px; font-weight: bold; }
    .label { display: block; font-size: 13px; }
  }

  .low-stock { color: #fa8c16; font-weight: 500; }
  .expired { color: #f5222d; font-weight: 500; }

  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
}
</style>
