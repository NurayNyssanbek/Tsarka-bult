"""
Phishing Awareness Training - FastAPI Backend Entry Point.
Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db
from routers import auth, emails, results
from seed_emails import seed_emails
from add_emails import add_new_emails

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: create DB tables, seed sample emails if empty, then append any new emails from JSON.
    Shutdown: nothing to clean up for SQLite.
    """
    init_db()
    try:
        seed_emails()
        add_new_emails()
    except Exception as e:
        print(f"Seed warning: {e}")
    yield
    # shutdown (optional cleanup)


app = FastAPI(
    title="Phishing Awareness Training API",
    description="Educational API for phishing awareness training (registration, login, emails, results).",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: allow frontend (e.g. Live Server on port 5500) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (auth, emails, results)
app.include_router(auth.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(results.router, prefix="/api")


@app.get("/")
def root():
    """Health check / API info."""
    return {
        "message": "Phishing Awareness Training API",
        "docs": "/docs",
        "version": "1.0.0",
    }

frontend_dir = os.path.join(os.path.dirname(os.getcwd()), "frontend")

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")