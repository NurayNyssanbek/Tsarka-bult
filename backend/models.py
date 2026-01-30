"""
SQLAlchemy database models (tables).
Each class represents a table; attributes are columns.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    Users table - stores registered users.
    Never store plain-text passwords; we only store password_hash.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash, never plain text
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: one user has many results (for ORM convenience)
    results = relationship("Result", back_populates="user", cascade="all, delete-orphan")


class Email(Base):
    """
    Emails table - stores sample phishing and legitimate emails for training.
    is_phishing=True means it's a phishing email; False means legitimate.
    """
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(500), nullable=False)
    sender = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)  # Full email body (can be long)
    is_phishing = Column(Boolean, nullable=False)  # Ground truth for scoring
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("Result", back_populates="email", cascade="all, delete-orphan")


class Result(Base):
    """
    Results table - stores each user's answer for each email they've seen.
    Used to calculate correctness and show progress/history.
    """
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)
    answer = Column(Boolean, nullable=False)  # True = user said "Phishing", False = "Not Phishing"
    correct = Column(Boolean, nullable=False)  # Whether answer matched email.is_phishing
    risk_score = Column(Integer, nullable=True)  # 0-100 from our detector (for feedback)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="results")
    email = relationship("Email", back_populates="results")
