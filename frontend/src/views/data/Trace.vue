<template>
  <div class="data-trace">
    <div class="page-header">
      <h2 class="page-title">数据溯源</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <div class="page-card">
          <h3 class="card-title">溯源查询</h3>
          <el-form :model="searchForm" label-width="80px">
            <el-form-item label="溯源类型">
              <el-select v-model="searchForm.trace_type" style="width: 100%">
                <el-option label="样品溯源" value="sample" />
                <el-option label="任务溯源" value="task" />
              </el-select>
            </el-form-item>
            <el-form-item label="编号">
              <el-input v-model="searchForm.keyword" placeholder="输入样品/任务编号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch" style="width: 100%">
                开始溯源
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="page-card" style="margin-top: 20px">
          <h3 class="card-title">快速选择</h3>
          <el-select v-model="quickSelect" placeholder="选择样品" style="width: 100%" @change="handleQuickSelect">
            <el-option v-for="item in sampleList" :key="item.id" :label="item.sample_no" :value="item.id" />
          </el-select>
        </div>
      </el-col>

      <el-col :span="16">
        <div class="page-card">
          <h3 class="card-title">溯源结果</h3>
          
          <template v-if="traceTree.children && traceTree.children.length">
            <el-tree
              :data="[traceTree]"
              :props="{ label: 'name', children: 'children' }"
              default-expand-all
              class="trace-tree"
            >
              <template #default="{ node, data }">
                <div class="tree-node">
                  <el-icon v-if="data.type"><Document /></el-icon>
                  <span>{{ data.name }}</span>
                  <el-tag v-if="data.type" size="small" style="margin-left: 8px">{{ data.type }}</el-tag>
                  <span v-if="data.time" class="time">{{ data.time }}</span>
                </div>
              </template>
            </el-tree>
          </template>
          
          <el-empty v-else description="请输入编号进行溯源查询" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'

const searchForm = reactive({
  trace_type: 'sample',
  keyword: ''
})

const quickSelect = ref('')
const sampleList = ref([])
const traceTree = ref({ name: '溯源根节点', children: [] })

onMounted(() => {
  fetchSampleList()
})

async function fetchSampleList() {
  try {
    const res = await api.get('/samples/', { params: { limit: 20 } })
    sampleList.value = res.data.items || []
  } catch (e) {}
}

async function handleSearch() {
  if (!searchForm.keyword) {
    ElMessage.warning('请输入编号')
    return
  }
  
  try {
    const params = searchForm.trace_type === 'sample' 
      ? { sample_id: searchForm.keyword }
      : { task_id: searchForm.keyword }
    const res = await api.get('/data/traces/tree', { params })
    traceTree.value = res.data || { name: '溯源结果', children: [] }
  } catch (e) {
    ElMessage.error('溯源查询失败')
  }
}

async function handleQuickSelect(sampleId) {
  searchForm.trace_type = 'sample'
  searchForm.keyword = sampleId
  await handleSearch()
}
</script>

<style lang="scss" scoped>
.data-trace {
  .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
  }

  .trace-tree {
    .tree-node {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .time {
        margin-left: auto;
        color: #909399;
        font-size: 12px;
      }
    }
  }
}
</style>
