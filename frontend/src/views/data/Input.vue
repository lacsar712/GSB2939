<template>
  <div class="data-input">
    <div class="page-header">
      <h2 class="page-title">检测数据录入</h2>
    </div>

    <el-row :gutter="20">
      <!-- 选择任务 -->
      <el-col :span="8">
        <div class="page-card">
          <h3 class="card-title">选择任务</h3>
          <el-input v-model="searchKeyword" placeholder="搜索任务" clearable style="margin-bottom: 16px" />
          <div class="task-list">
            <div
              v-for="task in filteredTasks"
              :key="task.id"
              class="task-item"
              :class="{ active: selectedTask?.id === task.id }"
              @click="selectTask(task)"
            >
              <div class="task-no">{{ task.task_no }}</div>
              <div class="task-name">{{ task.sample_name }}</div>
              <el-tag size="small" :type="getStatusType(task.status)">{{ task.status }}</el-tag>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 数据录入 -->
      <el-col :span="16">
        <div class="page-card" v-if="selectedTask">
          <h3 class="card-title">数据录入 - {{ selectedTask.task_no }}</h3>
          
          <el-form :model="formData" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="检测项目">
                  <el-input v-model="formData.item_name" placeholder="请输入检测项目" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="检测方法">
                  <el-input v-model="formData.test_method" placeholder="请输入检测方法" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="结果值">
                  <el-input-number v-model="formData.result_value" :precision="4" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="单位">
                  <el-select v-model="formData.result_unit" style="width: 100%">
                    <el-option label="mg/kg" value="mg/kg" />
                    <el-option label="mg/L" value="mg/L" />
                    <el-option label="μg/kg" value="μg/kg" />
                    <el-option label="%" value="%" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="标准值">
                  <el-input v-model="formData.standard_value" placeholder="如：≤0.5" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="是否合格">
                  <el-radio-group v-model="formData.is_qualified">
                    <el-radio :label="true">合格</el-radio>
                    <el-radio :label="false">不合格</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="环境条件">
                  <el-input v-model="formData.environment" placeholder="如：温度25℃，湿度60%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="备注">
              <el-input v-model="formData.remarks" type="textarea" :rows="2" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="loading">
                提交数据
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 已录入数据 -->
          <el-divider />
          <h4 style="margin-bottom: 16px">已录入数据</h4>
          <el-table :data="existingData" stripe size="small">
            <el-table-column prop="item_name" label="检测项目" />
            <el-table-column prop="result_value" label="结果值" width="100">
              <template #default="{ row }">
                {{ row.result_value }} {{ row.result_unit }}
              </template>
            </el-table-column>
            <el-table-column prop="is_qualified" label="判定" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_qualified ? 'success' : 'danger'" size="small">
                  {{ row.is_qualified ? '合格' : '不合格' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <el-empty v-else description="请从左侧选择任务" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'

const loading = ref(false)
const tasks = ref([])
const selectedTask = ref(null)
const existingData = ref([])
const searchKeyword = ref('')

const formData = reactive({
  task_id: 0,
  sample_id: 0,
  item_name: '',
  result_value: 0,
  result_unit: 'mg/kg',
  standard_value: '',
  is_qualified: true,
  test_method: '',
  environment: '',
  remarks: ''
})

const filteredTasks = computed(() => {
  if (!searchKeyword.value) return tasks.value
  return tasks.value.filter(t => 
    t.task_no.includes(searchKeyword.value) || 
    t.sample_name.includes(searchKeyword.value)
  )
})

onMounted(() => {
  fetchTasks()
})

async function fetchTasks() {
  try {
    const res = await api.get('/tasks/', { params: { status: '进行中', limit: 50 } })
    tasks.value = res.data.items || []
  } catch (e) {}
}

async function selectTask(task) {
  selectedTask.value = task
  formData.task_id = task.id
  formData.sample_id = task.sample_id
  
  // 获取已录入数据
  try {
    const res = await api.get('/data/detection/', { params: { task_id: task.id } })
    existingData.value = res.data.items || []
  } catch (e) {
    existingData.value = []
  }
}

async function handleSubmit() {
  if (!formData.item_name) {
    ElMessage.warning('请输入检测项目')
    return
  }
  
  loading.value = true
  try {
    await api.post('/data/detection/', formData)
    ElMessage.success('提交成功')
    handleReset()
    // 刷新已录入数据
    const res = await api.get('/data/detection/', { params: { task_id: selectedTask.value.id } })
    existingData.value = res.data.items || []
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    loading.value = false
  }
}

function handleReset() {
  formData.item_name = ''
  formData.result_value = 0
  formData.standard_value = ''
  formData.is_qualified = true
  formData.test_method = ''
  formData.environment = ''
  formData.remarks = ''
}

function getStatusType(status) {
  const map = { '进行中': 'primary', '已完成': 'success' }
  return map[status] || 'info'
}
</script>

<style lang="scss" scoped>
.data-input {
  .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
  }

  .task-list {
    max-height: calc(100vh - 300px);
    overflow: auto;
  }

  .task-item {
    padding: 12px;
    border: 1px solid #eee;
    border-radius: 8px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover, &.active {
      border-color: #409eff;
      background: #ecf5ff;
    }

    .task-no {
      font-size: 13px;
      color: #409eff;
      margin-bottom: 4px;
    }

    .task-name {
      font-size: 14px;
      color: #303133;
      margin-bottom: 8px;
    }
  }
}
</style>
