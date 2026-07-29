# Data Processing API — 文档转换与数据处理服务

## 📦 项目简介

一个生产级的文档转换 API 服务，支持 PDF 转文本、Excel 转 CSV、Word 转 Markdown 等常用数据格式互转。

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（修改 config.yaml）

# 3. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8001

# 4. Docker 部署
docker build -t data-processing-api .
docker run -p 8001:8001 data-processing-api
```

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/convert/pdf-to-text` | PDF 转文本 |
| POST | `/convert/excel-to-csv` | Excel 转 CSV |
| POST | `/convert/docx-to-markdown` | Word 转 Markdown |
| GET | `/stats/{doc_id}` | 查询处理记录 |

### 请求示例（PDF 转文本）

```bash
curl -X POST http://localhost:8001/convert/pdf-to-text \
  -H "X-API-Key: your-api-key-here" \
  -F "file=@document.pdf"
```

---

## 💼 产品描述（可用于接单平台）

### 服务名称：Data Processing API — 文档智能转换引擎

**服务描述：**
为企业提供稳定的文档数据转换 API 服务。一键完成 PDF、Excel、Word 等常见办公文件格式互转，提取结构化数据，大幅降低人工操作成本。

**核心功能：**
- ✅ PDF 转纯文本（保留分页结构）
- ✅ Excel 多 Sheet 转 CSV
- ✅ Word 文档转 Markdown（含标题层级、表格解析）
- ✅ 文件安全上传+临时清理
- ✅ 每个任务生成唯一 Job ID，方便追踪

**适用场景：**
- 企业知识库文档批量转换
- 财务报表自动化处理
- 合同/文档信息抽取
- 内容管理系统 (CMS) 数据导入

**定价建议：**
- 按次计费：¥0.5 - ¥2 / 次转换
- 包月套餐：¥299/月起（不限次数）
- 私有部署：¥5,000 - ¥20,000（一次性项目费）

---

## 🔧 技术栈

- Python 3.11+, FastAPI
- pdfplumber / openpyxl / python-docx
- Pandas 数据处理
- Docker 容器化

## 📄 License

MIT
