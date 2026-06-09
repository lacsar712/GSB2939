<template>
  <div class="original-record">
    <div class="page-header">
      <h2 class="page-title">原始记录管理</h2>
    </div>

    <div class="search-form">
      <el-input v-model="searchParams.keyword" placeholder="搜索记录编号" style="width: 200px" />
      <el-select v-model="searchParams.status" placeholder="状态" clearable style="width: 120px">
        <el-option label="待审核" value="待审核" />
        <el-option label="已审核" value="已审核" />
        <el-option label="已退回" value="已退回" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="record_no" label="记录编号" width="150" />
        <el-table-column prop="sample_no" label="样品编号" width="150" />
        <el-table-column prop="sample_name" label="样品名称" min-width="150" />
        <el-table-column prop="test_items" label="检测项目" width="150" show-overflow-tooltip />
        <el-table-column prop="tester_name" label="检测人" width="100" />
        <el-table-column prop="test_date" label="检测日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.test_date, 'YYYY-MM-DD') }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="success" @click="handleReview(row)" v-if="row.status === '待审核'">
              审核
            </el-button>
            <el-button link type="primary" @click="handleExport(row)">导出</el-button>
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

    <!-- 查看详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="原始记录详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="记录编号">{{ currentRecord.record_no }}</el-descriptions-item>
        <el-descriptions-item label="样品编号">{{ currentRecord.sample_no }}</el-descriptions-item>
        <el-descriptions-item label="样品名称">{{ currentRecord.sample_name }}</el-descriptions-item>
        <el-descriptions-item label="检测项目">{{ currentRecord.test_items }}</el-descriptions-item>
        <el-descriptions-item label="检测人">{{ currentRecord.tester_name }}</el-descriptions-item>
        <el-descriptions-item label="检测日期">{{ formatDate(currentRecord.test_date) }}</el-descriptions-item>
        <el-descriptions-item label="记录内容" :span="2">
          <div class="record-content">{{ currentRecord.record_content || '暂无内容' }}</div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 审核弹窗 -->
    <el-dialog v-model="showReviewDialog" title="审核原始记录" width="500px">
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="审核结果">
          <el-radio-group v-model="reviewForm.approved">
            <el-radio :label="true">通过</el-radio>
            <el-radio :label="false">退回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="reviewForm.opinion" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" @click="submitReview">确定</el-button>
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
const showDetailDialog = ref(false)
const showReviewDialog = ref(false)
const currentRecord = ref({})

const searchParams = reactive({ keyword: '', status: '' })
const pagination = reactive({ page: 1, total: 0 })

const reviewForm = reactive({
  approved: true,
  opinion: ''
})

onMounted(() => { fetchData() })

async function fetchData() {
  loading.value = true
  try {
    const params = { skip: (pagination.page - 1) * 10, limit: 10, ...searchParams }
    const res = await api.get('/data/records/', { params })
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

function handleView(row) {
  currentRecord.value = row
  showDetailDialog.value = true
}

function handleReview(row) {
  currentRecord.value = row
  reviewForm.approved = true
  reviewForm.opinion = ''
  showReviewDialog.value = true
}

async function submitReview() {
  try {
    await api.put(`/data/records/${currentRecord.value.id}/review`, null, {
      params: { approved: reviewForm.approved, opinion: reviewForm.opinion }
    })
    ElMessage.success('审核完成')
    showReviewDialog.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('审核失败')
  }
}

function handleExport(row) {
  const columns = [
    { label: '记录编号', prop: 'record_no' },
    { label: '样品编号', prop: 'sample_no' },
    { label: '样品名称', prop: 'sample_name' },
    { label: '检测项目', prop: 'test_items' },
    { label: '检测人', prop: 'tester_name' },
    { label: '检测日期', prop: 'test_date', type: 'date' },
    { label: '状态', prop: 'status' }
  ]
  exportToCSV([row], columns, `原始记录_${row.record_no}.csv`)
}

function getStatusType(status) {
  const map = { '待审核': 'warning', '已审核': 'success', '已退回': 'danger' }
  return map[status] || 'info'
}

function formatDate(date, format = 'YYYY-MM-DD HH:mm') {
  return date ? dayjs(date).format(format) : '-'
}
</script>

<style lang="scss" scoped>
.original-record {
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
  .record-content { white-space: pre-wrap; line-height: 1.6; }
}
</style>
