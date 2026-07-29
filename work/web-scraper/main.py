"""Web Scraper API - Automated web scraping and data extraction service."""

import os
import uuid
import json
import sqlite3
import random
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

import yaml
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── Config ────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

DB_PATH = Path(config.get("database", {}).get("path", "./scraper_data.db"))
RATE_DELAY = config.get("rate_delay", {}).get("min_seconds", 1.0)
MAX_DELAY = config.get("rate_delay", {}).get("max_seconds", 3.0)
MAX_RETRY = config.get("scraping", {}).get("max_retries", 3)

# ─── User Agents Pool ──────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ─── DB Initialization ─────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrape_jobs (
            job_id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            result_format TEXT DEFAULT 'json',
            created_at TEXT,
            completed_at TEXT,
            error_message TEXT,
            rows_returned INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrape_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            content TEXT,
            meta_json TEXT,
            FOREIGN KEY (job_id) REFERENCES scrape_jobs(job_id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ─── Auth ──────────────────────────────────────────────────────
REQUIRED_API_KEY = config.get("auth", {}).get("api_key", "")

def validate_api_key(x_api_key: Optional[str] = Header(None)):
    if REQUIRED_API_KEY and x_api_key != REQUIRED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# ─── Pydantic Models ──────────────────────────────────────────
class ScrapeRequest(BaseModel):
    url: str
    format: str = "json"  # json, csv, txt
    extract_fields: Optional[List[str]] = None  # title, links, paragraphs
    timeout: Optional[int] = 30

class ScrapeJobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: str
    completed_at: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    url: str
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    rows_returned: int = 0
    results: Optional[List[Dict[str, Any]]] = None

# ─── Core Scraping Logic ───────────────────────────────────────
async def fetch_page(url: str, headers: dict) -> Optional[str]:
    """Fetch page HTML with retry logic."""
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(MAX_RETRY):
            try:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.text
            except Exception as e:
                if attempt == MAX_RETRY - 1:
                    return None
                delay = RATE_DELAY + random.random() * (MAX_DELAY - RATE_DELAY)
                await asyncio.sleep(delay)

def extract_content(html: str, fields: List[str]) -> List[Dict[str, Any]]:
    """Extract structured content from HTML based on requested fields."""
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Extract title
    if not fields or "title" in fields:
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        results.append({"field": "title", "value": title})

    # Extract all links
    if not fields or "links" in fields:
        links = []
        for a in soup.find_all("a", href=True):
            links.append({
                "text": a.get_text(strip=True),
                "href": a["href"]
            })
        results.append({"field": "links", "value": links})

    # Extract paragraphs
    if not fields or "paragraphs" in fields:
        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
            if p.get_text(strip=True)
        ]
        results.append({"field": "paragraphs", "value": paragraphs[:200]})  # Limit to 200

    # Extract headings
    if not fields or "headings" in fields:
        headings = []
        for h in soup.find_all(re.compile(r"^h[1-6]$")):
            level = h.name
            text = h.get_text(strip=True)
            headings.append({level: text})
        results.append({"field": "headings", "value": headings})

    if not results:
        # Default: return all basic info
        results.extend([
            {"field": "title", "value": soup.title.get_text(strip=True) if soup.title else ""},
            {"field": "links", "value": [{"text": a.get_text(strip=True), "href": a["href"]} for a in soup.find_all("a", href=True)]},
            {"field": "paragraphs", "value": [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)][:100]},
        ])

    return results

async def save_job_to_db(job_id: str, url: str, status: str, results: list, error_msg: str = None):
    """Persist scrape job results to SQLite."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    cursor.execute(
        "INSERT OR REPLACE INTO scrape_jobs (job_id, url, status, created_at, completed_at, error_message, rows_returned) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (job_id, url, status, now, now if status == "completed" else None, error_msg, len(results) if results else 0)
    )

    if results:
        for item in results:
            cursor.execute(
                "INSERT INTO scrape_results (job_id, content, meta_json) VALUES (?, ?, ?)",
                (job_id, json.dumps(item.get("value", ""), ensure_ascii=False), json.dumps({"field": item.get("field", "")}))
            )

    conn.commit()
    conn.close()

async def run_scrape(request: ScrapeRequest) -> tuple:
    """Core scraping workflow: fetch → extract → save → return."""
    job_id = uuid.uuid4().hex[:12]
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    html = await fetch_page(request.url, headers)
    if not html:
        error_msg = "Failed to fetch URL after retries"
        await save_job_to_db(job_id, request.url, "failed", [], error_msg)
        return job_id, "failed", [], error_msg

    results = extract_content(html, request.extract_fields or [])
    await save_job_to_db(job_id, request.url, "completed", results)
    return job_id, "completed", results, None

# ─── App ───────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Web Scraper API] Server starting...")
    print(f"[Web Scraper API] Database: {DB_PATH}")
    yield

app = FastAPI(
    title="Web Scraper API",
    description="Automated web scraping and data extraction service",
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
async def health_check(api_key: str = Depends(validate_api_key)):
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.post("/scrape/url", response_model=ScrapeJobResponse)
async def scrape_url(
    request: ScrapeRequest,
    api_key: str = Depends(validate_api_key)
):
    """Scrape a single URL and return extracted content."""
    job_id, status, results, error_msg = await run_scrape(request)

    return ScrapeJobResponse(
        job_id=job_id,
        status=status,
        message="Scrape completed successfully" if status == "completed" else f"Error: {error_msg}",
        created_at=datetime.now().isoformat(),
        completed_at=datetime.now().isoformat()
    )

@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    api_key: str = Depends(validate_api_key)
):
    """Get detailed status of a scrape job by ID."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scrape_jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")

    columns = ["job_id", "url", "status", "created_at", "completed_at", "error_message", "rows_returned"]
    job = dict(zip(columns, row))

    # Get results
    cursor.execute("SELECT meta_json, content FROM scrape_results WHERE job_id = ?", (job_id,))
    raw_results = cursor.fetchall()
    results = [{"meta": json.loads(r[0]), "content": r[1]} for r in raw_results]
    conn.close()

    return JobStatusResponse(**job, results=results)

# ─── Run Locally ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
