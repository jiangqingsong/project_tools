<template>
  <div v-if="visible" style="margin-top: 24px;">
    <el-alert
      v-if="status === 'success'"
      :title="`处理完成：${fileName}`"
      type="success"
      :closable="false"
      show-icon
    />
    <el-alert
      v-if="status === 'error'"
      :title="errorMessage"
      type="error"
      :closable="false"
      show-icon
    >
      <template #default>
        <el-button size="small" @click="$emit('retry')" style="margin-top: 8px;">重试</el-button>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  status: '' | 'success' | 'error'
  fileName?: string
  errorMessage?: string
}>()

defineEmits<{
  retry: []
}>()
</script>
