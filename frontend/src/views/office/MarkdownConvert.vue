<template>
  <AppLayout>
    <h2 style="margin-bottom: 20px;">Markdown 转换</h2>
    <el-tabs v-model="inputMode">
      <el-tab-pane label="粘贴文本" name="text">
        <el-input
          v-model="text"
          type="textarea"
          :rows="12"
          placeholder="在此粘贴 Markdown 内容..."
        />
      </el-tab-pane>
      <el-tab-pane label="上传文件" name="file">
        <FileUploader
          ref="fileUploaderRef"
          accept=".md,.txt"
          tip="上传 .md 或 .txt 文件"
          submit-text="开始转换"
          :loading="loading"
          @submit="handleFileSubmit"
        />
      </el-tab-pane>
    </el-tabs>
    <el-form label-width="80px" style="margin: 16px 0;">
      <el-form-item label="输出格式">
        <el-radio-group v-model="outputFormat" @change="onFormatChange">
          <el-radio value="pdf">PDF</el-radio>
          <el-radio value="docx">Word</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="文件名">
        <el-input v-model="filename" placeholder="请输入导出文件名" style="width: 300px;">
          <template #suffix>.{{ outputFormat }}</template>
        </el-input>
      </el-form-item>
    </el-form>
    <div style="text-align: center;" v-if="inputMode === 'text'">
      <el-button type="primary" @click="handleTextSubmit" :loading="loading">开始转换</el-button>
    </div>
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
import { markdownConvert } from '@/api/office'

const fileUploaderRef = ref<InstanceType<typeof FileUploader>>()
const inputMode = ref('text')
const text = ref('')
const outputFormat = ref('pdf')
const filename = ref('')
const loading = ref(false)
const result = reactive<{ status: '' | 'success' | 'error'; fileName?: string; errorMessage?: string }>({ status: '' })

function onFormatChange() {
  filename.value = ''
}

function getDownloadName(): string {
  const base = filename.value.trim() || 'converted'
  return base + '.' + outputFormat.value
}

async function handleTextSubmit() {
  loading.value = true
  result.status = ''
  try {
    const blob = await markdownConvert(text.value, outputFormat.value)
    triggerDownload(blob, getDownloadName())
  } catch (e: any) {
    result.status = 'error'
    result.errorMessage = e.message || '转换失败'
  } finally {
    loading.value = false
  }
}

async function handleFileSubmit(files: any[]) {
  loading.value = true
  result.status = ''
  try {
    const blob = await markdownConvert('', outputFormat.value, files[0].raw)
    const ext = outputFormat.value === 'pdf' ? 'pdf' : 'docx'
    const name = files[0].name.replace(/\.(md|txt)$/i, '') + '.' + ext
    triggerDownload(blob, name)
    fileUploaderRef.value?.clearFiles()
  } catch (e: any) {
    result.status = 'error'
    result.errorMessage = e.message || '转换失败'
  } finally {
    loading.value = false
  }
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
  result.status = 'success'
  result.fileName = filename
}
</script>
