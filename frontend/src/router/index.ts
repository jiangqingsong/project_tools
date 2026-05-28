import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  {
    path: '/office/pdf-to-word',
    name: 'PdfToWord',
    component: () => import('@/views/office/PdfToWord.vue'),
  },
  {
    path: '/office/pdf-merge',
    name: 'PdfMerge',
    component: () => import('@/views/office/PdfMerge.vue'),
  },
  {
    path: '/office/pdf-split',
    name: 'PdfSplit',
    component: () => import('@/views/office/PdfSplit.vue'),
  },
  {
    path: '/office/pdf-to-image',
    name: 'PdfToImage',
    component: () => import('@/views/office/PdfToImage.vue'),
  },
  {
    path: '/office/word-to-pdf',
    name: 'WordToPdf',
    component: () => import('@/views/office/WordToPdf.vue'),
  },
  {
    path: '/office/markdown-convert',
    name: 'MarkdownConvert',
    component: () => import('@/views/office/MarkdownConvert.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
