# Office 工具集 Implementation Plan

> **状态：✅ 已完成** | 完成日期：2026-05-28
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 project_tools 的 Office 文档处理模块，包含 PDF 转 Word、PDF 合并/拆分、PDF 转图片、Word 转 PDF、Markdown 转换 6 个工具。

**Architecture:** Vue 3 + Element Plus 前端 SPA，Python FastAPI 后端，模块化架构（后端 `modules/office/`，前端 `views/office/`），通用组件共享。

**Tech Stack:** Vue 3, TypeScript, Element Plus, Vite / FastAPI, pdfplumber, pypdf, python-docx, pdf2image, markdown, weasyprint

---

### Task 1: 后端项目骨架

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/router.py`
- Create: `backend/app/core/file_utils.py`

- [x] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-multipart==0.0.19
pdfplumber==0.11.4
python-docx==1.1.2
pypdf==5.1.0
pdf2image==1.17.0
markdown==3.7
weasyprint==63.1
```

- [x] **Step 2: 创建 backend/app/__init__.py**（空文件）

- [x] **Step 3: 创建 backend/app/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.router import register_routers
from app.core.file_utils import start_cleanup_scheduler, stop_cleanup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_cleanup_scheduler()
    yield
    stop_cleanup_scheduler()


app = FastAPI(title="Project Tools", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routers(app)
```

- [x] **Step 4: 创建 backend/app/core/__init__.py**（空文件）

- [x] **Step 5: 创建 backend/app/core/file_utils.py**

```python
import shutil
import time
from pathlib import Path

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

_timer = None


def get_temp_path(filename: str) -> Path:
    return TEMP_DIR / f"{int(time.time() * 1000)}_{filename}"


def cleanup_expired(max_age_seconds: int = 1800):
    now = time.time()
    for f in TEMP_DIR.iterdir():
        if f.is_file() and now - f.stat().st_mtime > max_age_seconds:
            f.unlink()


def start_cleanup_scheduler():
    import threading

    def _loop():
        while True:
            time.sleep(300)
            cleanup_expired()

    global _timer
    _timer = threading.Thread(target=_loop, daemon=True)
    _timer.start()


def stop_cleanup_scheduler():
    pass
```

- [x] **Step 6: 创建 backend/app/core/router.py**

```python
import importlib
import pkgutil
from pathlib import Path

from fastapi import FastAPI


def register_routers(app: FastAPI):
    modules_path = Path(__file__).parent.parent / "modules"
    for module_info in pkgutil.iter_modules([str(modules_path)]):
        mod = importlib.import_module(f"app.modules.{module_info.name}.router")
        if hasattr(mod, "router"):
            prefix = f"/api/{module_info.name}"
            app.include_router(mod.router, prefix=prefix)
```

---

### Task 2: 后端 Office 模块 - PDF 服务

**Files:**
- Create: `backend/app/modules/__init__.py`（空文件）
- Create: `backend/app/modules/office/__init__.py`（空文件）
- Create: `backend/app/modules/office/services/__init__.py`（空文件）
- Create: `backend/app/modules/office/services/pdf.py`

- [x] **Step 1: 创建所有目录和空 __init__.py 文件**

- [x] **Step 2: 创建 PDF 服务**

```python
import io
import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.core.file_utils import get_temp_path


def pdf_merge(file_paths: list[Path]) -> Path:
    writer = PdfWriter()
    for fp in file_paths:
        reader = PdfReader(str(fp))
        for page in reader.pages:
            writer.add_page(page)
    output = get_temp_path("merged.pdf")
    writer.write(str(output))
    return output


def pdf_split(file_path: Path, mode: str, pages: str) -> Path:
    reader = PdfReader(str(file_path))
    total = len(reader.pages)
    ranges = _parse_split_ranges(mode, pages, total)

    zip_path = get_temp_path("split.zip")
    with zipfile.ZipFile(str(zip_path), "w") as zf:
        for i, (start, end) in enumerate(ranges):
            writer = PdfWriter()
            for p in range(start, end + 1):
                writer.add_page(reader.pages[p])
            buf = io.BytesIO()
            writer.write(buf)
            zf.writestr(f"part_{i + 1:03d}.pdf", buf.getvalue())
    return zip_path


def _parse_split_ranges(mode: str, pages: str, total: int) -> list[tuple[int, int]]:
    if mode == "range":
        ranges = []
        for part in pages.split(","):
            start, end = part.split("-")
            ranges.append((int(start) - 1, int(end) - 1))
        return ranges
    if mode == "count":
        count = int(pages)
        return [(i, min(i + count - 1, total - 1)) for i in range(0, total, count)]
    if mode == "parts":
        parts = int(pages)
        per_part = total // parts
        remainder = total % parts
        ranges = []
        start = 0
        for i in range(parts):
            size = per_part + (1 if i < remainder else 0)
            end = start + size - 1
            ranges.append((start, end))
            start = end + 1
        return ranges
    return []


def pdf_to_word(file_path: Path) -> Path:
    import pdfplumber
    from docx import Document

    doc = Document()
    with pdfplumber.open(str(file_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                doc.add_paragraph(text)
    output = get_temp_path("converted.docx")
    doc.save(str(output))
    return output


def pdf_to_image(file_path: Path, fmt: str = "png") -> Path:
    from pdf2image import convert_from_path

    images = convert_from_path(str(file_path))
    zip_path = get_temp_path("images.zip")
    with zipfile.ZipFile(str(zip_path), "w") as zf:
        for i, img in enumerate(images):
            buf = io.BytesIO()
            img.save(buf, format=fmt.upper())
            zf.writestr(f"page_{i + 1:03d}.{fmt}", buf.getvalue())
    return zip_path
```

---

### Task 3: 后端 Office 模块 - 转换服务

**Files:**
- Create: `backend/app/modules/office/services/convert.py`

- [x] **Step 1: 创建转换服务**

```python
from pathlib import Path

from docx import Document

from app.core.file_utils import get_temp_path


def word_to_pdf(file_path: Path) -> Path:
    from docx2pdf import convert
    output = get_temp_path("converted.pdf")
    convert(str(file_path), str(output))
    return output


def markdown_convert(text: str, output_format: str) -> Path:
    import markdown

    html = markdown.markdown(text, extensions=["tables", "fenced_code", "codehilite"])

    if output_format == "pdf":
        from weasyprint import HTML
        output = get_temp_path("converted.pdf")
        HTML(string=html).write_pdf(str(output))
        return output

    if output_format == "docx":
        from htmldocx import HtmlToDocx
        doc = Document()
        HtmlToDocx().add_html_to_document(html, doc)
        output = get_temp_path("converted.docx")
        doc.save(str(output))
        return output

    raise ValueError(f"Unsupported format: {output_format}")
```

---

### Task 4: 后端 Office 模块 - 路由

**Files:**
- Create: `backend/app/modules/office/router.py`

- [x] **Step 1: 创建 Office 路由**

```python
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.core.file_utils import get_temp_path
from app.modules.office.services.pdf import pdf_merge, pdf_split, pdf_to_word, pdf_to_image
from app.modules.office.services.convert import word_to_pdf, markdown_convert

router = APIRouter()


def _save_temp(upload: UploadFile, suffix: str) -> Path:
    path = get_temp_path(f"upload_{suffix}")
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


@router.post("/pdf/to-word")
async def pdf_to_word_api(file: UploadFile = File(...)):
    tmp = _save_temp(file, ".pdf")
    result = pdf_to_word(tmp)
    return FileResponse(result, filename=result.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@router.post("/pdf/merge")
async def pdf_merge_api(files: list[UploadFile] = File(...)):
    paths = [_save_temp(f, ".pdf") for f in files]
    result = pdf_merge(paths)
    return FileResponse(result, filename="merged.pdf", media_type="application/pdf")


@router.post("/pdf/split")
async def pdf_split_api(
    file: UploadFile = File(...),
    mode: str = Form(...),
    pages: str = Form(...),
):
    tmp = _save_temp(file, ".pdf")
    result = pdf_split(tmp, mode, pages)
    return FileResponse(result, filename="split.zip", media_type="application/zip")


@router.post("/pdf/to-image")
async def pdf_to_image_api(
    file: UploadFile = File(...),
    fmt: str = Form(default="png"),
):
    tmp = _save_temp(file, ".pdf")
    result = pdf_to_image(tmp, fmt)
    return FileResponse(result, filename="images.zip", media_type="application/zip")


@router.post("/convert/word-to-pdf")
async def word_to_pdf_api(file: UploadFile = File(...)):
    tmp = _save_temp(file, ".docx")
    result = word_to_pdf(tmp)
    return FileResponse(result, filename=result.name, media_type="application/pdf")


@router.post("/convert/markdown")
async def markdown_convert_api(
    text: str = Form(default=""),
    output_format: str = Form(...),
    file: UploadFile | None = None,
):
    if file:
        content = (await file.read()).decode("utf-8")
    else:
        content = text
    result = markdown_convert(content, output_format)
    media_type = "application/pdf" if output_format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(result, filename=result.name, media_type=media_type)
```

---

### Task 5: 前端项目骨架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/styles/global.css`

- [x] **Step 1: 创建 package.json**

```json
{
  "name": "project-tools",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.0",
    "element-plus": "^2.9.1",
    "axios": "^1.7.9"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "typescript": "^5.7.2",
    "vite": "^6.0.5",
    "vue-tsc": "^2.2.0"
  }
}
```

- [x] **Step 2: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Project Tools</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [x] **Step 3: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [x] **Step 4: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noEmit": true,
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.vue"]
}
```

- [x] **Step 5: 创建 src/main.ts**

```typescript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './styles/global.css'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
```

- [x] **Step 6: 创建 src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [x] **Step 7: 创建 src/styles/global.css**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
```

---

### Task 6: 前端路由和首页

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/views/Home.vue`

- [x] **Step 1: 创建路由**

```typescript
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
```

- [x] **Step 2: 创建首页 Home.vue**

```vue
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
```

---

### Task 7: 前端通用组件

**Files:**
- Create: `frontend/src/components/common/AppLayout.vue`
- Create: `frontend/src/components/common/FileUploader.vue`
- Create: `frontend/src/components/common/ResultPanel.vue`

- [x] **Step 1: 创建 AppLayout.vue**

```vue
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
```

- [x] **Step 2: 创建 FileUploader.vue**

```vue
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
</script>
```

- [x] **Step 3: 创建 ResultPanel.vue**

```vue
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
```

---

### Task 8: 前端 Office API 封装

**Files:**
- Create: `frontend/src/api/office.ts`

- [x] **Step 1: 创建 API 封装**

```typescript
import axios from 'axios'

const api = axios.create({ baseURL: '/api/office' })

export async function pdfToWord(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/pdf/to-word', form, { responseType: 'blob' })
  return res.data
}

export async function pdfMerge(files: File[]) {
  const form = new FormData()
  files.forEach(f => form.append('files', f))
  const res = await api.post('/pdf/merge', form, { responseType: 'blob' })
  return res.data
}

export async function pdfSplit(file: File, mode: string, pages: string) {
  const form = new FormData()
  form.append('file', file)
  form.append('mode', mode)
  form.append('pages', pages)
  const res = await api.post('/pdf/split', form, { responseType: 'blob' })
  return res.data
}

export async function pdfToImage(file: File, fmt: string = 'png') {
  const form = new FormData()
  form.append('file', file)
  form.append('fmt', fmt)
  const res = await api.post('/pdf/to-image', form, { responseType: 'blob' })
  return res.data
}

export async function wordToPdf(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/convert/word-to-pdf', form, { responseType: 'blob' })
  return res.data
}

export async function markdownConvert(text: string, outputFormat: string, file?: File) {
  const form = new FormData()
  form.append('output_format', outputFormat)
  if (file) {
    form.append('file', file)
  } else {
    form.append('text', text)
  }
  const res = await api.post('/convert/markdown', form, { responseType: 'blob' })
  return res.data
}
```

---

### Task 9: PdfToWord 页面

**Files:**
- Create: `frontend/src/views/office/PdfToWord.vue`

- [x] **Step 1: 创建 PdfToWord.vue**

```vue
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
```

---

### Task 10: PdfMerge 页面

**Files:**
- Create: `frontend/src/views/office/PdfMerge.vue`

- [x] **Step 1: 创建 PdfMerge.vue**

```vue
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
```

---

### Task 11: PdfSplit 页面

**Files:**
- Create: `frontend/src/views/office/PdfSplit.vue`

- [x] **Step 1: 创建 PdfSplit.vue**

```vue
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
```

---

### Task 12: PdfToImage 页面

**Files:**
- Create: `frontend/src/views/office/PdfToImage.vue`

- [x] **Step 1: 创建 PdfToImage.vue**

```vue
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
```

---

### Task 13: WordToPdf 页面

**Files:**
- Create: `frontend/src/views/office/WordToPdf.vue`

- [x] **Step 1: 创建 WordToPdf.vue**

```vue
<template>
  <AppLayout>
    <h2 style="margin-bottom: 20px;">Word 转 PDF</h2>
    <FileUploader
      accept=".docx"
      tip="仅支持 .docx 文件"
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
import { wordToPdf } from '@/api/office'

const loading = ref(false)
const result = reactive<{ status: '' | 'success' | 'error'; fileName?: string; errorMessage?: string }>({ status: '' })

async function handleSubmit(files: any[]) {
  loading.value = true
  result.status = ''
  try {
    const blob = await wordToPdf(files[0].raw)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = files[0].name.replace(/\.docx$/i, '') + '.pdf'
    a.click()
    URL.revokeObjectURL(url)
    result.status = 'success'
    result.fileName = files[0].name.replace(/\.docx$/i, '') + '.pdf'
  } catch (e: any) {
    result.status = 'error'
    result.errorMessage = e.message || '转换失败'
  } finally {
    loading.value = false
  }
}
</script>
```

---

### Task 14: MarkdownConvert 页面

**Files:**
- Create: `frontend/src/views/office/MarkdownConvert.vue`

- [x] **Step 1: 创建 MarkdownConvert.vue**

```vue
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
        <el-radio-group v-model="outputFormat">
          <el-radio value="pdf">PDF</el-radio>
          <el-radio value="docx">Word</el-radio>
        </el-radio-group>
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

const inputMode = ref('text')
const text = ref('')
const outputFormat = ref('pdf')
const loading = ref(false)
const result = reactive<{ status: '' | 'success' | 'error'; fileName?: string; errorMessage?: string }>({ status: '' })

async function handleTextSubmit() {
  loading.value = true
  result.status = ''
  try {
    const blob = await markdownConvert(text.value, outputFormat.value)
    triggerDownload(blob, 'converted.' + outputFormat.value)
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
```

---

### Task 15: 安装依赖并验证启动

- [x] **Step 1: 安装 Python 依赖**

```bash
cd backend && pip install -r requirements.txt
```

- [x] **Step 2: 启动后端验证**

```bash
cd backend && python -m uvicorn app.main:app --reload --port 8000
```

Expected: 访问 http://localhost:8000/docs 可见 Swagger 文档，列出所有 API。

- [x] **Step 3: 安装前端依赖**

```bash
cd frontend && npm install
```

- [x] **Step 4: 启动前端验证**

```bash
cd frontend && npm run dev
```

Expected: Vite 启动成功，访问 http://localhost:3000 可见首页工具卡片。

---

### Task 16: 功能联调验证

- [x] **Step 1: 测试 PDF 转 Word** — 准备一个 .pdf，上传转换，验证下载的 .docx 可正常打开
- [x] **Step 2: 测试 PDF 合并** — 选择 2-3 个 PDF，合并后验证页数正确
- [x] **Step 3: 测试 PDF 拆分** — 分别用三种拆分方式测试，验证结果
- [x] **Step 4: 测试 PDF 转图片** — 分别选 PNG/JPG 格式，解压验证图片
- [x] **Step 5: 测试 Word 转 PDF** — 上传 .docx，验证 PDF 内容正确
- [x] **Step 6: 测试 Markdown 转换** — 粘贴文本和上传文件两种方式，分别转 PDF/Word
