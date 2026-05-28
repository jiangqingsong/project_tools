# Office 工具集 - 设计文档

> 日期：2026-05-28 | 状态：待实施

## 概述

project_tools 是一个日常办公工具集 Web 应用，采用模块化架构，支持按工具类别隔离开发。首期实现 Office 文档处理模块。

## 技术栈

| 层 | 选型 | 说明 |
|---|------|------|
| 前端 | Vue 3 + TypeScript + Element Plus | SPA，组件化开发 |
| 后端 | Python FastAPI | RESTful API，文件处理 |
| 构建 | Vite（前端）/ uvicorn（后端） | |

## 目录结构

```
project_tools/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口，挂载 CORS、静态文件
│   │   ├── core/
│   │   │   ├── router.py            # 自动发现并注册 modules/* 下的子路由
│   │   │   └── file_utils.py        # 临时文件管理、清理
│   │   └── modules/
│   │       └── office/              # Office 工具模块
│   │           ├── __init__.py
│   │           ├── router.py        # /api/office/* 路由汇总
│   │           └── services/
│   │               ├── pdf.py       # PDF 处理核心逻辑
│   │               └── convert.py   # 文档格式转换核心逻辑
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── router/
│   │   │   └── index.ts            # 全局路由，按模块拆分
│   │   ├── views/
│   │   │   ├── Home.vue            # 首页：工具卡片网格
│   │   │   └── office/
│   │   │       ├── PdfToWord.vue
│   │   │       ├── PdfMerge.vue
│   │   │       ├── PdfSplit.vue
│   │   │       ├── PdfToImage.vue
│   │   │       ├── WordToPdf.vue
│   │   │       └── MarkdownConvert.vue
│   │   ├── components/
│   │   │   └── common/
│   │   │       ├── AppLayout.vue    # 整体布局（侧边栏+顶栏+内容区）
│   │   │       ├── FileUploader.vue # 拖拽/点击上传，支持单文件和多文件
│   │   │       └── ResultPanel.vue  # 处理结果展示 + 下载按钮
│   │   ├── api/
│   │   │   └── office.ts           # Office 模块 API 封装
│   │   └── styles/
│   │       └── global.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-05-28-office-tools-design.md  # 本文档
```

## 模块隔离设计

- 后端：`modules/` 下每个子目录是一个独立工具类别，通过 `core/router.py` 自动发现注册。新增模块只需在 `modules/` 下新建目录，添加 `router.py` 即可。
- 前端：`views/` 按类别分目录，`api/` 按类别分文件，路由在 `router/index.ts` 中按模块组织。通用组件放 `components/common/` 供全局复用。
- 首页工具卡片根据已注册模块动态展示。

## 首期功能（Office 模块）

| 功能 | 输入 | 输出 | 说明 |
|------|------|------|------|
| PDF 转 Word | .pdf | .docx | 保留原格式 |
| PDF 合并 | 多个 .pdf | .pdf | 支持拖拽排序 |
| PDF 拆分 | .pdf | .zip（多个pdf） | 按页数或份数拆分 |
| PDF 转图片 | .pdf | .zip（png/jpg） | 可选图片格式 |
| Word 转 PDF | .docx | .pdf | |
| Markdown 转换 | .md / 文本 | .pdf / .docx | 粘贴或上传 |

## 前端路由

| 路径 | 页面 | 组件 |
|------|------|------|
| `/` | Home | 工具卡片网格 |
| `/office/pdf-to-word` | PdfToWord | FileUploader + ResultPanel |
| `/office/pdf-merge` | PdfMerge | FileUploader(多文件) + ResultPanel |
| `/office/pdf-split` | PdfSplit | FileUploader + 拆分选项 + ResultPanel |
| `/office/pdf-to-image` | PdfToImage | FileUploader + 格式选择 + ResultPanel |
| `/office/word-to-pdf` | WordToPdf | FileUploader + ResultPanel |
| `/office/markdown-convert` | MarkdownConvert | 输入框/上传 + 格式选择 + ResultPanel |

## 后端 API

基础路径：`/api/office`

| 方法 | 路径 | 请求 | 响应 |
|------|------|------|------|
| POST | `/pdf/to-word` | multipart: file(.pdf) | FileResponse(.docx) |
| POST | `/pdf/merge` | multipart: files[](.pdf) | FileResponse(.pdf) |
| POST | `/pdf/split` | multipart: file(.pdf) + mode + pages | FileResponse(.zip) |
| POST | `/pdf/to-image` | multipart: file(.pdf) + format | FileResponse(.zip) |
| POST | `/convert/word-to-pdf` | multipart: file(.docx) | FileResponse(.pdf) |
| POST | `/convert/markdown` | multipart: file(.md) or JSON: {text, format} | FileResponse(.pdf/.docx) |

## 核心流程

```
1. 用户在首页选择工具 → 路由跳转
2. 上传文件（拖拽/点击）→ FileUploader 展示文件信息
3. 用户配置参数（拆分方式、图片格式等）
4. 点击"开始转换"→ 前端发送请求到后端
5. 后端处理文件 → 生成结果 → 返回文件流
6. 前端 ResultPanel 展示"处理完成" + 下载按钮
7. 后端定时清理超过 30 分钟的临时文件
```

## 通用组件设计

### FileUploader
- Props: `accept`（文件类型限制）、`multiple`（是否多文件）、`maxSize`（大小限制）
- 支持拖拽上传和点击上传
- 多文件模式下支持拖拽排序
- 展示文件名、大小、上传状态

### ResultPanel
- Props: `status`（loading/success/error）、`fileName`、`downloadUrl`
- loading: 显示处理中动画
- success: 显示文件名 + 下载按钮
- error: 显示错误信息 + 重试按钮

## 后续扩展

加新工具类别时，例如图片处理模块：

```
backend/app/modules/image/       # 新增后端模块
frontend/src/views/image/        # 新增前端页面
frontend/src/api/image.ts        # 新增 API 封装
```

完全隔离，不动现有代码。

## 后端依赖（Python）

- `fastapi` + `uvicorn` - Web 框架
- `python-multipart` - 文件上传
- `pdfplumber` - PDF 文本提取（PDF 转 Word）
- `python-docx` - Word 文件读写
- `PyPDF2` 或 `pypdf` - PDF 合并/拆分
- `pdf2image` - PDF 转图片
- `docx2pdf` 或 `libreoffice` - Word 转 PDF
- `markdown` + `weasyprint` 或 `pandoc` - Markdown 转换
