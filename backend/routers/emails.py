"""
Email routes: list emails and get a single email for training.
- List: return IDs of emails (optionally excluding ones user already answered).
- Get: return one email by ID (subject, sender, body - no is_phishing!).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Email, Result
from schemas import EmailResponse
from auth import get_current_user

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.get("/", response_model=list[dict])
def list_emails(
    exclude_answered: bool = Query(True, description="Exclude emails user already answered"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List available training emails (IDs and basic info).
    If exclude_answered=True, only return emails the user hasn't answered yet.
    """
    query = db.query(Email)
    if exclude_answered:
        answered_ids = db.query(Result.email_id).filter(Result.user_id == current_user.id).distinct()
        query = query.filter(~Email.id.in_(answered_ids))

    emails = query.all()
    return [{"id": e.id, "subject": e.subject, "sender": e.sender} for e in emails]


@router.get("/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single email by ID for training.
    Returns subject, sender, body - NOT is_phishing (user must guess!).
    """
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return EmailResponse.model_validate(email)
