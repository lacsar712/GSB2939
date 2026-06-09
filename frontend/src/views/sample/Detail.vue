<template>
  <div class="sample-detail">
    <div class="page-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <div class="actions">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon> 编辑
        </el-button>
        <el-button @click="handlePrint">
          <el-icon><Printer /></el-icon> 打印标签
        </el-button>
        <el-button type="primary" @click="handleCreateTask">
          <el-icon><Plus /></el-icon> 创建任务
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 基本信息 -->
        <div class="page-card">
          <h3 class="card-title">基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="样品编号">
              {{ sampleInfo.sample_no }}
            </el-descriptions-item>
            <el-descriptions-item label="样品名称">
              {{ sampleInfo.name }}
            </el-descriptions-item>
            <el-descriptions-item label="样品来源">
              {{ sampleInfo.source }}
            </el-descriptions-item>
            <el-descriptions-item label="样品类型">
              {{ sampleInfo.type }}
            </el-descriptions-item>
            <el-descriptions-item label="批次号">
              {{ sampleInfo.batch_no }}
            </el-descriptions-item>
            <el-descriptions-item label="数量">
              {{ sampleInfo.quantity }} {{ sampleInfo.unit }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(sampleInfo.status)">
                {{ sampleInfo.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="接收日期">
              {{ formatDate(sampleInfo.receive_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="预期完成日期">
              {{ formatDate(sampleInfo.expected_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">
              {{ sampleInfo.remarks || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 客户信息 -->
        <div class="page-card">
          <h3 class="card-title">客户信息</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="客户名称">
              {{ sampleInfo.customer_name }}
            </el-descriptions-item>
            <el-descriptions-item label="联系人">
              {{ sampleInfo.customer_contact }}
            </el-descriptions-item>
            <el-descriptions-item label="联系电话">
              {{ sampleInfo.customer_phone }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 流转记录 -->
        <div class="page-card">
          <h3 class="card-title">流转记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="item in transfers"
              :key="item.id"
              :timestamp="formatDate(item.created_at)"
              placement="top"
            >
              <div class="timeline-content">
                <h4>{{ item.operation }}</h4>
                <p v-if="item.from_status || item.to_status">
                  {{ item.from_status }} → {{ item.to_status }}
                </p>
                <p v-if="item.operator_name">操作人：{{ item.operator_name }}</p>
                <p v-if="item.remarks">备注：{{ item.remarks }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>

      <el-col :span="8">
        <!-- 二维码 -->
        <div class="page-card text-center">
          <h3 class="card-title">样品标识</h3>
          <canvas ref="qrcodeRef" class="qrcode"></canvas>
          <p class="sample-no">{{ sampleInfo.sample_no }}</p>
        </div>

        <!-- 关联任务 -->
        <div class="page-card">
          <h3 class="card-title">关联任务</h3>
          <el-empty v-if="!relatedTasks.length" description="暂无关联任务" :image-size="60" />
          <div v-else class="task-list">
            <div
              v-for="task in relatedTasks"
              :key="task.id"
              class="task-item"
              @click="$router.push(`/task/detail/${task.id}`)"
            >
              <div class="task-info">
                <span class="task-no">{{ task.task_no }}</span>
                <el-tag :type="getStatusType(task.status)" size="small">
                  {{ task.status }}
                </el-tag>
              </div>
              <div class="task-progress">
                <el-progress :percentage="task.progress" :stroke-width="6" />
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="page-card">
          <h3 class="card-title">快捷操作</h3>
          <div class="quick-actions">
            <el-button type="success" @click="handleStatusChange('检测中')">
              开始检测
            </el-button>
            <el-button type="primary" @click="handleStatusChange('检测完成')">
              完成检测
            </el-button>
            <el-button type="info" @click="handleStatusChange('已归档')">
              归档
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 编辑样品弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑样品" width="800px">
      <el-form :model="editForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="样品名称">
              <el-input v-model="editForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="样品来源">
              <el-input v-model="editForm.source" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="样品类型">
              <el-select v-model="editForm.type" style="width: 100%">
                <el-option label="食品" value="食品" />
                <el-option label="饮用水" value="饮用水" />
                <el-option label="环境" value="环境" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="批次号">
              <el-input v-model="editForm.batch_no" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量">
              <el-input-number v-model="editForm.quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="editForm.unit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户名称">
              <el-input v-model="editForm.customer_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="editForm.customer_contact" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="editForm.customer_phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预期完成日期">
              <el-date-picker
                v-model="editForm.expected_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="editForm.remarks" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSample">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import dayjs from 'dayjs'
import QRCode from 'qrcode'

const route = useRoute()
const router = useRouter()
const qrcodeRef = ref()

const sampleInfo = ref({})
const transfers = ref([])
const relatedTasks = ref([])

const showEditDialog = ref(false)
const editForm = reactive({})

onMounted(() => {
  fetchSampleDetail()
})

async function fetchSampleDetail() {
  try {
    const res = await api.get(`/samples/${route.params.id}`)
    sampleInfo.value = res.data.sample || {}
    transfers.value = res.data.transfers || []
    relatedTasks.value = res.data.tasks || []

    // 生成二维码
    nextTick(() => {
      if (qrcodeRef.value && sampleInfo.value.sample_no) {
        QRCode.toCanvas(qrcodeRef.value, `SAMPLE:${sampleInfo.value.sample_no}`, {
          width: 180,
          margin: 2
        })
      }
      // 自动打印
      if (route.query.print === 'true') {
        setTimeout(() => {
          window.print()
        }, 500)
      }
    })
  } catch (e) {
    ElMessage.error('获取样品详情失败')
  }
}

async function handleStatusChange(status) {
  try {
    await api.put(`/samples/${sampleInfo.value.id}`, { status })
    ElMessage.success('状态更新成功')
    fetchSampleDetail()
  } catch (e) {
    ElMessage.error('状态更新失败')
  }
}

function handleEdit() {
  Object.assign(editForm, sampleInfo.value)
  showEditDialog.value = true
}

async function saveSample() {
  try {
    await api.put(`/samples/${sampleInfo.value.id}`, editForm)
    ElMessage.success('保存成功')
    showEditDialog.value = false
    fetchSampleDetail()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

function handlePrint() {
  window.print()
}

function handleCreateTask() {
  router.push({
    path: '/task/list',
    query: { sample_id: sampleInfo.value.id }
  })
}

function getStatusType(status) {
  const map = {
    '已登记': 'success',
    '检测中': 'primary',
    '检测完成': 'info',
    '已归档': 'info',
    '进行中': 'primary',
    '已完成': 'success',
    '待分配': 'info'
  }
  return map[status] || 'info'
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
@media print {
  :deep(.page-header),
  :deep(.el-dialog__wrapper),
  :deep(.v-modal),
  :deep(.el-overlay) {
    display: none !important;
  }
  .sample-detail {
    padding: 0;
  }
  .page-card {
    box-shadow: none !important;
    border: 1px solid #ccc;
    margin-bottom: 20px;
    break-inside: avoid;
  }
}

.sample-detail {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .actions {
      display: flex;
      gap: 10px;
    }
  }

  .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #eee;
  }

  .qrcode {
    display: inline-block;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 16px;
  }

  .sample-no {
    font-size: 18px;
    font-weight: bold;
    color: #303133;
  }

  .timeline-content {
    h4 {
      margin: 0 0 8px;
      color: #303133;
    }
    
    p {
      margin: 4px 0;
      color: #606266;
      font-size: 13px;
    }
  }

  .task-list {
    .task-item {
      padding: 12px;
      border: 1px solid #eee;
      border-radius: 8px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        border-color: #409eff;
        background: #f5f7fa;
      }
      
      .task-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .task-no {
          font-weight: 500;
          color: #303133;
        }
      }
      
      .task-progress {
        margin-top: 8px;
      }
    }
  }

  .quick-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
    
    .el-button {
      width: 100%;
      margin-left: 0;
    }
  }
}
</style>
