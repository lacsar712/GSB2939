<template>
  <div class="dilution-calculator">
    <div class="page-header">
      <h2 class="page-title">溶液稀释倍数计算器</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">输入参数</h3>
          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-width="120px"
            @submit.prevent="handleCalculate"
          >
            <el-form-item label="原始浓度" prop="original_concentration">
              <el-input-number
                v-model="formData.original_concentration"
                :min="0"
                :precision="4"
                :step="0.1"
                :controls="false"
                placeholder="请输入原始浓度"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="目标浓度" prop="target_concentration">
              <el-input-number
                v-model="formData.target_concentration"
                :min="0"
                :precision="4"
                :step="0.1"
                :controls="false"
                placeholder="请输入目标浓度"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleCalculate">
                计算稀释倍数
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">计算结果</h3>
          <el-empty v-if="!result" description="请填写参数后点击计算" />
          <el-descriptions v-else :column="1" border>
            <el-descriptions-item label="原始浓度">
              {{ result.original_concentration }}
            </el-descriptions-item>
            <el-descriptions-item label="目标浓度">
              {{ result.target_concentration }}
            </el-descriptions-item>
            <el-descriptions-item label="稀释倍数">
              <el-tag type="success" size="large">
                {{ result.dilution_factor }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const formRef = ref(null)
const loading = ref(false)
const result = ref(null)

const formData = reactive({
  original_concentration: null,
  target_concentration: null
})

const formRules = {
  original_concentration: [
    { required: true, message: '请输入原始浓度', trigger: 'blur' }
  ],
  target_concentration: [
    { required: true, message: '请输入目标浓度', trigger: 'blur' }
  ]
}

async function handleCalculate() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }

  loading.value = true
  try {
    const { data } = await api.post('/data/dilution/calculate', {
      original_concentration: formData.original_concentration,
      target_concentration: formData.target_concentration
    })
    result.value = data
    ElMessage.success('计算成功')
  } catch (error) {
    result.value = null
  } finally {
    loading.value = false
  }
}

function handleReset() {
  formRef.value?.resetFields()
  formData.original_concentration = null
  formData.target_concentration = null
  result.value = null
}
</script>

<style lang="scss" scoped>
.dilution-calculator {
  .page-header {
    margin-bottom: 20px;

    .page-title {
      margin: 0;
      font-size: 20px;
      color: #303133;
    }
  }

  .page-card {
    background: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);

    .card-title {
      margin: 0 0 20px 0;
      font-size: 16px;
      color: #303133;
      border-left: 3px solid #409eff;
      padding-left: 10px;
    }
  }
}
</style>
