<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <h1>欢迎回来，{{ userStore.userName }}</h1>
        <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
      </div>
      <div class="welcome-illustration">
        <el-icon :size="100" color="rgba(255,255,255,0.3)"><DataAnalysis /></el-icon>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon :size="32"><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.samples }}</div>
            <div class="stat-label">样品总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card success">
          <div class="stat-icon">
            <el-icon :size="32"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.tasks }}</div>
            <div class="stat-label">进行中任务</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card warning">
          <div class="stat-icon">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.reports }}</div>
            <div class="stat-label">待审核报告</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card info">
          <div class="stat-icon">
            <el-icon :size="32"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.warnings }}</div>
            <div class="stat-label">预警信息</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 内容区域 -->
    <el-row :gutter="20">
      <!-- 最近任务 -->
      <el-col :xs="24" :lg="12">
        <div class="page-card">
          <div class="card-header">
            <span class="card-title">最近任务</span>
            <el-button text type="primary" @click="$router.push('/task/list')">
              查看全部 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <el-table :data="recentTasks" stripe style="width: 100%">
            <el-table-column prop="task_no" label="任务编号" width="140" />
            <el-table-column prop="sample_name" label="样品名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ row.priority }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <!-- 最近样品 -->
      <el-col :xs="24" :lg="12">
        <div class="page-card">
          <div class="card-header">
            <span class="card-title">最近样品</span>
            <el-button text type="primary" @click="$router.push('/sample/list')">
              查看全部 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <el-table :data="recentSamples" stripe style="width: 100%">
            <el-table-column prop="sample_no" label="样品编号" width="140" />
            <el-table-column prop="name" label="样品名称" />
            <el-table-column prop="customer_name" label="客户" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- 任务进度图表 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :lg="12">
        <div class="page-card">
          <div class="card-header">
            <span class="card-title">任务统计</span>
          </div>
          <div ref="taskChartRef" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="page-card">
          <div class="card-header">
            <span class="card-title">样品状态分布</span>
          </div>
          <div ref="sampleChartRef" style="height: 300px"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { api } from '@/utils/api'
import dayjs from 'dayjs'
import * as echarts from 'echarts'

const userStore = useUserStore()
const taskChartRef = ref()
const sampleChartRef = ref()

const currentDate = dayjs().format('YYYY年MM月DD日')

const stats = ref({
  samples: 0,
  tasks: 0,
  reports: 0,
  warnings: 0
})

const recentTasks = ref([])
const recentSamples = ref([])

function getStatusType(status) {
  const map = {
    '待分配': 'info',
    '已分配': 'info',
    '待审核': 'warning',
    '进行中': 'primary',
    '检测中': 'primary',
    '已登记': 'success',
    '已完成': 'success',
    '检测完成': 'success',
    '已签发': 'success',
    '已归档': 'info'
  }
  return map[status] || 'info'
}

function getPriorityType(priority) {
  const map = {
    '紧急': 'danger',
    '普通': 'info'
  }
  return map[priority] || 'info'
}

onMounted(() => {
  initCharts()
  fetchData()
})

async function fetchData() {
  try {
    // 获取任务统计
    const taskRes = await api.get('/tasks/statistics/')
    if (taskRes.data) {
      stats.value.tasks = taskRes.data.in_progress || 0
    }
    
    // 获取样品统计
    const sampleRes = await api.get('/samples/', { params: { limit: 1 } })
    if (sampleRes.data) {
      stats.value.samples = sampleRes.data.total || 0
    }
    
    // 获取报告统计
    const reportRes = await api.get('/reports/statistics/')
    if (reportRes.data) {
      stats.value.reports = reportRes.data.pending || 0
    }
    
    // 获取预警
    const warningRes = await api.get('/resources/reagents/warning')
    if (warningRes.data) {
      const w = warningRes.data
      stats.value.warnings = (w.low_stock?.length || 0) + (w.expired?.length || 0) + (w.soon_expired?.length || 0)
    }
    
    // 获取最近任务
    const recentTaskRes = await api.get('/tasks/', { params: { limit: 5 } })
    recentTasks.value = recentTaskRes.data.items || []
    
    // 获取最近样品
    const recentSampleRes = await api.get('/samples/', { params: { limit: 5 } })
    recentSamples.value = recentSampleRes.data.items || []
    
    // 更新图表数据
    updateCharts()
  } catch (e) {
    console.log('统计数据加载中...')
  }
}

function initCharts() {
  // 任务统计图
  const taskChart = echarts.init(taskChartRef.value)
  taskChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%', left: 'center' },
    series: [{
      name: '任务状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 16, fontWeight: 'bold' }
      },
      labelLine: { show: false },
      data: []
    }]
  })

  // 样品状态图
  const sampleChart = echarts.init(sampleChartRef.value)
  sampleChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['已登记', '检测中', '检测完成', '已归档']
    },
    yAxis: { type: 'value' },
    series: [{
      data: [],
      type: 'bar',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#409eff' },
          { offset: 1, color: '#79bbff' }
        ])
      }
    }]
  })

  // 响应式
  window.addEventListener('resize', () => {
    taskChart.resize()
    sampleChart.resize()
  })
}

async function updateCharts() {
  const taskChart = echarts.getInstanceByDom(taskChartRef.value)
  const sampleChart = echarts.getInstanceByDom(sampleChartRef.value)
  
  if (taskChart) {
    // 获取任务状态统计
    try {
      const res = await api.get('/tasks/statistics/')
      const data = res.data || {}
      taskChart.setOption({
        series: [{
          data: [
            { value: data.pending || 0, name: '待分配', itemStyle: { color: '#909399' } },
            { value: data.assigned || data.waiting || 0, name: '已分配', itemStyle: { color: '#e6a23c' } },
            { value: data.in_progress || 0, name: '进行中', itemStyle: { color: '#409eff' } },
            { value: data.completed || 0, name: '已完成', itemStyle: { color: '#67c23a' } }
          ]
        }]
      })
    } catch (e) {}
  }
  
  if (sampleChart) {
    // 统计样品状态
    const statusCount = { '已登记': 0, '检测中': 0, '检测完成': 0, '已归档': 0 }
    recentSamples.value.forEach(s => {
      if (statusCount[s.status] !== undefined) {
        statusCount[s.status]++
      }
    })
    sampleChart.setOption({
      series: [{ data: Object.values(statusCount) }]
    })
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  .welcome-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 30px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    margin-bottom: 24px;
    
    .welcome-content {
      h1 {
        font-size: 24px;
        margin-bottom: 8px;
      }
      
      p {
        font-size: 14px;
        opacity: 0.9;
      }
    }
    
    .welcome-illustration {
      opacity: 0.5;
    }
  }

  .stat-row {
    margin-bottom: 20px;
    
    .el-col {
      margin-bottom: 16px;
    }
  }

  .stat-card {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-4px);
    }
    
    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }
    
    &.success .stat-icon {
      background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    &.warning .stat-icon {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    &.info .stat-icon {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .stat-info {
      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
      }
      
      .stat-label {
        font-size: 14px;
        color: #909399;
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
}
</style>
