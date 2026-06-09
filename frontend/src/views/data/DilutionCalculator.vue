<template>
  <div class="dilution-calculator">
    <div class="page-header">
      <h2 class="page-title">溶液稀释倍数计算器</h2>
    </div>

    <el-row :gutter="20" justify="center">
      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">浓度参数输入</h3>
          
          <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
            <el-form-item label="原始浓度" prop="original_concentration">
              <el-input-number 
                v-model="formData.original_concentration" 
                :precision="4" 
                :step="0.1"
                :min="0"
                style="width: 100%" 
                placeholder="请输入原始浓度"
              />
            </el-form-item>

            <el-form-item label="目标浓度" prop="target_concentration">
              <el-input-number 
                v-model="formData.target_concentration" 
                :precision="4" 
                :step="0.1"
                :min="0"
                style="width: 100%" 
                placeholder="请输入目标浓度"
              />
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
            <el-descriptions-item label="原始浓度">{{ result.original_concentration }}</el-descriptions-item>
            <el-descriptions-item label="目标浓度">{{ result.target_concentration }}</el-descriptions-item>
            <el-descriptions-item label="稀释倍数">
              <span class="result-value">{{ result.dilution_factor }} 倍</span>
            </el-descriptions-item>
          </el-descriptions>
          <el-alert
            title="使用说明"
            type="info"
            :closable="false"
            style="margin-top: 16px"
          >
            <template #default>
              即取 1 份原始溶液，加入 {{ (result.dilution_factor - 1).toFixed(2) }} 份溶剂进行稀释。
            </template>
          </el-alert>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'

const loading = ref(false)
const formRef = ref(null)
const result = ref(null)

const formData = reactive({
  original_concentration: null,
  target_concentration: null
})

const rules = {
  original_concentration: [
    { required: true, message: '请输入原始浓度', trigger: 'blur' }
  ],
  target_concentration: [
    { required: true, message: '请输入目标浓度', trigger: 'blur' }
  ]
}

async function handleCalculate() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      result.value = null
      try {
        const res = await api.post('/data/dilution-calculator/', formData)
        result.value = res.data
        ElMessage.success('计算成功')
      } catch (e) {
        result.value = null
      } finally {
        loading.value = false
      }
    }
  })
}

function handleReset() {
  formData.original_concentration = null
  formData.target_concentration = null
  result.value = null
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style lang="scss" scoped>
.dilution-calculator {
  .page-card {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  }

  .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 24px;
    color: #303133;
  }

  .result-card {
    .result-value {
      font-size: 24px;
      font-weight: 700;
      color: #409eff;
    }
  }
}
</style>
