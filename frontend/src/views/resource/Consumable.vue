<template>
  <div class="consumable-manage">
    <div class="page-header">
      <h2 class="page-title">耗材管理</h2>
    </div>

    <div class="search-form">
      <el-input v-model="searchParams.keyword" placeholder="搜索耗材编号/名称" style="width: 200px" />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增耗材
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="consumable_no" label="耗材编号" min-width="130" />
        <el-table-column prop="name" label="耗材名称" min-width="150" />
        <el-table-column prop="specification" label="规格" min-width="100" />
        <el-table-column prop="category" label="分类" min-width="100" />
        <el-table-column prop="quantity" label="库存" min-width="100">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.quantity <= row.warning_quantity }">
              {{ row.quantity }} {{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="存放位置" min-width="100" />
        <el-table-column prop="supplier" label="供应商" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleOperation(row, '入库')">入库</el-button>
            <el-button link type="primary" @click="handleOperation(row, '领用')">领用</el-button>
            <el-button link type="primary" @click="handleOperation(row, '退还')">退还</el-button>
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
    <el-dialog v-model="showDialog" title="新增耗材" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="耗材名称"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="规格型号"><el-input v-model="formData.specification" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="formData.category" style="width: 100%">
            <el-option label="玻璃器皿" value="玻璃器皿" />
            <el-option label="过滤耗材" value="过滤耗材" />
            <el-option label="防护用品" value="防护用品" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="库存数量"><el-input-number v-model="formData.quantity" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="formData.unit" style="width: 80px" /></el-form-item>
        <el-form-item label="预警数量"><el-input-number v-model="formData.warning_quantity" /></el-form-item>
        <el-form-item label="存放位置"><el-input v-model="formData.location" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConsumable">确定</el-button>
      </template>
    </el-dialog>

    <!-- 出入库弹窗 -->
    <el-dialog v-model="showOperationDialog" :title="operationType" width="400px">
      <el-form :model="operationForm" label-width="80px">
        <el-form-item label="数量"><el-input-number v-model="operationForm.quantity" :min="0.1" /></el-form-item>
        <el-form-item label="部门"><el-input v-model="operationForm.department" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="operationForm.remarks" type="textarea" /></el-form-item>
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

const loading = ref(false)
const tableData = ref([])
const showDialog = ref(false)
const showOperationDialog = ref(false)
const operationType = ref('入库')
const currentConsumable = ref(null)

const searchParams = reactive({ keyword: '' })
const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({
  name: '', specification: '', category: '',
  quantity: 0, unit: '个', warning_quantity: 10, location: ''
})

const operationForm = reactive({ quantity: 1, department: '', remarks: '' })

onMounted(() => { fetchData() })

async function fetchData() {
  loading.value = true
  try {
    const params = { skip: (pagination.page - 1) * 10, limit: 10, ...searchParams }
    const res = await api.get('/resources/consumables/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() { pagination.page = 1; fetchData() }

function handleAdd() {
  Object.assign(formData, {
    name: '', specification: '', category: '',
    quantity: 0, unit: '个', warning_quantity: 10, location: ''
  })
  showDialog.value = true
}

async function saveConsumable() {
  try {
    await api.post('/resources/consumables/', formData)
    ElMessage.success('添加成功')
    showDialog.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

function handleOperation(row, type) {
  currentConsumable.value = row
  operationType.value = type
  operationForm.quantity = 1
  operationForm.department = ''
  operationForm.remarks = ''
  showOperationDialog.value = true
}

async function confirmOperation() {
  try {
    await api.post(`/resources/consumables/${currentConsumable.value.id}/operation`, null, {
      params: {
        operation_type: operationType.value,
        quantity: operationForm.quantity,
        department: operationForm.department,
        remarks: operationForm.remarks
      }
    })
    ElMessage.success('操作成功')
    showOperationDialog.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}
</script>

<style lang="scss" scoped>
.consumable-manage {
  .low-stock { color: #fa8c16; font-weight: 500; }
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
}
</style>
