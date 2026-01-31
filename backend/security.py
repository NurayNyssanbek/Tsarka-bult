"""
Authentication utilities: password hashing (bcrypt) and JWT tokens.
- Passwords are NEVER stored in plain text; we hash them with bcrypt.
- JWT (JSON Web Token) is used for session-based auth: client sends token in header.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import get_settings
from database import SessionLocal
from models import User

settings = get_settings()

# CryptContext: use bcrypt for hashing (industry standard, slow = secure)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTPBearer: expect "Authorization: Bearer <token>" header
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password with bcrypt.
    Same password always produces same hash (due to salt stored in hash).
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if plain_password matches the stored hash.
    Returns True if correct, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token containing user id (and optional expiry).
    Client will send this token in Authorization header for protected routes.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    Returns payload (e.g. {"sub": user_id}) or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_by_username_or_email(username: str) -> Optional[User]:
    """Find user by username or email (for login)."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        return user
    finally:
        db.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    """Find user by id (for JWT payload)."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    """
    Dependency: get current user from JWT in Authorization header.
    Use in routes that require login: current_user: User = Depends(get_current_user).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload["sub"])
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
