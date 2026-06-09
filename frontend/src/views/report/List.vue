<template>
  <div class="report-list">
    <div class="page-header">
      <h2 class="page-title">报告管理</h2>
    </div>

    <div class="search-form">
      <el-input v-model="searchParams.keyword" placeholder="搜索报告编号/样品名称" style="width: 200px" />
      <el-select v-model="searchParams.status" placeholder="报告状态" clearable style="width: 120px">
        <el-option label="待审核" value="待审核" />
        <el-option label="审核中" value="审核中" />
        <el-option label="已签发" value="已签发" />
        <el-option label="已退回" value="已退回" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon> 生成报告
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading" @row-click="handleView">
        <el-table-column prop="report_no" label="报告编号" min-width="150" />
        <el-table-column prop="sample_no" label="样品编号" min-width="150" />
        <el-table-column prop="sample_name" label="样品名称" min-width="150" />
        <el-table-column prop="customer_name" label="客户" min-width="120" />
        <el-table-column prop="test_items" label="检测项目" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="prepared_by_name" label="编制人" min-width="90" />
        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="handleView(row)">查看</el-button>
            <el-button link type="success" @click.stop="handleAudit(row)" v-if="row.status === '待审核'">
              审核
            </el-button>
            <el-button link type="primary" @click.stop="handlePrint(row)" v-if="row.status === '已签发'">
              打印
            </el-button>
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

    <!-- 审核弹窗 -->
    <el-dialog v-model="showAuditDialog" title="报告审核" width="500px">
      <el-form :model="auditForm" label-width="100px">
        <el-form-item label="审核结果">
          <el-radio-group v-model="auditForm.audit_result">
            <el-radio label="通过">通过</el-radio>
            <el-radio label="退回">退回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="auditForm.audit_opinion" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAuditDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAudit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const showAuditDialog = ref(false)
const currentReport = ref(null)

const searchParams = reactive({ keyword: '', status: '' })
const pagination = reactive({ page: 1, total: 0 })
const auditForm = reactive({ audit_level: 1, audit_result: '通过', audit_opinion: '' })

onMounted(() => { fetchData() })

async function fetchData() {
  loading.value = true
  try {
    const params = { skip: (pagination.page - 1) * 10, limit: 10, ...searchParams }
    const res = await api.get('/reports/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() { pagination.page = 1; fetchData() }

function handleCreate() {
  router.push('/task/list')
}

function handleView(row) {
  router.push(`/report/detail/${row.id}`)
}

function handleAudit(row) {
  currentReport.value = row
  auditForm.audit_result = '通过'
  auditForm.audit_opinion = ''
  showAuditDialog.value = true
}

async function submitAudit() {
  try {
    await api.post(`/reports/${currentReport.value.id}/audit`, {
      report_id: currentReport.value.id,
      ...auditForm
    })
    ElMessage.success('审核成功')
    showAuditDialog.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('审核失败')
  }
}

function handlePrint(row) {
  const routeData = router.resolve({
    path: `/report/detail/${row.id}`,
    query: { print: 'true' }
  })
  window.open(routeData.href, '_blank')
}

function getStatusType(status) {
  const map = { '待审核': 'warning', '审核中': 'primary', '已签发': 'success', '已退回': 'danger' }
  return map[status] || 'info'
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.report-list {
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
}
</style>
