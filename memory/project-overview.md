---
name: project-overview
description: 项目全貌——架构、启动方式、技术栈、目录结构，新 session 快速上手
metadata:
  type: reference
---

# Project Tools - Office 工具集

## 一句话

一个 Web 版 Office 文档处理工具箱，前端 Vue3 + ElementPlus，后端 Python FastAPI。

## 技术栈

- 前端：Vue 3 + TypeScript + Element Plus + Vite，端口 3000
- 后端：Python FastAPI + uvicorn，端口 8000
- 前端 /api 代理到后端 localhost:8000
- 后端日志：`backend/logs/app.log`（RotatingFileHandler，10MB×5，同时输出控制台）

## 启动方式

```bash
# 后端（端口 8000）
cd backend
pip install -r requirements.txt  # 首次
python -m uvicorn app.main:app --reload --port 8000

# 前端（端口 3000）
cd frontend
npm install   # 首次
npm run dev
```

浏览器打开 http://localhost:3000

## 目录结构

```
project_tools/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口，lifespan 管理清理调度
│   │   ├── core/
│   │   │   ├── file_utils.py    # 临时文件清理
│   │   │   └── router.py       # 自动发现并注册模块路由 → /api/{module}/
│   │   └── modules/
│   │       └── office/          # Office 工具模块
│   │           ├── router.py    # 路由定义
│   │           └── services/    # 业务逻辑
│   │               ├── convert.py  # 格式转换（pdf↔word, markdown）
│   │               └── pdf.py      # PDF 合并/拆分/转图片
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── main.ts              # Vue 入口，挂载 ElementPlus + Router
│       ├── App.vue
│       ├── router/index.ts      # 路由：/ /office/pdf-to-word /office/pdf-merge ...
│       ├── api/office.ts        # 后端 API 封装（axios）
│       ├── views/
│       │   ├── Home.vue
│       │   └── office/          # PdfToWord, PdfMerge, PdfSplit, PdfToImage, WordToPdf, MarkdownConvert
│       ├── components/common/   # AppLayout, FileUploader, ResultPanel
│       └── styles/global.css
├── main.py                      # 空壳，PyCharm 生成的示例文件，无实际用途
├── docs/USAGE.md                # 使用文档
└── CLAUDE.md                    # 项目级 Claude 指令（沟通/Git/编码规则）
```

## 已实现功能（6个工具）

1. PDF 转 Word — pdfplumber 提取文本 → python-docx 生成
2. PDF 合并 — pypdf 按序合并
3. PDF 拆分 — 按页码范围/每份页数/总份数拆分
4. PDF 转图片 — pdf2image + poppler，输出 PNG/JPG
5. Word 转 PDF — mammoth + weasyprint 纯 Python 方案，不需要外部软件
6. Markdown 转换 — markdown + weasyprint → PDF/Word

## 模块化设计

后端 `core/router.py` 自动扫描 `modules/` 下每个子目录的 `router.py`，挂载到 `/api/{目录名}/`。新增工具模块只需在 `modules/` 下建目录加 `router.py`，不动现有代码。

## Git 历史

- 55bb2e9: 项目初始化，Office 工具集首期（6个工具）
- a69b7d0: 实施计划进度更新
- 09f9402: 添加使用文档和记忆系统
