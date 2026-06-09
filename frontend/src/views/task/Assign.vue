<template>
  <div class="task-assign">
    <div class="page-header">
      <h2 class="page-title">任务分配</h2>
    </div>

    <el-row :gutter="20">
      <!-- 待分配任务 -->
      <el-col :span="12">
        <div class="page-card">
          <div class="card-header">
            <span>待分配任务</span>
            <el-tag type="warning">{{ pendingTasks.length }}</el-tag>
          </div>
          <div class="task-pool">
            <div
              v-for="task in pendingTasks"
              :key="task.id"
              class="task-card"
              :class="{ selected: selectedTask?.id === task.id }"
              draggable="true"
              @dragstart="handleDragStart($event, task)"
              @click="selectTask(task)"
            >
              <div class="task-header">
                <span class="task-no">{{ task.task_no }}</span>
                <el-tag :type="task.priority === '紧急' ? 'danger' : 'info'" size="small">
                  {{ task.priority }}
                </el-tag>
              </div>
              <div class="task-body">
                <p><strong>{{ task.sample_name }}</strong></p>
                <p class="text-muted">{{ task.test_items }}</p>
              </div>
              <div class="task-footer">
                <span>截止：{{ formatDate(task.deadline) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 检测人员列表 -->
      <el-col :span="12">
        <div class="page-card">
          <div class="card-header">
            <span>检测人员</span>
          </div>
          <div class="tester-list">
            <div
              v-for="tester in testers"
              :key="tester.id"
              class="tester-card"
              @dragover.prevent
              @drop="handleDrop($event, tester)"
            >
              <div class="tester-avatar">
                <el-avatar :size="48">{{ tester.name.charAt(0) }}</el-avatar>
              </div>
              <div class="tester-info">
                <h4>{{ tester.name }}</h4>
                <p>{{ tester.department }}</p>
                <el-tag size="small" type="info">当前任务：{{ tester.taskCount }}</el-tag>
              </div>
              <el-button
                v-if="selectedTask && tester.id"
                type="primary"
                size="small"
                @click="assignTask(tester)"
              >
                分配
              </el-button>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'

const pendingTasks = ref([])
const testers = ref([])
const selectedTask = ref(null)

onMounted(() => {
  fetchPendingTasks()
  fetchTesters()
})

async function fetchPendingTasks() {
  try {
    const res = await api.get('/tasks/', { params: { status: '待分配', limit: 50 } })
    pendingTasks.value = res.data.items || []
  } catch (e) {}
}

async function fetchTesters() {
  try {
    const res = await api.get('/users/', { params: { role: 'tester' } })
    // 获取检测人员（角色为检测人员的用户）
    testers.value = (res.data || [])
      .filter(u => u.roles?.some(r => r.code === 'tester'))
      .map(u => ({
        id: u.id,
        name: u.real_name || u.username,
        department: u.department,
        taskCount: 0
      }))
  } catch (e) {
    testers.value = []
    ElMessage.error('获取检测人员失败')
  }
}

function selectTask(task) {
  selectedTask.value = task
}

function handleDragStart(event, task) {
  event.dataTransfer.setData('taskId', task.id)
  selectedTask.value = task
}

async function handleDrop(event, tester) {
  const taskId = event.dataTransfer.getData('taskId')
  if (taskId) {
    await doAssign(Number(taskId), tester)
  }
}

async function assignTask(tester) {
  if (!selectedTask.value) {
    ElMessage.warning('请先选择任务')
    return
  }
  await doAssign(selectedTask.value.id, tester)
}

async function doAssign(taskId, tester) {
  try {
    await api.post(`/tasks/${taskId}/assign`, {
      task_id: taskId,
      user_id: tester.id,
      user_name: tester.name,
      department: tester.department
    })
    ElMessage.success(`已分配给 ${tester.name}`)
    fetchPendingTasks()
    selectedTask.value = null
  } catch (e) {
    ElMessage.error('分配失败')
  }
}

function formatDate(date) {
  return date ? dayjs(date).format('MM-DD') : '-'
}
</script>

<style lang="scss" scoped>
.task-assign {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    font-weight: 600;
  }

  .task-pool {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: calc(100vh - 280px);
    overflow: auto;
  }

  .task-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.3s;
    border: 2px solid transparent;

    &:hover {
      background: #f0f2f5;
    }

    &.selected {
      border-color: #409eff;
      background: #ecf5ff;
    }

    .task-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .task-no {
        font-weight: 500;
        color: #409eff;
      }
    }

    .task-body {
      margin-bottom: 8px;
      
      p {
        margin: 4px 0;
      }
      
      .text-muted {
        color: #909399;
        font-size: 13px;
      }
    }

    .task-footer {
      font-size: 12px;
      color: #909399;
    }
  }

  .tester-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .tester-card {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 16px;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .tester-info {
      flex: 1;

      h4 {
        margin: 0 0 4px;
      }

      p {
        margin: 0 0 8px;
        color: #909399;
        font-size: 13px;
      }
    }
  }
}
</style>
