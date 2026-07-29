# 🚀 三个项目一键启动指南

## 项目总览

| 项目 | 端口 | 说明 |
|------|------|------|
| ai-chat-api | 8000 | AI 多模型对话接口 |
| data-tools | 8001 | 文档转换服务 |
| web-scraper | 8002 | 自动化爬虫服务 |

---

## 快速启动（Python）

```bash
# 项目1: AI Chat API
cd work/ai-chat-api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# 项目2: Data Tools
cd ../data-tools
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001

# 项目3: Web Scraper
cd ../web-scraper
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002
```

## Docker 启动

```bash
# 每个项目独立容器
docker build -t ai-chat-api -f ai-chat-api/Dockerfile ai-chat-api/
docker build -t data-tools -f data-tools/Dockerfile data-tools/
docker build -t web-scraper -f web-scraper/Dockerfile web-scraper/

docker run -d -p 8000:8000 ai-chat-api
docker run -d -p 8001:8000 data-tools
docker run -d -p 8002:8002 web-scraper
```

---

## 接单平台发布建议

### 推荐平台
- **国内**: 闲鱼、猪八戒、淘宝外包
- **国际**: Fiverr、Upwork、Freelancer

### 起步策略
1. 先在本地跑通测试，录屏 Demo
2. 在平台发布 3 个独立服务条目
3. 第一个客户可以给半价或免费试用
4. 收集好评后逐步提价

### 定价参考
| 项目 | 入门价 | 进阶价 |
|------|--------|--------|
| AI Chat API | ¥500 | ¥3,000+ |
| 数据处理 API | ¥300 | ¥1,500+ |
| 爬虫服务 | ¥500 | ¥5,000+ |
