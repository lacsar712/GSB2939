<template>
  <div class="task-list">
    <div class="page-header">
      <h2 class="page-title">任务列表</h2>
    </div>

    <!-- 搜索表单 -->
    <div class="search-form">
      <el-input
        v-model="searchParams.keyword"
        placeholder="搜索任务编号/样品名称"
        clearable
        style="width: 200px"
        @keyup.enter="handleSearch"
      />
      <el-select v-model="searchParams.status" placeholder="任务状态" clearable style="width: 140px">
        <el-option label="待分配" value="待分配" />
        <el-option label="已分配" value="已分配" />
        <el-option label="进行中" value="进行中" />
        <el-option label="已暂停" value="已暂停" />
        <el-option label="已完成" value="已完成" />
      </el-select>
      <el-select v-model="searchParams.department" placeholder="检测科室" clearable style="width: 140px">
        <el-option label="检测一部" value="检测一部" />
        <el-option label="检测二部" value="检测二部" />
        <el-option label="检测三部" value="检测三部" />
      </el-select>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon> 搜索
      </el-button>
      <el-button @click="handleReset">重置</el-button>
      <div style="flex: 1; text-align: right">
        <el-button type="primary" size="default" @click="handleCreate">
          <el-icon><Plus /></el-icon> 新建任务
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :span="4">
        <div class="mini-stat" style="background: #e6f7ff; border-color: #91d5ff">
          <span class="value">{{ statistics.total }}</span>
          <span class="label">总任务</span>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="mini-stat" style="background: #fff7e6; border-color: #ffd591">
          <span class="value">{{ statistics.pending }}</span>
          <span class="label">待分配</span>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="mini-stat" style="background: #fff1f0; border-color: #ffa39e">
          <span class="value">{{ statistics.assigned }}</span>
          <span class="label">已分配</span>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="mini-stat" style="background: #f0f5ff; border-color: #adc6ff">
          <span class="value">{{ statistics.in_progress }}</span>
          <span class="label">进行中</span>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="mini-stat" style="background: #f6ffed; border-color: #b7eb8f">
          <span class="value">{{ statistics.completed }}</span>
          <span class="label">已完成</span>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="mini-stat" style="background: #fff2e8; border-color: #ffbb96">
          <span class="value">{{ statistics.overdue }}</span>
          <span class="label">超期任务</span>
        </div>
      </el-col>
    </el-row>

    <!-- 数据表格 -->
    <div v-if="viewMode === 'list'" class="page-card">
      <el-table
        :data="tableData"
        stripe
        v-loading="loading"
        @row-click="handleRowClick"
        style="cursor: pointer"
      >
        <el-table-column prop="task_no" label="任务编号" min-width="150" />
        <el-table-column prop="sample_no" label="样品编号" min-width="150" />
        <el-table-column prop="sample_name" label="样品名称" min-width="150" />
        <el-table-column prop="test_items" label="检测项目" min-width="150" show-overflow-tooltip />
        <el-table-column prop="department" label="检测科室" min-width="100" />
        <el-table-column prop="assignee_name" label="负责人" min-width="90" />
        <el-table-column prop="priority" label="优先级" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.priority === '紧急' ? 'danger' : 'info'" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" min-width="120">
          <template #default="{ row }">
            <span :class="{ 'overdue': isOverdue(row.deadline) }">
              {{ formatDate(row.deadline) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="handleView(row)">
              详情
            </el-button>
            <el-button link type="primary" @click.stop="handleAssign(row)">
              分配
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 看板视图 -->
    <div v-else class="kanban-board">
      <div class="kanban-column" v-for="status in kanbanStatuses" :key="status.value">
        <div class="column-header" :style="{ borderTopColor: status.color }">
          <span class="title">{{ status.label }}</span>
          <el-tag size="small" effect="plain" round>{{ kanbanColumns[status.value]?.length || 0 }}</el-tag>
        </div>
        <div class="column-body">
          <draggable
            v-model="kanbanColumns[status.value]"
            item-key="id"
            group="tasks"
            @change="(evt) => onColumnChange(evt, status.value)"
            class="draggable-area"
          >
            <template #item="{ element: task }">
              <div 
                class="task-card" 
                @click="handleView(task)"
              >
                <div class="card-header">
                  <span class="task-no">{{ task.task_no }}</span>
                  <el-tag size="small" :type="task.priority === '紧急' ? 'danger' : 'info'">{{ task.priority }}</el-tag>
                </div>
                <div class="card-body">
                  <div class="card-row">
                    <span class="label">样品：</span>
                    <span class="value">{{ task.sample_name }}</span>
                  </div>
                  <div class="card-row">
                    <span class="label">项目：</span>
                    <span class="value" :title="task.test_items">{{ task.test_items }}</span>
                  </div>
                  <div class="card-row">
                    <span class="label">负责人：</span>
                    <span class="value">{{ task.assignee_name || '未分配' }}</span>
                  </div>
                  <div class="card-row" style="margin-top: 8px;">
                     <el-progress :percentage="task.progress" :stroke-width="6" style="width: 100%" />
                  </div>
                </div>
                <div class="card-footer">
                   <span class="date" :class="{ 'overdue': isOverdue(task.deadline, task.status) }">
                     截止: {{ formatDate(task.deadline) }}
                   </span>
                   <el-button link type="primary" size="small" @click.stop="handleAssign(task)" v-if="task.status === '待分配' || task.status === '待接收'">
                     分配
                   </el-button>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </div>

    <TaskAssignDialog 
      v-model="assignDialogVisible" 
      :task="currentAssignTask"
      @success="handleAssignSuccess"
    />

    <!-- 新建任务弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新建任务" width="600px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="样品" required>
          <el-select v-model="createForm.sample_id" placeholder="选择样品" style="width: 100%">
            <el-option
              v-for="item in sampleOptions"
              :key="item.id"
              :label="`${item.sample_no} - ${item.name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="检测项目">
          <el-input v-model="createForm.test_items" placeholder="如：铅、砷、镉" />
        </el-form-item>
        <el-form-item label="标准方法">
          <MethodSelect v-model="createForm.standard_method_id" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="createForm.priority">
            <el-radio label="普通">普通</el-radio>
            <el-radio label="紧急">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="createForm.deadline"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="检测科室">
          <el-select v-model="createForm.department" style="width: 100%">
            <el-option label="检测一部" value="检测一部" />
            <el-option label="检测二部" value="检测二部" />
            <el-option label="检测三部" value="检测三部" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remarks" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'
import draggable from 'vuedraggable'
import TaskAssignDialog from '@/components/TaskAssignDialog.vue'
import MethodSelect from '@/components/MethodSelect.vue'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const showCreateDialog = ref(false)
const assignDialogVisible = ref(false)
const currentAssignTask = ref(null)
const sampleOptions = ref([])
const viewMode = ref('list')

const kanbanColumns = reactive({
  '待分配': [],
  '已分配': [],
  '进行中': [],
  '已完成': []
})

watch(tableData, (newVal) => {
  // Clear columns
  Object.keys(kanbanColumns).forEach(k => kanbanColumns[k].length = 0)
  
  // Distribute
  newVal.forEach(task => {
    let key = task.status
    if (key === '待接收') key = '已分配'
    if (key === '已暂停') key = '进行中'
    if (kanbanColumns[key]) {
      kanbanColumns[key].push(task)
    }
  })
}, { deep: true, immediate: true })

const onColumnChange = (evt, status) => {
  if (evt.added) {
    const task = evt.added.element
    
    // If moved to '已分配', open assignment dialog
    if (status === '已分配') {
      currentAssignTask.value = task
      assignDialogVisible.value = true
      return
    }
    
    // Update status for other columns
    updateTaskStatus(task.id, status)
  }
}

async function updateTaskStatus(taskId, status) {
  try {
    await api.patch(`/tasks/${taskId}`, { status })
    ElMessage.success('状态更新成功')
    fetchData() 
    fetchStatistics()
  } catch (e) {
    ElMessage.error('状态更新失败')
    fetchData() // Revert changes
  }
}

function handleAssignSuccess() {
  fetchData()
  fetchStatistics()
}

// Watch dialog close to ensure UI consistency (revert drag if cancelled)
watch(assignDialogVisible, (val) => {
  if (!val) {
    fetchData()
  }
})

const kanbanStatuses = [
  { label: '待分配', value: '待分配', color: '#E6A23C' },
  { label: '已分配', value: '已分配', color: '#409EFF' },
  { label: '进行中', value: '进行中', color: '#67C23A' },
  { label: '已完成', value: '已完成', color: '#909399' }
]

const searchParams = reactive({
  keyword: '',
  status: '',
  department: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const statistics = ref({
  total: 4,
  pending: 1,
  in_progress: 1,
  completed: 1,
  overdue: 0
})

const createForm = reactive({
  sample_id: '',
  sample_no: '',
  sample_name: '',
  test_items: '',
  standard_method_id: '',
  priority: '普通',
  deadline: null,
  department: '',
  remarks: ''
})

onMounted(() => {
  fetchData()
  fetchStatistics()
  fetchOptions()
})

async function fetchData() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchParams
    }
    const res = await api.get('/tasks/', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchStatistics() {
  try {
    const res = await api.get('/tasks/statistics/')
    statistics.value = res.data
  } catch (e) {}
}

async function fetchOptions() {
  try {
    const res = await api.get('/samples/', { params: { limit: 100 } })
    sampleOptions.value = res.data.items || []
  } catch (e) {}
}

function handleViewModeChange(mode) {
  if (mode === 'kanban') {
    pagination.pageSize = 50
    fetchData()
  } else {
    pagination.pageSize = 10
    fetchData()
  }
}

function getTasksByStatus(status) {
  if (!tableData.value) return []
  if (status === '已分配') {
    return tableData.value.filter(t => t.status === '已分配' || t.status === '待接收')
  }
  if (status === '进行中') {
    return tableData.value.filter(t => t.status === '进行中' || t.status === '已暂停')
  }
  return tableData.value.filter(t => t.status === status)
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  Object.assign(searchParams, { keyword: '', status: '', department: '' })
  pagination.page = 1
  fetchData()
}

function handleCreate() {
  Object.assign(createForm, {
    sample_id: '',
    sample_no: '',
    sample_name: '',
    test_items: '',
    standard_method_id: '',
    priority: '普通',
    deadline: null,
    department: '',
    remarks: ''
  })
  showCreateDialog.value = true
}

async function saveTask() {
  if (!createForm.sample_id) {
    ElMessage.warning('请选择样品')
    return
  }
  
  const sample = sampleOptions.value.find(s => s.id === createForm.sample_id)
  if (sample) {
    createForm.sample_no = sample.sample_no
    createForm.sample_name = sample.name
  }
  
  try {
    await api.post('/tasks/', createForm)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    fetchData()
    fetchStatistics()
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

function handleRowClick(row) {
  router.push(`/task/detail/${row.id}`)
}

function handleView(row) {
  router.push(`/task/detail/${row.id}`)
}

function handleAssign(row) {
  router.push({ path: '/task/assign', query: { task_id: row.id } })
}

function getStatusType(status) {
  const map = {
    '待分配': 'info',
    '已分配': 'warning',
    '待接收': 'warning',
    '进行中': 'primary',
    '已完成': 'success',
    '已暂停': 'danger'
  }
  return map[status] || 'info'
}

function isOverdue(deadline, status) {
  if (!deadline || ['已完成', '已终止'].includes(status)) return false
  return dayjs(deadline).isBefore(dayjs(), 'day')
}

function formatDate(date) {
  return date ? dayjs(date).format('MM-DD') : '-'
}
</script>

<style lang="scss" scoped>
.task-list {
  .mini-stat {
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid;
    text-align: center;
    
    .value {
      display: block;
      font-size: 24px;
      font-weight: bold;
      color: #303133;
    }
    
    .label {
      display: block;
      font-size: 13px;
      color: #606266;
      margin-top: 4px;
    }
  }

  .overdue {
    color: #f56c6c;
    font-weight: 500;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
