<template>
  <AppLayout>
    <h2 style="margin-bottom: 20px;">PDF 转图片</h2>
    <el-form label-width="100px" style="max-width: 400px; margin-bottom: 20px;">
      <el-form-item label="图片格式">
        <el-radio-group v-model="fmt">
          <el-radio value="png">PNG</el-radio>
          <el-radio value="jpg">JPG</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <FileUploader
      accept=".pdf"
      tip="选择要转换的 PDF 文件"
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
import { pdfToImage } from '@/api/office'

const fmt = ref('png')
const loading = ref(false)
const result = reactive<{ status: '' | 'success' | 'error'; fileName?: string; errorMessage?: string }>({ status: '' })

async function handleSubmit(files: any[]) {
  loading.value = true
  result.status = ''
  try {
    const blob = await pdfToImage(files[0].raw, fmt.value)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'images.zip'
    a.click()
    URL.revokeObjectURL(url)
    result.status = 'success'
    result.fileName = 'images.zip'
  } catch (e: any) {
    result.status = 'error'
    result.errorMessage = e.message || '转换失败'
  } finally {
    loading.value = false
  }
}
</script>
