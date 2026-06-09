<template>
  <div class="report-detail">
    <div class="page-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <div class="actions">
        <el-button type="primary" @click="handlePrint" v-if="reportInfo.status === '已签发'">
          <el-icon><Printer /></el-icon> 打印报告
        </el-button>
        <el-button @click="handleExport" v-if="reportInfo.status === '已签发'">
          <el-icon><Download /></el-icon> 导出PDF
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16" class="print-area">
        <div class="page-card report-content" v-if="templateInfo && templateInfo.template_content">
           <div class="custom-report">
             <div class="report-header" v-if="templateInfo.header_content">{{ templateInfo.header_content }}</div>
             <div class="report-body" v-html="renderReportContent()"></div>
             <div class="report-footer" v-if="templateInfo.footer_content">{{ templateInfo.footer_content }}</div>
           </div>
        </div>

        <div class="page-card report-content" v-else>
          <div class="report-header">
            <h1>检测报告</h1>
            <p class="report-no">{{ reportInfo.report_no }}</p>
          </div>

          <el-divider />

          <el-descriptions :column="2" border>
            <el-descriptions-item label="样品名称">{{ reportInfo.sample_name }}</el-descriptions-item>
            <el-descriptions-item label="样品编号">{{ reportInfo.sample_no }}</el-descriptions-item>
            <el-descriptions-item label="客户名称">{{ reportInfo.customer_name }}</el-descriptions-item>
            <el-descriptions-item label="报告状态">
              <el-tag :type="getStatusType(reportInfo.status)">{{ reportInfo.status }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <h3 style="margin: 20px 0 16px">检测结果</h3>
          <el-table :data="testResults" stripe border>
            <el-table-column prop="item" label="检测项目" />
            <el-table-column prop="result" label="检测结果" />
            <el-table-column prop="standard" label="标准限值" />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="qualified" label="判定" width="80">
              <template #default="{ row }">
                <el-tag :type="row.qualified ? 'success' : 'danger'" size="small">
                  {{ row.qualified ? '合格' : '不合格' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <h3 style="margin: 20px 0 16px">检测结论</h3>
          <div class="conclusion">
            {{ reportInfo.conclusion || '该样品所检项目符合标准要求。' }}
          </div>

          <div class="signatures" style="margin-top: 40px">
            <el-row :gutter="40">
              <el-col :span="8">
                <div class="signature-item">
                  <span>检测人：</span>
                  <div class="signature-line"></div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="signature-item">
                  <span>审核人：</span>
                  <div class="signature-line"></div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="signature-item">
                  <span>批准人：</span>
                  <div class="signature-line"></div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-col>

      <el-col :span="8" class="no-print">
        <!-- 审核记录 -->
        <div class="page-card">
          <h3 class="card-title">审核记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="item in audits"
              :key="item.id"
              :type="item.audit_result === '通过' ? 'success' : 'danger'"
              :timestamp="formatDate(item.audited_at)"
            >
              <p><strong>{{ item.auditor_name }}</strong> - {{ item.audit_result }}</p>
              <p v-if="item.audit_opinion">{{ item.audit_opinion }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 基本信息 -->
        <div class="page-card">
          <h3 class="card-title">基本信息</h3>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="编制人">{{ reportInfo.prepared_by_name }}</el-descriptions-item>
            <el-descriptions-item label="编制日期">{{ formatDate(reportInfo.prepared_at) }}</el-descriptions-item>
            <el-descriptions-item label="签发人">{{ reportInfo.issued_by_name }}</el-descriptions-item>
            <el-descriptions-item label="签发日期">{{ formatDate(reportInfo.issued_at) }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const route = useRoute()
const reportInfo = ref({})
const audits = ref([])
const testResults = ref([])
const templateInfo = ref(null)

onMounted(() => { fetchDetail() })

async function fetchDetail() {
  try {
    const res = await api.get(`/reports/${route.params.id}`)
    reportInfo.value = res.data.report || {}
    audits.value = res.data.audits || []
    
    if (reportInfo.value.template_id) {
      try {
        const tplRes = await api.get(`/reports/templates/${reportInfo.value.template_id}`)
        templateInfo.value = tplRes.data || {}
      } catch (e) {
        console.error('Fetch template failed', e)
      }
    }

    // 获取检测数据
    if (reportInfo.value.task_id) {
      const dataRes = await api.get('/data/detection/', { params: { task_id: reportInfo.value.task_id } })
      testResults.value = (dataRes.data.items || []).map(item => ({
        item: item.item_name,
        result: item.result_value,
        standard: item.standard_value,
        unit: item.result_unit,
        qualified: item.is_qualified
      }))
    }

    // 自动打印
    if (route.query.print === 'true') {
      setTimeout(() => {
        window.print()
      }, 500)
    }
  } catch (e) {
    ElMessage.error('获取报告详情失败')
  }
}

function renderReportContent() {
  if (!templateInfo.value || !templateInfo.value.template_content) return ''
  let content = templateInfo.value.template_content
  const data = reportInfo.value
  
  const map = {
    '{report_no}': data.report_no,
    '{sample_name}': data.sample_name,
    '{sample_no}': data.sample_no,
    '{customer_name}': data.customer_name,
    '{test_items}': data.test_items,
    '{conclusion}': data.conclusion,
    '{prepared_by}': data.prepared_by_name,
    '{prepared_at}': formatDate(data.prepared_at),
    '{issued_by}': data.issued_by_name,
    '{issued_at}': formatDate(data.issued_at)
  }
  
  for (const key in map) {
    const val = map[key]
    content = content.replace(new RegExp(key, 'g'), val || '')
  }
  
  if (content.includes('{test_results_table}')) {
    let tableHtml = `<table style="width:100%; border-collapse: collapse; border: 1px solid #dcdfe6; margin: 20px 0;">
      <thead style="background: #f5f7fa;">
        <tr>
          <th style="padding: 10px; border: 1px solid #dcdfe6;">检测项目</th>
          <th style="padding: 10px; border: 1px solid #dcdfe6;">结果</th>
          <th style="padding: 10px; border: 1px solid #dcdfe6;">单位</th>
          <th style="padding: 10px; border: 1px solid #dcdfe6;">标准</th>
          <th style="padding: 10px; border: 1px solid #dcdfe6;">判定</th>
        </tr>
      </thead>
      <tbody>`
      
    testResults.value.forEach(row => {
      tableHtml += `<tr>
        <td style="padding: 8px; border: 1px solid #dcdfe6;">${row.item}</td>
        <td style="padding: 8px; border: 1px solid #dcdfe6;">${row.result}</td>
        <td style="padding: 8px; border: 1px solid #dcdfe6;">${row.unit || '-'}</td>
        <td style="padding: 8px; border: 1px solid #dcdfe6;">${row.standard || '-'}</td>
        <td style="padding: 8px; border: 1px solid #dcdfe6;">
          <span style="color: ${row.qualified ? '#67c23a' : '#f56c6c'}">${row.qualified ? '合格' : '不合格'}</span>
        </td>
      </tr>`
    })
    tableHtml += `</tbody></table>`
    content = content.replace('{test_results_table}', tableHtml)
  }
  
  return content.replace(/\n/g, '<br>')
}

function handlePrint() {
  window.print()
}

function handleExport() {
  window.print()
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
@media print {
  .page-header, .no-print {
    display: none !important;
  }
  .print-area {
    width: 100% !important;
    max-width: 100% !important;
    flex: 0 0 100% !important;
  }
  .report-detail {
    padding: 0;
  }
  .page-card {
    box-shadow: none !important;
    border: none !important;
    margin-bottom: 0;
  }
}

.report-detail {
  .page-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
  }

  .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
  }

  .report-content {
    .report-header {
      text-align: center;
      padding: 20px 0;
      
      h1 { margin: 0 0 10px; color: #303133; }
      .report-no { color: #909399; margin: 0; }
    }

    .conclusion {
      background: #f5f7fa;
      padding: 16px;
      border-radius: 8px;
      line-height: 1.8;
    }

    .signature-item {
      .signature-line {
        height: 40px;
        border-bottom: 1px solid #dcdfe6;
        margin-top: 8px;
      }
    }
  }
}
</style>
