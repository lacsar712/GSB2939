<template>
  <el-select
    v-model="internalValue"
    filterable
    clearable
    placeholder="请选择标准方法"
    :loading="loading"
    @change="handleChange"
    style="width: 100%"
  >
    <el-option
      v-for="item in options"
      :key="item.id"
      :label="`${item.method_no} - ${item.method_name}`"
      :value="item.id"
    >
      <div class="method-option">
        <span class="method-no">{{ item.method_no }}</span>
        <span class="method-name">{{ item.method_name }}</span>
        <span class="standard-no">{{ item.standard_no }}</span>
      </div>
    </el-option>
  </el-select>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { api } from '@/utils/api'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const internalValue = ref(props.modelValue)
const loading = ref(false)
const options = ref([])
const allOptions = ref([])

watch(() => props.modelValue, (val) => {
  internalValue.value = val
})

const handleChange = (val) => {
  emit('update:modelValue', val)
  const selected = options.value.find(item => item.id === val)
  emit('change', selected)
}

// Initial fetch to show options
onMounted(async () => {
  try {
    loading.value = true
    const res = await api.get('/tasks/methods/', { params: { limit: 1000 } })
    options.value = res.data.items || []
    
    if (props.modelValue) {
      // Check if current options contain the selected value
      const exists = options.value.find(item => item.id === props.modelValue)
      if (!exists) {
        // Fetch the specific method if not in the list (though with limit 1000 it should be)
        try {
          const methodRes = await api.get(`/tasks/methods/${props.modelValue}`)
          if (methodRes.data) {
            options.value.push(methodRes.data)
          }
        } catch (err) {
          console.error(err)
        }
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.method-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.method-no {
  font-weight: bold;
  color: #333;
}
.method-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.standard-no {
  color: #999;
  font-size: 12px;
}
</style>
