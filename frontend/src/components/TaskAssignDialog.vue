<template>
  <el-dialog
    v-model="visible"
    title="任务分配"
    width="500px"
    @open="handleOpen"
    @close="handleClose"
  >
    <el-form :model="form" label-width="100px" v-loading="loading">
      <el-form-item label="检测任务">
        <span>{{ task?.task_no }} - {{ task?.sample_name }}</span>
      </el-form-item>
      <el-form-item label="检测人员" required>
        <el-select v-model="form.testerId" placeholder="请选择检测人员" style="width: 100%" @change="handleTesterChange">
          <el-option
            v-for="item in testerOptions"
            :key="item.id"
            :label="`${item.real_name || item.username} (${item.department || '无部门'})`"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remarks" type="textarea" :rows="2" placeholder="分配备注（选填）" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/utils/api'

const props = defineProps({
  modelValue: Boolean,
  task: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const submitting = ref(false)
const testerOptions = ref([])
const form = reactive({
  testerId: '',
  testerName: '',
  department: '',
  remarks: ''
})

const handleOpen = () => {
  form.testerId = ''
  form.testerName = ''
  form.department = ''
  form.remarks = ''
  fetchTesters()
}

const handleClose = () => {
  // Reset handled by open or manual reset if needed
}

const fetchTesters = async () => {
  loading.value = true
  try {
    // Fetch users with role 'tester'
    // Note: API might support role filter directly or we filter client side
    // Based on Assign.vue, it filters client side if API doesn't fully support it, 
    // but let's try passing role parameter first as per Assign.vue usage
    const res = await api.get('/users/', { params: { role: 'tester', limit: 100 } })
    // Filter locally just in case backend doesn't filter strict enough or returns all
    testerOptions.value = (res.data.items || res.data || []).filter(u => 
      u.roles?.some(r => r.code === 'tester') || u.role === 'tester'
    )
  } catch (e) {
    console.error(e)
    ElMessage.error('获取检测人员列表失败')
  } finally {
    loading.value = false
  }
}

const handleTesterChange = (val) => {
  const tester = testerOptions.value.find(t => t.id === val)
  if (tester) {
    form.testerName = tester.real_name || tester.username
    form.department = tester.department
  }
}

const handleConfirm = async () => {
  if (!form.testerId) {
    ElMessage.warning('请选择检测人员')
    return
  }

  submitting.value = true
  try {
    await api.post(`/tasks/${props.task.id}/assign`, {
      task_id: props.task.id,
      user_id: form.testerId,
      user_name: form.testerName,
      department: form.department,
      remarks: form.remarks
    })
    ElMessage.success('分配成功')
    visible.value = false
    emit('success')
  } catch (e) {
    console.error(e)
    ElMessage.error('分配失败')
  } finally {
    submitting.value = false
  }
}
</script>
