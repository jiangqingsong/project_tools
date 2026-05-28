<template>
  <el-container style="min-height: 100vh;">
    <el-header style="display: flex; align-items: center; border-bottom: 1px solid #e4e7ed;">
      <span style="font-size: 18px; font-weight: 700; cursor: pointer;" @click="$router.push('/')">
        Project Tools
      </span>
      <el-breadcrumb separator="/" style="margin-left: 32px;">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentCategory">{{ currentCategory }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentTool">{{ currentTool }}</el-breadcrumb-item>
      </el-breadcrumb>
    </el-header>
    <el-main>
      <slot />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const toolMap: Record<string, { category: string; tool: string }> = {
  PdfToWord: { category: 'Office', tool: 'PDF 转 Word' },
  PdfMerge: { category: 'Office', tool: 'PDF 合并' },
  PdfSplit: { category: 'Office', tool: 'PDF 拆分' },
  PdfToImage: { category: 'Office', tool: 'PDF 转图片' },
  WordToPdf: { category: 'Office', tool: 'Word 转 PDF' },
  MarkdownConvert: { category: 'Office', tool: 'Markdown 转换' },
}

const currentCategory = computed(() => toolMap[route.name as string]?.category ?? '')
const currentTool = computed(() => toolMap[route.name as string]?.tool ?? '')
</script>
