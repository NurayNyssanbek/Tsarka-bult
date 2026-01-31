"""
Phishing Awareness Training - FastAPI Backend Entry Point.
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import get_settings
from database import init_db
from routers import auth, emails, results
from seed_emails import seed_emails
from add_emails import add_new_emails

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables, seed emails."""
    init_db()
    try:
        seed_emails()
        add_new_emails()
    except Exception as e:
        print(f"Seed warning: {e}")
    yield

app = FastAPI(
    title="Phishing Awareness Training API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: разрешаем всем
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Сначала подключаем API
app.include_router(auth.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(results.router, prefix="/api")

# 2. ИСПРАВЛЕННЫЙ ПУТЬ К ФРОНТЕНДУ
BASE_DIR = Path(__file__).resolve().parent.parent  # Корень репозитория
frontend_dir = BASE_DIR / "frontend"

if os.path.exists(frontend_dir):
    print(f"✅ Frontend found at: {frontend_dir}")
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    print(f"❌ WARNING: Frontend NOT found at {frontend_dir}")
    
    @app.get("/")
    def root():
        return {"message": "API is working, but frontend folder was not found."}