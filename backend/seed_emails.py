"""
Seed the database with sample phishing and legitimate emails from JSON.
Run once after creating the database: python seed_emails.py
"""
import json
import os
from pathlib import Path

from database import SessionLocal, init_db
from models import Email

# Path to sample emails JSON (next to this script, in data/)
DATA_DIR = Path(__file__).parent / "data"
SAMPLE_EMAILS_PATH = DATA_DIR / "sample_emails.json"


def load_sample_emails():
    """Load sample emails from JSON file."""
    if not SAMPLE_EMAILS_PATH.exists():
        raise FileNotFoundError(f"Sample emails file not found: {SAMPLE_EMAILS_PATH}")
    with open(SAMPLE_EMAILS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_emails():
    """Create tables and insert sample emails if table is empty."""
    init_db()
    db = SessionLocal()
    try:
        count = db.query(Email).count()
        if count > 0:
            print(f"Emails table already has {count} emails. Skipping seed.")
            return
        emails_data = load_sample_emails()
        for item in emails_data:
            email = Email(
                subject=item["subject"],
                sender=item["sender"],
                body=item["body"],
                is_phishing=item["is_phishing"],
            )
            db.add(email)
        db.commit()
        print(f"Seeded {len(emails_data)} emails.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_emails()
