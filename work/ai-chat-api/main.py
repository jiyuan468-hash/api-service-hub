"""AI Chat API - Production-ready FastAPI service for multi-model AI chat."""

import os
import yaml
import time
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ─── Load Config ───────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# ─── Rate Limiter ──────────────────────────────────────────────
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: Dict[str, list] = {}

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Clean old entries
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if now - t < self.window
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        self.requests[client_ip].append(now)
        return True


rate_limiter = RateLimiter(
    max_requests=config["rate_limit"]["max_requests_per_minute"],
    window_seconds=60
)

# ─── Auth Middleware ───────────────────────────────────────────
REQUIRED_API_KEY = config.get("auth", {}).get("api_key", "")

def validate_api_key(x_api_key: Optional[str] = Header(None)):
    if REQUIRED_API_KEY and x_api_key != REQUIRED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# ─── Pydantic Models ──────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]

# ─── Model Router (simplified proxy to remote/local providers) ─
async def call_ai_model(model_name: str, messages: list, temperature: float) -> str:
    """Proxy to configured AI provider. Supports OpenAI, Ollama, and custom endpoints."""
    import httpx

    providers = config.get("providers", {})
    selected_provider = None

    # Find matching provider for model
    for name, prov in providers.items():
        if model_name in prov.get("models", []) or prov.get("default_model") == model_name:
            selected_provider = prov
            break

    if not selected_provider:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model_name}")

    headers = {
        "Authorization": f"Bearer {selected_provider['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": selected_provider.get("default_model"),
        "messages": [{"role": m.role, "content": m.content} for m in messages],
        "temperature": temperature
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                selected_provider["endpoint"],
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI Provider Error: {str(e)}")

# ─── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[AI Chat API] Server starting...")
    print(f"[AI Chat API] Providers loaded: {list(config.get('providers', {}).keys())}")
    yield

# ─── App Init ──────────────────────────────────────────────────
app = FastAPI(
    title="AI Chat API",
    description="Production-ready AI chat API supporting multiple models",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "uptime": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/models")
async def list_models():
    providers = config.get("providers", {})
    models = []
    for name, prov in providers.items():
        models.extend(prov.get("models", []))
        if prov.get("default_model"):
            models.append(prov["default_model"])
    return {"available_models": list(set(models))}

@app.post("/chat/completions")
async def create_chat_completion(
    req: ChatCompletionRequest,
    api_key: str = Depends(validate_api_key),
    request: Request = None
):
    client_ip = request.client.host if request else "unknown"

    # Check rate limit
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    model = req.model or config.get("providers", {}).get("openai", {}).get("default_model", "gpt-3.5-turbo")

    try:
        response_text = await call_ai_model(model, req.messages, req.temperature)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "id": f"chatcmpl-{int(time.time())}-{os.urandom(4).hex()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": response_text},
            "finish_reason": "stop"
        }]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
