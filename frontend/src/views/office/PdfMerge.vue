<template>
  <AppLayout>
    <h2 style="margin-bottom: 20px;">PDF 合并</h2>
    <FileUploader
      accept=".pdf"
      :multiple="true"
      tip="可选择多个 PDF 文件，上传后点击合并"
      submit-text="开始合并"
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
import { pdfMerge } from '@/api/office'

const loading = ref(false)
const result = reactive<{ status: '' | 'success' | 'error'; fileName?: string; errorMessage?: string }>({ status: '' })

async function handleSubmit(files: any[]) {
  loading.value = true
  result.status = ''
  try {
    const blob = await pdfMerge(files.map((f: any) => f.raw))
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'merged.pdf'
    a.click()
    URL.revokeObjectURL(url)
    result.status = 'success'
    result.fileName = 'merged.pdf'
  } catch (e: any) {
    result.status = 'error'
    result.errorMessage = e.message || '合并失败'
  } finally {
    loading.value = false
  }
}
</script>
