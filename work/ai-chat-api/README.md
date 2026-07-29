# AI Chat API - 多模型智能对话接口服务

## 📦 项目简介

一个生产级的 FastAPI 服务，提供统一的 AI 聊天接口，支持 OpenAI、Anthropic、Ollama 等多种 AI 模型。

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（修改 config.yaml）
#    编辑 providers.openai.api_key

# 3. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000

# 4. Docker 部署
docker build -t ai-chat-api .
docker run -p 8000:8000 ai-chat-api
```

## 📡 API 文档

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/models` | 获取可用模型列表 |
| POST | `/chat/completions` | AI 对话接口 |

### 对话请求示例

```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "你好，介绍一下你自己"}
    ],
    "temperature": 0.7
  }'
```

---

## 💼 产品描述（可用于接单平台）

### 服务名称：AI Chat API — 多模型统一对话接口

**服务描述：**
为您提供稳定、高效的 AI 对话 API 服务。支持 GPT-4、Claude、本地开源模型等主流 AI 引擎，一键接入您的应用、网站或机器人。

**核心功能：**
- ✅ 多模型支持（OpenAI / Anthropic / 本地模型）
- ✅ 统一接口，轻松切换不同 AI 引擎
- ✅ 内置 API 密钥认证 + 频率限制
- ✅ 容器化部署，开箱即用
- ✅ 高并发处理，生产级稳定性

**适用场景：**
- 企业客服聊天机器人
- 内容生成助手（文案/代码/翻译）
- 个人/团队 AI 工具集成
- Web App AI 后端

**定价建议：**
- 基础版：免费试用（限额调用）
- 标准版：按 token 计费，约 $0.002/1K tokens
- 定制版：根据需求私有部署，一次性项目收费 ¥3,000 - ¥15,000

---

## 🔧 技术栈

- Python 3.11+
- FastAPI + Uvicorn
- PyYAML / httpx
- Docker 容器化

## 📄 License

MIT
