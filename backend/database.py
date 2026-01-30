"""
Database connection and session management.
SQLAlchemy creates tables and provides a session for CRUD operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

settings = get_settings()

# For SQLite we need check_same_thread=False (FastAPI uses multiple threads)
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set to True to log SQL queries (useful for debugging)
)

# SessionLocal: each request gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our model classes
Base = declarative_base()


def get_db():
    """
    Dependency that yields a database session.
    Ensures the session is closed after the request (used in FastAPI routes).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database. Call this on startup."""
    Base.metadata.create_all(bind=engine)
