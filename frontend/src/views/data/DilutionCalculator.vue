<template>
  <div class="dilution-calculator">
    <div class="page-header">
      <h2 class="page-title">溶液稀释倍数计算器</h2>
    </div>

    <el-row :gutter="20" justify="center">
      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">计算稀释倍数</h3>
          
          <el-form :model="formData" label-width="120px">
            <el-form-item label="原始浓度">
              <el-input-number
                v-model="formData.original_concentration"
                :min="0"
                :precision="4"
                :step="0.1"
                style="width: 100%"
                placeholder="请输入原始浓度"
              />
              <span class="unit-label">单位：mg/L 等</span>
            </el-form-item>

            <el-form-item label="目标浓度">
              <el-input-number
                v-model="formData.target_concentration"
                :min="0"
                :precision="4"
                :step="0.1"
                style="width: 100%"
                placeholder="请输入目标浓度"
              />
              <span class="unit-label">单位：与原始浓度一致</span>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleCalculate" :loading="loading">
                计算稀释倍数
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="page-card result-card" v-if="result">
          <h3 class="card-title">计算结果</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="原始浓度">
              {{ result.original_concentration }}
            </el-descriptions-item>
            <el-descriptions-item label="目标浓度">
              {{ result.target_concentration }}
            </el-descriptions-item>
            <el-descriptions-item label="稀释倍数">
              <span class="dilution-result">{{ result.dilution_factor }} 倍</span>
            </el-descriptions-item>
          </el-descriptions>
          <div class="result-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>即 1 份原液需加入 {{ result.dilution_factor - 1 }} 份稀释液</span>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { api } from '@/utils/api'

const loading = ref(false)
const result = ref(null)

const formData = reactive({
  original_concentration: null,
  target_concentration: null
})

async function handleCalculate() {
  if (formData.original_concentration === null || formData.original_concentration === undefined) {
    ElMessage.warning('请输入原始浓度')
    return
  }
  if (formData.target_concentration === null || formData.target_concentration === undefined) {
    ElMessage.warning('请输入目标浓度')
    return
  }

  loading.value = true
  result.value = null
  try {
    const res = await api.post('/data/dilution/calculate', {
      original_concentration: formData.original_concentration,
      target_concentration: formData.target_concentration
    })
    result.value = res.data
    ElMessage.success('计算成功')
  } catch (e) {
    if (e.response?.data?.detail) {
      ElMessage.error(e.response.data.detail)
    }
  } finally {
    loading.value = false
  }
}

function handleReset() {
  formData.original_concentration = null
  formData.target_concentration = null
  result.value = null
}
</script>

<style lang="scss" scoped>
.dilution-calculator {
  .page-card {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }

  .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #303133;
  }

  .unit-label {
    display: block;
    font-size: 12px;
    color: #909399;
    margin-top: 6px;
  }

  .result-card {
    .dilution-result {
      font-size: 24px;
      font-weight: 700;
      color: #409eff;
    }

    .result-tip {
      margin-top: 16px;
      padding: 12px 16px;
      background: #ecf5ff;
      border-radius: 4px;
      color: #409eff;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}
</style>
