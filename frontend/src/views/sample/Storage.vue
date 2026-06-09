<template>
  <div class="sample-storage">
    <div class="page-header">
      <h2 class="page-title">样品存储</h2>
    </div>

    <div class="search-form">
      <div style="flex: 1; text-align: right">
        <el-button type="primary" @click="handleAddStorage">
          <el-icon><Plus /></el-icon> 新增存储位置
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 存储位置树 -->
      <el-col :span="6">
        <div class="page-card" style="height: calc(100vh - 200px); overflow: auto">
          <h4 style="margin-bottom: 16px">存储位置</h4>
          <el-tree
            :data="storageTree"
            :props="{ label: 'location_name', children: 'children' }"
            default-expand-all
            :expand-on-click-node="false"
            draggable
            @node-drop="handleNodeDrop"
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon><Folder /></el-icon>
                <span>{{ data.location_name }}</span>
                <el-tag size="small" type="info" style="margin-left: 8px">
                  {{ data.used_capacity }}/{{ data.capacity }}
                </el-tag>
              </div>
            </template>
          </el-tree>
        </div>
      </el-col>

      <!-- 存储详情 -->
      <el-col :span="18">
        <div class="page-card">
          <div class="storage-header">
            <h3>{{ currentStorage?.location_name || '请选择存储位置' }}</h3>
            <el-tag v-if="currentStorage" :type="getStatusType(currentStorage.status)">
              {{ currentStorage.status }}
            </el-tag>
          </div>

          <template v-if="currentStorage">
            <el-descriptions :column="3" border style="margin-bottom: 20px">
              <el-descriptions-item label="位置编码">
                {{ currentStorage.location_code }}
              </el-descriptions-item>
              <el-descriptions-item label="位置类型">
                {{ currentStorage.location_type }}
              </el-descriptions-item>
              <el-descriptions-item label="容量使用">
                {{ currentStorage.used_capacity }} / {{ currentStorage.capacity }}
              </el-descriptions-item>
              <el-descriptions-item label="温度要求">
                {{ currentStorage.temperature || '无' }}
              </el-descriptions-item>
              <el-descriptions-item label="湿度要求">
                {{ currentStorage.humidity || '无' }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                {{ currentStorage.status }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 容量可视化 -->
            <div class="capacity-visual" style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
              <div ref="capacityChartRef" style="width: 100%; height: 300px;"></div>
            </div>

            <!-- 存储样品列表 -->
            <h4 style="margin: 20px 0 16px">存储样品</h4>
            <el-table :data="storedSamples" stripe>
              <el-table-column prop="sample_no" label="样品编号" width="150" />
              <el-table-column prop="name" label="样品名称" />
              <el-table-column prop="type" label="类型" width="100" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="220">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="handleMove(row)">
                    移动
                  </el-button>
                  <el-button link type="primary" size="small" @click="handleOut(row)">
                    出库
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </template>

          <el-empty v-else description="请从左侧选择存储位置" />
        </div>
      </el-col>
    </el-row>

    <!-- 新增存储位置弹窗 -->
    <el-dialog v-model="showStorageDialog" title="新增存储位置" width="500px">
      <el-form :model="storageForm" label-width="100px">
        <el-form-item label="位置编码">
          <el-input v-model="storageForm.location_code" />
        </el-form-item>
        <el-form-item label="位置名称">
          <el-input v-model="storageForm.location_name" />
        </el-form-item>
        <el-form-item label="位置类型">
          <el-select v-model="storageForm.location_type" style="width: 100%">
            <el-option label="库房" value="库房" />
            <el-option label="冰箱" value="冰箱" />
            <el-option label="货架" value="货架" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="storageForm.capacity" :min="1" />
        </el-form-item>
        <el-form-item label="温度要求">
          <el-input v-model="storageForm.temperature" placeholder="如：4℃" />
        </el-form-item>
        <el-form-item label="湿度要求">
          <el-input v-model="storageForm.humidity" placeholder="如：50%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStorageDialog = false">取消</el-button>
        <el-button type="primary" @click="saveStorage">确定</el-button>
      </template>
    </el-dialog>
    <!-- 移动样品弹窗 -->
    <el-dialog v-model="showMoveDialog" title="移动样品" width="400px">
      <el-form :model="moveForm" label-width="80px">
        <el-form-item label="目标位置">
          <el-select v-model="moveForm.target_storage_id" style="width: 100%" placeholder="请选择目标位置">
            <el-option
              v-for="item in allStorages"
              :key="item.id"
              :label="item.location_name"
              :value="item.id"
              :disabled="item.id === currentStorage?.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="saveMove">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/utils/api'
import * as echarts from 'echarts'

const storageTree = ref([])
const allStorages = ref([])
const currentStorage = ref(null)
const storedSamples = ref([])
const showStorageDialog = ref(false)
const showMoveDialog = ref(false)
const capacityChartRef = ref(null)
let capacityChart = null

const moveForm = reactive({
  sample_id: null,
  target_storage_id: null
})

const storageForm = reactive({
  location_code: '',
  location_name: '',
  location_type: '货架',
  capacity: 100,
  temperature: '',
  humidity: ''
})

const initCapacityChart = () => {
  if (!capacityChartRef.value || !currentStorage.value) return
  
  if (capacityChart) {
    capacityChart.dispose()
  }
  
  capacityChart = echarts.init(capacityChartRef.value)
  
  const used = currentStorage.value.used_capacity || 0
  const total = currentStorage.value.capacity || 100
  const free = Math.max(0, total - used)
  
  const option = {
    title: {
      text: '存储容量分布',
      left: 'center',
      top: '10px'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        name: '容量详情',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: used, name: '已使用', itemStyle: { color: '#F56C6C' } },
          { value: free, name: '剩余空间', itemStyle: { color: '#67C23A' } }
        ]
      }
    ]
  }
  
  capacityChart.setOption(option)
}

watch(currentStorage, async () => {
  await nextTick()
  initCapacityChart()
})

const handleResize = () => {
  capacityChart && capacityChart.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  fetchStorageData()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (capacityChart) {
    capacityChart.dispose()
  }
})

async function fetchStorageData() {
  try {
    const res = await api.get('/samples/storages/')
    const list = res.data || []
    allStorages.value = list
    // 构建树形结构
    const buildTree = (items, parentId = null) => {
      return items
        .filter(item => item.parent_id === parentId)
        .map(item => ({
          ...item,
          children: buildTree(items, item.id)
        }))
    }
    storageTree.value = buildTree(list)
  } catch (e) {
    console.error('获取存储位置失败', e)
  }
}

function handleNodeClick(data) {
  currentStorage.value = data
  fetchStoredSamples(data.id)
}

async function handleNodeDrop(draggingNode, dropNode, dropType, ev) {
  let parentId = null
  if (dropType === 'inner') {
    parentId = dropNode.data.id
  } else {
    parentId = dropNode.data.parent_id
  }
  
  // If undefined, treat as null (root)
  if (parentId === undefined) parentId = null

  try {
    await api.put(`/samples/storages/${draggingNode.data.id}`, {
      parent_id: parentId
    })
    ElMessage.success('移动成功')
    fetchStorageData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '移动失败')
    fetchStorageData()
  }
}

async function fetchStoredSamples(storageId) {
  try {
    const res = await api.get('/samples/', { params: { storage_id: storageId, limit: 100 } })
    storedSamples.value = res.data.items || []
  } catch (e) {
    storedSamples.value = []
  }
}

function handleAddStorage() {
  storageForm.location_code = ''
  storageForm.location_name = ''
  storageForm.location_type = '货架'
  storageForm.capacity = 100
  storageForm.temperature = ''
  storageForm.humidity = ''
  showStorageDialog.value = true
}

async function saveStorage() {
  try {
    await api.post('/samples/storages/', storageForm)
    ElMessage.success('添加成功')
    showStorageDialog.value = false
    fetchStorageData()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

function handleMove(row) {
  moveForm.sample_id = row.id
  moveForm.target_storage_id = null
  showMoveDialog.value = true
}

async function saveMove() {
  if (!moveForm.target_storage_id) {
    ElMessage.warning('请选择目标位置')
    return
  }
  try {
    await api.put(`/samples/${moveForm.sample_id}`, { storage_id: moveForm.target_storage_id })
    ElMessage.success('移动成功')
    showMoveDialog.value = false
    if (currentStorage.value) fetchStoredSamples(currentStorage.value.id)
    fetchStorageData() // Update capacity
  } catch (e) {
    ElMessage.error('移动失败')
  }
}

async function handleOut(row) {
  try {
    await ElMessageBox.confirm(`确定将样品 "${row.name}" 出库吗？`, '提示', { type: 'warning' })
    await api.put(`/samples/${row.id}`, { storage_id: null, status: '已出库' }) // Update status too? Maybe.
    ElMessage.success('出库成功')
    if (currentStorage.value) fetchStoredSamples(currentStorage.value.id)
    fetchStorageData() // Update capacity
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('出库失败')
  }
}

function getStatusType(status) {
  const map = {
    '正常': 'success',
    '已满': 'warning',
    '异常': 'danger'
  }
  return map[status] || 'info'
}
</script>

<style lang="scss" scoped>
.sample-storage {
  .tree-node {
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
    font-size: 14px;
  }

  .storage-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 {
      margin: 0;
    }
  }

  .capacity-bar {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 8px;
    
    span {
      display: block;
      margin-bottom: 8px;
      color: #606266;
    }
  }
}
</style>
