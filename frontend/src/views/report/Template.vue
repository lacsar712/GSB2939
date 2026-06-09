<template>
  <div class="report-template">
    <div class="page-header">
      <h2 class="page-title">报告模板</h2>
    </div>

    <div class="search-form">
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增模板
        </el-button>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="template_no" label="模板编号" width="120" />
        <el-table-column prop="template_name" label="模板名称" min-width="200" />
        <el-table-column prop="template_type" label="模板类型" width="120" />
        <el-table-column prop="is_default" label="默认模板" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_default ? 'success' : 'info'" size="small">
              {{ row.is_default ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handlePreview(row)">预览</el-button>
            <el-button link type="primary" @click="handleSetDefault(row)" v-if="!row.is_default">
              设为默认
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="showDialog" :title="isEdit ? '编辑模板' : '新增模板'" width="600px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="模板编号"><el-input v-model="formData.template_no" /></el-form-item>
        <el-form-item label="模板名称"><el-input v-model="formData.template_name" /></el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="formData.template_type" style="width: 100%">
            <el-option label="食品类" value="食品类" />
            <el-option label="水质类" value="水质类" />
            <el-option label="环境类" value="环境类" />
          </el-select>
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="formData.is_default" />
        </el-form-item>
        <el-form-item label="模板内容">
          <div class="variable-tags" style="margin-bottom: 10px">
            <span class="label">插入变量：</span>
            <el-tag 
              v-for="item in variables" 
              :key="item.value" 
              class="variable-tag"
              @click="insertVariable(item.value)"
              style="margin-right: 8px; cursor: pointer"
            >
              {{ item.label }}
            </el-tag>
          </div>
          <el-input 
            ref="contentInput"
            v-model="formData.template_content" 
            type="textarea" 
            :rows="10" 
            placeholder="请输入模板内容，支持Markdown格式"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">确定</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showPreviewDialog" title="模板预览" width="800px">
      <div class="template-preview">
        <div class="template-header" v-if="currentTemplate.header_content">
          {{ currentTemplate.header_content }}
        </div>
        <div class="template-body">
          <div v-html="renderPreview(currentTemplate.template_content)"></div>
        </div>
        <div class="template-footer" v-if="currentTemplate.footer_content">
          {{ currentTemplate.footer_content }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const showDialog = ref(false)
const isEdit = ref(false)
const contentInput = ref(null)

const variables = [
  { label: '报告编号', value: '{report_no}' },
  { label: '样品名称', value: '{sample_name}' },
  { label: '样品编号', value: '{sample_no}' },
  { label: '客户名称', value: '{customer_name}' },
  { label: '检测项目', value: '{test_items}' },
  { label: '检测结论', value: '{conclusion}' },
  { label: '检测结果表', value: '{test_results_table}' },
  { label: '编制人', value: '{prepared_by}' },
  { label: '编制日期', value: '{prepared_at}' },
  { label: '签发人', value: '{issued_by}' },
  { label: '签发日期', value: '{issued_at}' },
]

const formData = reactive({
  id: null,
  template_no: '',
  template_name: '',
  template_type: '',
  is_default: false,
  template_content: ''
})

function insertVariable(val) {
  if (!contentInput.value) return
  const textarea = contentInput.value.textarea
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = formData.template_content || ''
  
  formData.template_content = text.substring(0, start) + val + text.substring(end)
  
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + val.length, start + val.length)
  })
}

function renderPreview(content) {
  if (!content) return ''
  let html = content
    .replace(/\n/g, '<br>')
    .replace('{report_no}', 'RP202310010001')
    .replace('{sample_name}', '生活饮用水')
    .replace('{sample_no}', 'S20231001001')
    .replace('{customer_name}', '某某自来水厂')
    .replace('{test_items}', 'pH值、浑浊度、余氯')
    .replace('{conclusion}', '合格')
    .replace('{prepared_by}', '张三')
    .replace('{prepared_at}', '2023-10-01')
    .replace('{issued_by}', '李四')
    .replace('{issued_at}', '2023-10-02')
  
  if (html.includes('{test_results_table}')) {
    html = html.replace('{test_results_table}', `
      <table border="1" style="width: 100%; border-collapse: collapse; margin: 10px 0;">
        <tr style="background: #f5f7fa;"><th>检测项目</th><th>标准要求</th><th>检测结果</th><th>单位</th><th>单项判定</th></tr>
        <tr><td>pH值</td><td>6.5-8.5</td><td>7.2</td><td>-</td><td>合格</td></tr>
        <tr><td>浑浊度</td><td>≤1</td><td>0.3</td><td>NTU</td><td>合格</td></tr>
        <tr><td>余氯</td><td>≥0.05</td><td>0.1</td><td>mg/L</td><td>合格</td></tr>
      </table>
    `)
  }
  
  return html
}

onMounted(() => { fetchData() })

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/reports/templates/')
    tableData.value = res.data.items || []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  Object.assign(formData, {
    id: null, template_no: '', template_name: '', template_type: '',
    is_default: false, template_content: ''
  })
  showDialog.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(formData, row)
  showDialog.value = true
}

const showPreviewDialog = ref(false)
const currentTemplate = ref({})

function handlePreview(row) {
  currentTemplate.value = row
  showPreviewDialog.value = true
}

async function handleSetDefault(row) {
  try {
    await api.put(`/reports/templates/${row.id}/default`)
    ElMessage.success('设置默认模板成功')
    fetchData()
  } catch (e) {
    ElMessage.error('设置失败')
  }
}

async function saveTemplate() {
  try {
    await api.post('/reports/templates/', formData)
    ElMessage.success('保存成功')
    showDialog.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.report-template {}
</style>
