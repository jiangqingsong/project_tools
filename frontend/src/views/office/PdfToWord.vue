<template>
  <AppLayout>
    <h2 style="margin-bottom: 20px;">PDF 转 Word</h2>
    <FileUploader
      accept=".pdf"
      tip="仅支持 .pdf 文件，大小不超过 50MB"
      submit-text="开始转换"
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
import { pdfToWord } from '@/api/office'

const loading = ref(false)
const result = reactive<{ status: '' | 'success' | 'error'; fileName?: string; errorMessage?: string }>({ status: '' })

async function handleSubmit(files: any[]) {
  loading.value = true
  result.status = ''
  try {
    const blob = await pdfToWord(files[0].raw)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = files[0].name.replace(/\.pdf$/i, '') + '.docx'
    a.click()
    URL.revokeObjectURL(url)
    result.status = 'success'
    result.fileName = files[0].name.replace(/\.pdf$/i, '') + '.docx'
  } catch (e: any) {
    result.status = 'error'
    result.errorMessage = e.message || '转换失败'
  } finally {
    loading.value = false
  }
}
</script>
