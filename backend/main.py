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
    init_db()
    try:
        seed_emails()
        add_new_emails()
    except Exception as e:
        print(f"Seed warning: {e}")
    yield

app = FastAPI(title="Phishing Awareness Training API", version="1.0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(results.router, prefix="/api")

@app.get("/check-files")
async def check_files():
    import os
    current = Path(os.getcwd())
    return {
        "current_dir": str(current),
        "contents": os.listdir(current),
        "backend_exists": os.path.exists("backend"),
        "frontend_exists": os.path.exists("frontend")
    }

current_dir = Path(os.getcwd())
frontend_dir = current_dir / "frontend"

if frontend_dir.exists() and frontend_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dir / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "Frontend not found", "dir": str(current_dir)}
