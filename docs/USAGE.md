# Project Tools 使用文档

## 环境要求

- Python 3.11+
- Node.js 18+
- Windows / macOS / Linux

## 快速开始

### 1. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 启动服务

打开两个终端：

```bash
# 终端1 - 启动后端（端口 8000）
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 终端2 - 启动前端（端口 3000）
cd frontend
npm run dev
```

浏览器打开 `http://localhost:3000` 即可使用。

## 工具说明

### PDF 转 Word

将 PDF 文件转换为可编辑的 Word 文档。

- 支持格式：`.pdf`
- 输出格式：`.docx`
- 说明：提取 PDF 中的文本内容生成 Word，不保留原始排版

### PDF 合并

将多个 PDF 文件合并为一个。

- 支持格式：`.pdf`（可多选）
- 输出格式：`.pdf`
- 说明：按上传顺序合并，可拖拽调整顺序

### PDF 拆分

将一个 PDF 按指定方式拆分成多个文件。

- 支持格式：`.pdf`
- 输出格式：`.zip`
- 三种拆分方式：
  - **按页码范围**：指定页码范围，如 `1-3,4-6`
  - **按每份页数**：每 N 页拆一份，如 `5`
  - **按总份数**：均分为 N 份，如 `3`

### PDF 转图片

将 PDF 的每一页导出为图片。

- 支持格式：`.pdf`
- 输出格式：`.zip`（内含 PNG 或 JPG 图片）
- 可选图片格式：PNG / JPG

### Word 转 PDF

将 Word 文档转换为 PDF。

- 支持格式：`.docx`
- 输出格式：`.pdf`
- 依赖：需要本机安装 Microsoft Word 或 LibreOffice

### Markdown 转换

将 Markdown 文本转换为 PDF 或 Word 文档。

- 输入方式：粘贴文本 或 上传 `.md` / `.txt` 文件
- 输出格式：PDF / Word（docx）
- 支持：表格、代码块、代码高亮

## 项目结构

```
project_tools/
├── backend/                 # Python FastAPI 后端
│   └── app/
│       ├── main.py          # 入口
│       ├── core/            # 公共基础设施
│       └── modules/         # 工具模块（按类别隔离）
│           └── office/      # Office 工具模块
├── frontend/                # Vue 3 + Element Plus 前端
│   └── src/
│       ├── views/           # 页面（按类别分目录）
│       ├── components/      # 通用组件
│       └── api/             # API 封装
```

## 添加新工具模块

以后端为例，加一个"图片处理"模块：

1. 在 `backend/app/modules/` 下新建 `image/` 目录
2. 创建 `router.py`，定义一个 `router = APIRouter()` 并注册路由
3. 后端会自动发现并挂载到 `/api/image/`
4. 前端在 `src/views/` 下新建 `image/` 目录，添加页面
5. 在 `src/api/` 新建 API 封装文件
6. 在 `src/router/index.ts` 添加路由

完全隔离，不动现有代码。

## 常见问题

**Q: PDF 转 Word 排版不对？**

A: 当前版本只提取文本内容，不保留原始排版、表格和图片。如需保留排版，可考虑后续集成 LibreOffice 命令行。

**Q: Word 转 PDF 报错？**

A: 此功能依赖 `docx2pdf`，需要本机安装 Microsoft Word（Windows）或 LibreOffice（跨平台）。如果没装，建议用 PDF 打印功能替代。

**Q: 上传大文件很慢？**

A: 文件在前端处理后通过 HTTP 上传到后端，大文件建议压缩后再处理。目前没有文件大小硬性限制。
