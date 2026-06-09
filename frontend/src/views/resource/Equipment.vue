<template>
  <div class="equipment-manage">
    <div class="page-header">
      <h2 class="page-title">设备管理</h2>
    </div>

    <div class="search-form">
      <el-input v-model="searchParams.keyword" placeholder="搜索设备编号/名称" style="width: 200px" />
      <el-select v-model="searchParams.status" placeholder="状态" clearable style="width: 120px">
        <el-option label="正常" value="正常" />
        <el-option label="维修中" value="维修中" />
        <el-option label="报废" value="报废" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增设备
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="equipment_no" label="设备编号" min-width="130" />
        <el-table-column prop="name" label="设备名称" min-width="150" />
        <el-table-column prop="model" label="型号" min-width="120" />
        <el-table-column prop="manufacturer" label="生产厂家" min-width="150" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" min-width="100" />
        <el-table-column prop="location" label="存放位置" min-width="100" />
        <el-table-column prop="status" label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="next_calibration_date" label="下次校准" min-width="110">
          <template #default="{ row }">
            <span :class="{ 'calibration-due': isCalibrationDue(row.next_calibration_date) }">
              {{ formatDate(row.next_calibration_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="responsible_person" label="负责人" min-width="90" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleCalibration(row)">校准</el-button>
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

    <!-- 新增/校准弹窗 -->
    <el-dialog v-model="showDialog" :title="dialogTitle" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="设备名称"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="型号"><el-input v-model="formData.model" /></el-form-item>
        <el-form-item label="生产厂家"><el-input v-model="formData.manufacturer" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="formData.category" style="width: 100%">
            <el-option label="分析仪器" value="分析仪器" />
            <el-option label="称量设备" value="称量设备" />
            <el-option label="温控设备" value="温控设备" />
          </el-select>
        </el-form-item>
        <el-form-item label="存放位置"><el-input v-model="formData.location" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="formData.responsible_person" /></el-form-item>
        <template v-if="dialogTitle === '设备校准'">
          <el-divider />
          <el-form-item label="校准日期">
            <el-date-picker
              v-model="formData.calibration_date"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="下次校准">
            <el-date-picker
              v-model="formData.next_calibration_date"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="校准机构"><el-input v-model="formData.calibration_organization" /></el-form-item>
          <el-form-item label="校准结果">
            <el-select v-model="formData.calibration_result" style="width: 100%">
              <el-option label="合格" value="合格" />
              <el-option label="不合格" value="不合格" />
            </el-select>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEquipment">确定</el-button>
      </template>
    </el-dialog>
    <!-- 详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="设备详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="设备编号">{{ currentEquipment.equipment_no }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentEquipment.name }}</el-descriptions-item>
        <el-descriptions-item label="型号">{{ currentEquipment.model }}</el-descriptions-item>
        <el-descriptions-item label="生产厂家">{{ currentEquipment.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentEquipment.category }}</el-descriptions-item>
        <el-descriptions-item label="存放位置">{{ currentEquipment.location }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ currentEquipment.status }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ currentEquipment.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="下次校准日期">{{ formatDate(currentEquipment.next_calibration_date) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const showDialog = ref(false)
const showDetailDialog = ref(false)
const currentEquipment = ref({})
const dialogTitle = ref('新增设备')

const searchParams = reactive({ keyword: '', status: '' })
const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({
  id: null,
  name: '', model: '', manufacturer: '', category: '',
  location: '', responsible_person: '',
  calibration_date: null, next_calibration_date: null,
  calibration_organization: '', calibration_result: '合格'
})

onMounted(() => { fetchData() })

async function fetchData() {
  loading.value = true
  try {
    const params = { skip: (pagination.page - 1) * 10, limit: 10, ...searchParams }
    const res = await api.get('/resources/equipments/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() { pagination.page = 1; fetchData() }

function handleAdd() {
  dialogTitle.value = '新增设备'
  Object.assign(formData, {
    id: null, name: '', model: '', manufacturer: '', category: '',
    location: '', responsible_person: '',
    calibration_date: null, next_calibration_date: null,
    calibration_organization: '', calibration_result: '合格'
  })
  showDialog.value = true
}

function handleCalibration(row) {
  dialogTitle.value = '设备校准'
  formData.id = row.id
  formData.calibration_date = null
  formData.next_calibration_date = null
  formData.calibration_organization = ''
  formData.calibration_result = '合格'
  showDialog.value = true
}

function handleView(row) {
  currentEquipment.value = row
  showDetailDialog.value = true
}

async function saveEquipment() {
  try {
    if (dialogTitle.value === '设备校准') {
      await api.put(`/resources/equipments/${formData.id}/calibration`, null, {
        params: {
          calibration_date: formData.calibration_date,
          next_date: formData.next_calibration_date,
          organization: formData.calibration_organization,
          result: formData.calibration_result
        }
      })
    } else {
      await api.post('/resources/equipments/', formData)
    }
    ElMessage.success('操作成功')
    showDialog.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function getStatusType(status) {
  const map = { '正常': 'success', '维修中': 'warning', '报废': 'info' }
  return map[status] || 'info'
}

function isCalibrationDue(date) {
  if (!date) return false
  return dayjs(date).isBefore(dayjs().add(30, 'day'))
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-'
}
</script>

<style lang="scss" scoped>
.equipment-manage {
  .calibration-due { color: #fa8c16; font-weight: 500; }
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
}
</style>
