<template>
  <div class="dilution-calc">
    <div class="page-header">
      <h2 class="page-title">溶液稀释倍数计算器</h2>
    </div>

    <div class="page-card">
      <el-form :model="form" label-width="120px" style="max-width: 500px">
        <el-form-item label="原始浓度">
          <el-input-number
            v-model="form.original_concentration"
            :min="0"
            :precision="4"
            :controls="false"
            placeholder="请输入原始浓度"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="目标浓度">
          <el-input-number
            v-model="form.target_concentration"
            :min="0"
            :precision="4"
            :controls="false"
            placeholder="请输入目标浓度"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCalc" :loading="loading">
            计算稀释倍数
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-divider v-if="result !== null" />

      <el-descriptions
        v-if="result !== null"
        title="计算结果"
        :column="1"
        border
        style="max-width: 500px"
      >
        <el-descriptions-item label="原始浓度">
          {{ result.original_concentration }}
        </el-descriptions-item>
        <el-descriptions-item label="目标浓度">
          {{ result.target_concentration }}
        </el-descriptions-item>
        <el-descriptions-item label="稀释倍数">
          <el-tag type="success" size="large">{{ result.dilution_factor }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'

const loading = ref(false)
const result = ref(null)

const form = reactive({
  original_concentration: undefined,
  target_concentration: undefined
})

async function handleCalc() {
  if (form.original_concentration === undefined || form.target_concentration === undefined) {
    ElMessage.warning('请输入原始浓度和目标浓度')
    return
  }
  loading.value = true
  result.value = null
  try {
    const res = await api.post('/data/dilution-calc/', {
      original_concentration: form.original_concentration,
      target_concentration: form.target_concentration
    })
    result.value = res.data
  } catch (e) {
    if (e.response && e.response.status === 400) {
      ElMessage.error(e.response.data.detail || '参数错误')
    }
  } finally {
    loading.value = false
  }
}

function handleReset() {
  form.original_concentration = undefined
  form.target_concentration = undefined
  result.value = null
}
</script>

<style lang="scss" scoped>
.dilution-calc {
  .page-card {
    padding: 24px;
  }
}
</style>
