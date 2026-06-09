<template>
  <div class="task-detail">
    <div class="page-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <div class="actions">
        <el-button type="primary" @click="handleStart" v-if="['已分配', '待接收'].includes(taskInfo.status)">
          接收任务
        </el-button>
        <el-button type="success" @click="handleComplete" v-if="taskInfo.status === '进行中'">
          完成任务
        </el-button>
        <el-button type="warning" @click="handlePause" v-if="taskInfo.status === '进行中'">
          暂停
        </el-button>
        <el-button type="primary" @click="handleResume" v-if="taskInfo.status === '已暂停'">
          恢复
        </el-button>
        <el-button type="info" @click="handleGenerateReport" v-if="taskInfo.status === '已完成'">
          生成报告
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 基本信息 -->
        <div class="page-card">
          <h3 class="card-title">任务信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="任务编号">{{ taskInfo.task_no }}</el-descriptions-item>
            <el-descriptions-item label="任务状态">
              <el-tag :type="getStatusType(taskInfo.status)">{{ taskInfo.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="样品编号">{{ taskInfo.sample_no }}</el-descriptions-item>
            <el-descriptions-item label="样品名称">{{ taskInfo.sample_name }}</el-descriptions-item>
            <el-descriptions-item label="检测项目">{{ taskInfo.test_items }}</el-descriptions-item>
            <el-descriptions-item label="优先级">
              <el-tag :type="taskInfo.priority === '紧急' ? 'danger' : 'info'">
                {{ taskInfo.priority }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="检测科室">{{ taskInfo.department }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ taskInfo.assignee_name }}</el-descriptions-item>
            <el-descriptions-item label="截止日期">{{ formatDate(taskInfo.deadline) }}</el-descriptions-item>
            <el-descriptions-item label="任务进度">
              <el-progress :percentage="taskInfo.progress" />
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 进度时间线 -->
        <div class="page-card">
          <h3 class="card-title">进度跟踪</h3>
          <el-steps :active="getStepActive()" align-center>
            <el-step title="待分配" :description="taskInfo.status === '待分配' ? '当前' : ''" />
            <el-step title="已分配" :description="taskInfo.status === '已分配' ? '当前' : ''" />
            <el-step title="进行中" :description="taskInfo.status === '进行中' ? '当前' : ''" />
            <el-step title="已完成" :description="taskInfo.status === '已完成' ? '当前' : ''" />
          </el-steps>
        </div>

        <!-- 检测数据 -->
        <div class="page-card">
          <div class="card-header">
            <h3 class="card-title">检测数据</h3>
            <el-button type="primary" size="small" @click="handleAddData">
              <el-icon><Plus /></el-icon> 添加数据
            </el-button>
          </div>
          <el-table :data="detectionData" stripe>
            <el-table-column prop="item_name" label="检测项目" />
            <el-table-column prop="result_value" label="结果值" width="100">
              <template #default="{ row }">
                {{ row.result_value }} {{ row.result_unit }}
              </template>
        </el-table-column>
            <el-table-column prop="standard_value" label="标准值" width="100" />
            <el-table-column prop="is_qualified" label="是否合格" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_qualified ? 'success' : 'danger'" size="small">
                  {{ row.is_qualified ? '合格' : '不合格' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="test_date" label="检测日期" width="160">
              <template #default="{ row }">
                {{ formatDate(row.test_date) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <el-col :span="8">
        <!-- 标准方法 -->
        <div class="page-card">
          <h3 class="card-title">标准方法</h3>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="方法编号">{{ methodInfo.method_no }}</el-descriptions-item>
            <el-descriptions-item label="方法名称">{{ methodInfo.method_name }}</el-descriptions-item>
            <el-descriptions-item label="标准编号">{{ methodInfo.standard_no }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 关联样品 -->
        <div class="page-card">
          <h3 class="card-title">关联样品</h3>
          <div class="sample-link" @click="$router.push(`/sample/detail/${taskInfo.sample_id}`)">
            <el-icon><Box /></el-icon>
            <div class="sample-info">
              <p class="sample-no">{{ taskInfo.sample_no }}</p>
              <p class="sample-name">{{ taskInfo.sample_name }}</p>
            </div>
          </div>
        </div>

        <!-- 操作记录 -->
        <div class="page-card">
          <h3 class="card-title">操作记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="item in assignments"
              :key="item.id"
              :timestamp="formatDate(item.assigned_at)"
              placement="top"
            >
              <p>{{ item.status }}</p>
              <p v-if="item.user_name">负责人：{{ item.user_name }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
    </el-row>

    <!-- 添加数据弹窗 -->
    <el-dialog v-model="showDataDialog" title="添加检测数据" width="500px">
      <el-form :model="dataForm" label-width="100px">
        <el-form-item label="检测项目">
          <el-select
            v-model="dataForm.item_name"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入检测项目"
            style="width: 100%"
          >
            <el-option
              v-for="item in testItemOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="结果值">
          <el-input-number v-model="dataForm.result_value" :precision="4" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="dataForm.result_unit" style="width: 100px" />
        </el-form-item>
        <el-form-item label="标准值">
          <el-input v-model="dataForm.standard_value" />
        </el-form-item>
        <el-form-item label="是否合格">
          <el-radio-group v-model="dataForm.is_qualified">
            <el-radio :label="true">合格</el-radio>
            <el-radio :label="false">不合格</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDataDialog = false">取消</el-button>
        <el-button type="primary" @click="saveData">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReportDialog" title="生成报告" width="400px">
      <el-form label-width="80px">
        <el-form-item label="选择模板">
          <el-select v-model="selectedTemplateId" placeholder="请选择报告模板" style="width: 100%">
            <el-option
              v-for="item in templates"
              :key="item.id"
              :label="item.template_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmGenerateReport">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const taskInfo = ref({})
const methodInfo = ref({})
const assignments = ref([])
const detectionData = ref([])
const showDataDialog = ref(false)
const showReportDialog = ref(false)
const templates = ref([])
const selectedTemplateId = ref(null)

const dataForm = reactive({
  task_id: 0,
  sample_id: 0,
  item_name: '',
  result_value: 0,
  result_unit: '',
  standard_value: '',
  is_qualified: true
})

const testItemOptions = computed(() => {
  if (!taskInfo.value.test_items) return []
  return taskInfo.value.test_items.split(/[,，、]/).map(s => s.trim()).filter(s => s)
})

onMounted(() => {
  fetchTaskDetail()
})

async function fetchTaskDetail() {
  try {
    const res = await api.get(`/tasks/${route.params.id}`)
    taskInfo.value = res.data.task || {}
    assignments.value = res.data.assignments || []
    
    // 获取标准方法
    if (taskInfo.value.standard_method_id) {
      try {
        const methodRes = await api.get(`/tasks/methods/${taskInfo.value.standard_method_id}`)
        methodInfo.value = methodRes.data || {}
      } catch (e) {
        console.error('获取标准方法详情失败', e)
      }
    }
    
    // 获取检测数据
    const dataRes = await api.get('/data/detection/', { params: { task_id: route.params.id } })
    detectionData.value = dataRes.data.items || []
    
    dataForm.task_id = taskInfo.value.id
    dataForm.sample_id = taskInfo.value.sample_id
  } catch (e) {
    ElMessage.error('获取任务详情失败')
  }
}

async function handleStart() {
  try {
    const waitingAssignment = assignments.value.find(item => item.status === '待接收')
    if (waitingAssignment) {
      await api.post(`/tasks/assignments/${waitingAssignment.id}/accept`)
    } else {
      await api.put(`/tasks/${taskInfo.value.id}`, { status: '进行中' })
    }
    ElMessage.success('任务已接收')
    fetchTaskDetail()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleComplete() {
  try {
    await api.put(`/tasks/${taskInfo.value.id}`, { status: '已完成', progress: 100 })
    ElMessage.success('任务已完成')
    fetchTaskDetail()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handlePause() {
  try {
    await api.put(`/tasks/${taskInfo.value.id}`, { status: '已暂停' })
    ElMessage.success('任务已暂停')
    fetchTaskDetail()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleResume() {
  try {
    await api.put(`/tasks/${taskInfo.value.id}`, { status: '进行中' })
    ElMessage.success('任务已恢复')
    fetchTaskDetail()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function handleAddData() {
  dataForm.item_name = ''
  dataForm.result_value = 0
  dataForm.result_unit = ''
  dataForm.standard_value = ''
  dataForm.is_qualified = true
  showDataDialog.value = true
}

async function saveData() {
  try {
    const postData = {
      ...dataForm,
      task_id: taskInfo.value.id,
      sample_id: taskInfo.value.sample_id
    }
    await api.post('/data/detection/', postData)
    ElMessage.success('保存成功')
    showDataDialog.value = false
    fetchTaskDetail()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function handleGenerateReport() {
  try {
    const res = await api.get('/reports/templates/')
    templates.value = res.data.items || []
    if (templates.value.length > 0) {
      const defaultTpl = templates.value.find(t => t.is_default)
      selectedTemplateId.value = defaultTpl ? defaultTpl.id : templates.value[0].id
    }
    showReportDialog.value = true
  } catch (e) {
    ElMessage.error('获取模板列表失败')
  }
}

async function confirmGenerateReport() {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请选择模板')
    return
  }
  try {
    const res = await api.post('/reports/generate', {
      task_id: taskInfo.value.id,
      template_id: selectedTemplateId.value
    })
    ElMessage.success('报告生成成功')
    showReportDialog.value = false
    router.push(`/report/detail/${res.data.id}`)
  } catch (e) {
    ElMessage.error('生成报告失败')
  }
}

function getStepActive() {
  const map = { '待分配': 1, '已分配': 2, '进行中': 3, '已完成': 4 }
  return map[taskInfo.value.status] || 0
}

function getStatusType(status) {
  const map = { '待分配': 'info', '已分配': 'primary', '进行中': 'warning', '已完成': 'success', '已暂停': 'danger' }
  return map[status] || 'info'
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.task-detail {
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

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .card-title {
      margin: 0;
    }
  }

  .sample-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: #ecf5ff;
    }

    .sample-info {
      .sample-no {
        margin: 0;
        font-size: 14px;
        color: #409eff;
      }
      .sample-name {
        margin: 4px 0 0;
        font-size: 13px;
        color: #606266;
      }
    }
  }
}
</style>
