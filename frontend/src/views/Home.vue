<template>
  <AppLayout>
    <h1 style="margin-bottom: 24px; font-size: 24px;">工具集</h1>
    <el-row :gutter="20">
      <el-col v-for="tool in tools" :key="tool.path" :xs="24" :sm="12" :md="8" :lg="6">
        <el-card
          shadow="hover"
          class="tool-card"
          @click="$router.push(tool.path)"
        >
          <div class="tool-icon">{{ tool.icon }}</div>
          <div class="tool-name">{{ tool.name }}</div>
          <div class="tool-desc">{{ tool.desc }}</div>
        </el-card>
      </el-col>
    </el-row>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/common/AppLayout.vue'

const tools = [
  { path: '/office/pdf-to-word', icon: '📄', name: 'PDF 转 Word', desc: '将 PDF 文件转换为可编辑的 Word 文档' },
  { path: '/office/pdf-merge', icon: '📎', name: 'PDF 合并', desc: '将多个 PDF 文件合并为一个' },
  { path: '/office/pdf-split', icon: '✂️', name: 'PDF 拆分', desc: '将 PDF 按页数或份数拆分' },
  { path: '/office/pdf-to-image', icon: '🖼️', name: 'PDF 转图片', desc: '将 PDF 每页导出为图片' },
  { path: '/office/word-to-pdf', icon: '📝', name: 'Word 转 PDF', desc: '将 Word 文档转换为 PDF' },
  { path: '/office/markdown-convert', icon: '📋', name: 'Markdown 转换', desc: '将 Markdown 转为 PDF 或 Word' },
]
</script>

<style scoped>
.tool-card {
  cursor: pointer;
  text-align: center;
  margin-bottom: 20px;
  transition: transform 0.2s;
}
.tool-card:hover {
  transform: translateY(-4px);
}
.tool-icon { font-size: 36px; margin-bottom: 8px; }
.tool-name { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.tool-desc { font-size: 13px; color: #909399; }
</style>
