<template>
  <div class="sample-register">
    <div class="page-header">
      <h2 class="page-title">样品登记</h2>
    </div>

    <div class="page-card">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="register-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="样品名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入样品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="样品来源" prop="source">
              <el-input v-model="formData.source" placeholder="请输入样品来源" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="样品类型" prop="type">
              <el-select v-model="formData.type" placeholder="请选择样品类型" style="width: 100%">
                <el-option label="食品" value="食品" />
                <el-option label="饮用水" value="饮用水" />
                <el-option label="乳制品" value="乳制品" />
                <el-option label="食用油" value="食用油" />
                <el-option label="酒类" value="酒类" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="批次号" prop="batch_no">
              <el-input v-model="formData.batch_no" placeholder="请输入批次号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="formData.quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="formData.unit" placeholder="请选择单位" style="width: 100%">
                <el-option label="mL" value="mL" />
                <el-option label="L" value="L" />
                <el-option label="g" value="g" />
                <el-option label="kg" value="kg" />
                <el-option label="个" value="个" />
                <el-option label="件" value="件" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预期完成日期" prop="expected_date">
              <el-date-picker
                v-model="formData.expected_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">客户信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户名称" prop="customer_name">
              <el-input v-model="formData.customer_name" placeholder="请输入客户名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人" prop="customer_contact">
              <el-input v-model="formData.customer_contact" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="customer_phone">
              <el-input v-model="formData.customer_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            提交登记
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 登记成功弹窗 -->
    <el-dialog v-model="showSuccessDialog" title="登记成功" width="500px">
      <div class="success-content">
        <el-result icon="success" title="样品登记成功">
          <template #sub-title>
            <p>样品编号：<strong>{{ registeredNo }}</strong></p>
          </template>
        </el-result>
        <div class="qrcode-box">
          <div ref="qrcodeRef" class="qrcode"></div>
          <p>扫描二维码查看样品详情</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showSuccessDialog = false">继续登记</el-button>
        <el-button type="primary" @click="goToDetail">查看详情</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'
import QRCode from 'qrcode'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const showSuccessDialog = ref(false)
const registeredNo = ref('')
const registeredId = ref(0)
const qrcodeRef = ref()

const formData = reactive({
  name: '',
  source: '',
  type: '',
  batch_no: '',
  quantity: 0,
  unit: 'mL',
  expected_date: null,
  customer_name: '',
  customer_contact: '',
  customer_phone: '',
  remarks: ''
})

const rules = {
  name: [{ required: true, message: '请输入样品名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择样品类型', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }]
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await api.post('/samples/', formData)
    registeredNo.value = res.data.sample_no
    registeredId.value = res.data.id
    showSuccessDialog.value = true
    
    // 生成二维码
    nextTick(() => {
      QRCode.toCanvas(qrcodeRef.value, `SAMPLE:${res.data.sample_no}`, {
        width: 150,
        margin: 2
      })
    })
    
    ElMessage.success('样品登记成功')
    handleReset()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登记失败')
  } finally {
    loading.value = false
  }
}

function handleReset() {
  formRef.value.resetFields()
}

function goToDetail() {
  router.push(`/sample/detail/${registeredId.value}`)
}
</script>

<style lang="scss" scoped>
.sample-register {
  .register-form {
    max-width: 900px;
  }

  .success-content {
    text-align: center;

    .qrcode-box {
      margin-top: 20px;
      
      .qrcode {
        display: inline-block;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 10px;
      }
      
      p {
        margin-top: 10px;
        color: #909399;
        font-size: 14px;
      }
    }
  }
}
</style>
