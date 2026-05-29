<template>
  <div>
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :accept="accept"
      :multiple="multiple"
      :limit="multiple ? 20 : 1"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :file-list="fileList"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">{{ tip }}</div>
      </template>
    </el-upload>
    <div style="margin-top: 16px; text-align: center;" v-if="fileList.length > 0">
      <el-button type="primary" @click="$emit('submit', fileList)" :loading="loading">
        {{ submitText }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile, UploadUserFile } from 'element-plus'

defineProps<{
  accept: string
  multiple?: boolean
  tip: string
  submitText: string
  loading: boolean
}>()

defineEmits<{
  submit: [files: UploadUserFile[]]
}>()

const fileList = ref<UploadUserFile[]>([])

const handleChange = (_file: UploadFile, list: UploadUserFile[]) => {
  fileList.value = list
}

const handleRemove = (_file: UploadFile, list: UploadUserFile[]) => {
  fileList.value = list
}

function clearFiles() {
  fileList.value = []
}

defineExpose({ clearFiles })
</script>
