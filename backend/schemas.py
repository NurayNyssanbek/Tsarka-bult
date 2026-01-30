"""
Pydantic schemas for request/response validation.
These define what data we accept from the client and what we return.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ----- User schemas -----

class UserCreate(BaseModel):
    """Data required to register a new user."""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Data required to log in (username or email + password)."""
    username: str  # Can be username or email
    password: str


class UserResponse(BaseModel):
    """User data we send to the client (never include password_hash!)."""
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# ----- Auth schemas -----

class Token(BaseModel):
    """JWT token response after successful login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ----- Email schemas -----

class EmailResponse(BaseModel):
    """Email data sent to the client (no is_phishing - that's the answer to guess!)."""
    id: int
    subject: str
    sender: str
    body: str

    class Config:
        from_attributes = True


class EmailAnswer(BaseModel):
    """User's answer for an email (Phishing = True, Not Phishing = False)."""
    email_id: int
    answer: bool  # True = Phishing, False = Not Phishing


# ----- Result schemas -----

class ResultResponse(BaseModel):
    """Result of a single answer (correctness + feedback)."""
    correct: bool
    risk_score: Optional[int]  # Исправлено
    feedback: str
    email_was_phishing: bool  # Ground truth for learning


class ResultHistoryItem(BaseModel):
    """Single item in user's result history."""
    id: int
    email_id: int
    answer: bool
    correct: bool
    risk_score: Optional[int]  # Исправлено
    timestamp: datetime

    class Config:
        from_attributes = True


# ----- Dashboard stats -----

class DashboardStats(BaseModel):
    """Statistics shown on the user's dashboard."""
    total_answered: int
    correct_count: int
    accuracy_percent: float
    phishing_caught: int  # Correctly identified as phishing
    false_positives: int  # Said phishing but was legitimate
    false_negatives: int  # Said not phishing but was phishing
    total_emails: int  # Total emails available for training
