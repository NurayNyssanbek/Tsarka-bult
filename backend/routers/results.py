"""
Results routes: submit answer, get history, get dashboard stats.
- Submit: user answers "Phishing" or "Not Phishing", we store and return correctness + feedback.
- History: list user's past results.
- Stats: dashboard statistics (correct count, accuracy, etc.).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Email, Result
from schemas import EmailAnswer, ResultResponse, ResultHistoryItem, DashboardStats
from security import get_current_user
from phishing_detector import calculate_risk_score

router = APIRouter(prefix="/results", tags=["Results"])


@router.post("/submit", response_model=ResultResponse)
def submit_answer(
    payload: EmailAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    User submits their answer (Phishing = True, Not Phishing = False).
    We calculate risk score from our detector, store the result, and return correctness + feedback.
    """
    email = db.query(Email).filter(Email.id == payload.email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # Check if user already answered this email (optional: allow retry or block)
    existing = db.query(Result).filter(
        Result.user_id == current_user.id,
        Result.email_id == payload.email_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already answered this email")

    # Rule-based risk score (for feedback only; correctness is based on ground truth)
    risk_score, feedback = calculate_risk_score(email.subject, email.sender, email.body)

    # Correct if user's answer matches email.is_phishing
    correct = payload.answer == email.is_phishing

    result = Result(
        user_id=current_user.id,
        email_id=payload.email_id,
        answer=payload.answer,
        correct=correct,
        risk_score=risk_score,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return ResultResponse(
        correct=correct,
        risk_score=risk_score,
        feedback=feedback,
        email_was_phishing=email.is_phishing,
    )


@router.get("/history", response_model=list[ResultHistoryItem])
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's result history (most recent first)."""
    results = (
        db.query(Result)
        .filter(Result.user_id == current_user.id)
        .order_by(Result.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [ResultHistoryItem.model_validate(r) for r in results]


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dashboard statistics: total answered, correct count, accuracy,
    phishing caught, false positives, false negatives, total emails.
    """
    total_emails = db.query(Email).count()

    results = db.query(Result).filter(Result.user_id == current_user.id).all()
    total_answered = len(results)
    correct_count = sum(1 for r in results if r.correct)
    accuracy = (correct_count / total_answered * 100) if total_answered > 0 else 0.0

    # Phishing caught: user said phishing and it was phishing
    phishing_caught = sum(1 for r in results if r.answer and r.correct)
    # False positives: user said phishing but it was legitimate
    false_positives = sum(1 for r in results if r.answer and not r.correct)
    # False negatives: user said not phishing but it was phishing
    false_negatives = sum(1 for r in results if not r.answer and not r.correct)

    return DashboardStats(
        total_answered=total_answered,
        correct_count=correct_count,
        accuracy_percent=round(accuracy, 1),
        phishing_caught=phishing_caught,
        false_positives=false_positives,
        false_negatives=false_negatives,
        total_emails=total_emails,
    )
