<template>
  <AppLayout>
    <h2 style="margin-bottom: 20px;">PDF 拆分</h2>
    <el-form label-width="100px" style="max-width: 500px; margin-bottom: 20px;">
      <el-form-item label="拆分方式">
        <el-radio-group v-model="mode">
          <el-radio value="range">按页码范围</el-radio>
          <el-radio value="count">按每份页数</el-radio>
          <el-radio value="parts">按总份数</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="参数">
        <el-input v-model="pages" :placeholder="mode === 'range' ? '如: 1-3,4-6' : '如: 5'" />
      </el-form-item>
    </el-form>
    <FileUploader
      accept=".pdf"
      tip="选择要拆分的 PDF 文件"
      submit-text="开始拆分"
      :loading="loading"
      @submit="handleSubmit"
    />
    <ResultPanel
      :visible="result.status !== ''"
      :status="result.status"
      :file-name="result.fileName"
      :error-message="result.errorMessage"
      @retry="result.status = ''"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FileUploader from '@/components/common/FileUploader.vue'
import ResultPanel from '@/components/common/ResultPanel.vue'
import { pdfSplit } from '@/api/office'

const mode = ref('range')
const pages = ref('')
const loading = ref(false)
const result = reactive<{ status: '' | 'success' | 'error'; fileName?: string; errorMessage?: string }>({ status: '' })

async function handleSubmit(files: any[]) {
  loading.value = true
  result.status = ''
  try {
    const blob = await pdfSplit(files[0].raw, mode.value, pages.value)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'split.zip'
    a.click()
    URL.revokeObjectURL(url)
    result.status = 'success'
    result.fileName = 'split.zip'
  } catch (e: any) {
    result.status = 'error'
    result.errorMessage = e.message || '拆分失败'
  } finally {
    loading.value = false
  }
}
</script>
