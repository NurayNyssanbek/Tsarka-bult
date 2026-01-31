"""
Phishing Awareness Training - FastAPI Backend Entry Point.
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
# ... после всех app.include_router() ...

# ДИАГНОСТИКА - временный эндпоинт
@app.get("/check-files")
async def check_files():
    import os
    current = Path(os.getcwd())
    return {
        "current_dir": str(current),
        "contents": os.listdir(current),
        "backend_exists": os.path.exists("backend"),
        "frontend_exists": os.path.exists("frontend"),
        "files_in_root": os.listdir(".") if os.path.exists(".") else []
    }

# ... дальше код с frontend_dir ...
# 2. ПОДКЛЮЧЕНИЕ ФРОНТЕНДА - РАБОЧАЯ ВЕРСИЯ ДЛЯ BULT.AI
# В Bult.ai контейнер запускается с рабочей директорией в корне репозитория
current_dir = Path(os.getcwd())  # Корень репозитория в контейнере
frontend_dir = current_dir / "frontend"

print(f"Current directory: {current_dir}")
print(f"Looking for frontend at: {frontend_dir}")

# Проверяем существование папки
if frontend_dir.exists() and frontend_dir.is_dir():
    print(f"✅ Frontend found at: {frontend_dir}")
    print(f"Frontend contents: {os.listdir(frontend_dir)}")
    
    # Раздаём статические файлы из папки frontend
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    
    # Главная страница
    @app.get("/")
    async def serve_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"error": "index.html not found in frontend folder"}
    
    # Обработка всех остальных путей для SPA
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Проверяем, существует ли файл по пути
        file_path = frontend_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Если это путь API - пропускаем
        if full_path.startswith("api"):
            return {"error": "API route not found"}
        
        # Для SPA - возвращаем index.html
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        
        return {"error": "Frontend file not found"}
    
else:
    print(f"❌ WARNING: Frontend directory NOT found at {frontend_dir}")
    print(f"Available directories in {current_dir}: {os.listdir(current_dir)}")
    
    @app.get("/")
    async def root():
        return {
            "message": "API is working, but frontend folder was not found.",
            "current_dir": str(current_dir),
            "available_files": os.listdir(current_dir)
        }