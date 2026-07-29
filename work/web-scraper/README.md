# Web Scraper API — 自动化网页抓取与数据提取服务

## 📦 项目简介

一个生产级自动化爬虫 API 服务，支持单页抓取、多字段提取、反反爬机制，抓取结果自动持久化到 SQLite。

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8002

# 3. Docker 部署
docker build -t web-scraper-api .
docker run -p 8002:8002 web-scraper-api
```

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/scrape/url` | 抓取单个网页 |
| GET | `/jobs/{job_id}` | 查询抓取任务状态 |

### 请求示例

```bash
curl -X POST http://localhost:8002/scrape/url \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "url": "https://example.com",
    "extract_fields": ["title", "paragraphs", "links"]
  }'
```

---

## 💼 产品描述（可用于接单平台）

### 服务名称：Web Scraper API — 自动化数据采集引擎

**服务描述：**
为您提供稳定的网页数据采集 API 服务。内置反反爬机制（随机 User-Agent、请求延迟），自动提取标题、段落、链接等结构化内容，结果实时可查。

**核心功能：**
- ✅ 智能反反爬（随机 UA + 请求间隔 + 自动重试）
- ✅ 多种字段提取（标题、正文、链接、 headings）
- ✅ 抓取任务持久化到 SQLite，随时查询状态
- ✅ 容器化部署，开箱即用

**适用场景：**
- 竞品价格监控与数据分析
- 市场调研信息批量采集
- 舆情监控与新闻聚合
- 网站结构化数据提取

**定价建议：**
- 按次计费：¥0.3 - ¥1 / 次抓取
- 包月套餐：¥199/月起（ unlimited 调用）
- 定制爬虫系统：¥5,000 - ¥30,000（按复杂度报价）

---

## 🔧 技术栈

- Python 3.11+, FastAPI
- httpx + BeautifulSoup4
- SQLite 数据持久化
- Docker 容器化

## 📄 License

MIT
