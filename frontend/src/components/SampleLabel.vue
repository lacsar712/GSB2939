<template>
  <div class="sample-label-container">
    <div id="print-area" class="label-card">
      <div class="label-header">
        <span class="company-name">LIMS 实验室管理系统</span>
        <span class="label-type">样品标识卡</span>
      </div>
      <div class="label-body">
        <div class="qr-code">
          <img :src="qrCodeUrl" alt="QR Code" v-if="qrCodeUrl" width="100" height="100" />
        </div>
        <div class="info-list">
          <div class="info-item">
            <span class="label">样品编号：</span>
            <span class="value">{{ sample.sample_no }}</span>
          </div>
          <div class="info-item">
            <span class="label">样品名称：</span>
            <span class="value">{{ sample.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">接收日期：</span>
            <span class="value">{{ formatDate(sample.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">状态：</span>
            <span class="value">{{ sample.status }}</span>
          </div>
        </div>
      </div>
      <div class="label-footer">
        <span class="tip">请妥善保管此标签，扫码可查看详情</span>
      </div>
    </div>
    
    <div class="actions">
      <el-button type="primary" @click="handlePrint">打印标签</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import QRCode from 'qrcode'
import dayjs from 'dayjs'

const props = defineProps({
  sample: {
    type: Object,
    required: true,
    default: () => ({
      sample_no: 'SAMPLE-000000',
      name: '示例样品',
      created_at: new Date(),
      status: '未知'
    })
  }
})

const qrCodeUrl = ref('')

const generateQRCode = async () => {
  if (props.sample.sample_no) {
    try {
      qrCodeUrl.value = await QRCode.toDataURL(props.sample.sample_no, {
        width: 100,
        margin: 1,
        color: {
          dark: '#000000',
          light: '#ffffff'
        }
      })
    } catch (err) {
      console.error('QR Code generation failed', err)
    }
  }
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const handlePrint = () => {
  const printWindow = window.open('', '_blank')
  
  // Get the HTML content of the label card
  const labelContent = document.getElementById('print-area').innerHTML
  
  printWindow.document.write(`
    <html>
      <head>
        <title>打印标签 - ${props.sample.sample_no}</title>
        <style>
          body {
            font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
          }
          .label-card {
            border: 2px solid #000;
            border-radius: 8px;
            padding: 16px;
            width: 320px;
            box-sizing: border-box;
          }
          .label-header {
            text-align: center;
            border-bottom: 1px solid #000;
            padding-bottom: 8px;
            margin-bottom: 12px;
          }
          .company-name {
            font-size: 12px;
            color: #666;
            display: block;
            margin-bottom: 4px;
          }
          .label-type {
            font-size: 18px;
            font-weight: bold;
            color: #000;
            display: block;
          }
          .label-body {
            display: flex;
            align-items: flex-start;
          }
          .qr-code {
            margin-right: 16px;
          }
          .qr-code img {
            width: 100px;
            height: 100px;
            display: block;
          }
          .info-list {
            flex: 1;
            font-size: 13px;
            line-height: 1.5;
          }
          .info-item {
            margin-bottom: 4px;
            display: flex;
          }
          .info-item .label {
            font-weight: bold;
            width: 70px;
            flex-shrink: 0;
          }
          .info-item .value {
            font-weight: 500;
            word-break: break-all;
          }
          .label-footer {
            margin-top: 12px;
            text-align: center;
            font-size: 10px;
            color: #666;
            border-top: 1px solid #000;
            padding-top: 8px;
          }
        </style>
      </head>
      <body>
        <div class="label-card">
          ${labelContent}
        </div>
        <script>
          window.onload = function() {
            window.print();
            window.onafterprint = function() {
              window.close();
            }
          }
        <\/script>
      </body>
    </html>
  `)
  
  printWindow.document.close()
}

onMounted(() => {
  generateQRCode()
})

watch(() => props.sample, () => {
  generateQRCode()
}, { deep: true })
</script>

<style scoped>
.sample-label-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.label-card {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  width: 320px;
  background: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.label-header {
  text-align: center;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
  margin-bottom: 12px;
}

.company-name {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.label-type {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.label-body {
  display: flex;
  align-items: flex-start;
}

.qr-code {
  margin-right: 16px;
}

.info-list {
  flex: 1;
  font-size: 13px;
  line-height: 1.6;
}

.info-item {
  display: flex;
  margin-bottom: 4px;
}

.info-item .label {
  color: #606266;
  width: 70px;
  flex-shrink: 0;
}

.info-item .value {
  color: #303133;
  font-weight: 500;
  word-break: break-all;
}

.label-footer {
  margin-top: 12px;
  text-align: center;
  font-size: 12px;
  color: #909399;
  border-top: 1px solid #ebeef5;
  padding-top: 8px;
}

.actions {
  margin-top: 20px;
}
</style>