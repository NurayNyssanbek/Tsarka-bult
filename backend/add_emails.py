"""
Append new emails from sample_emails.json to the database (without wiping existing data).
Use this when you add more entries to sample_emails.json and want to load them.
Skips emails that already exist (same subject + sender).
Run from backend folder: python add_emails.py
"""
from database import SessionLocal, init_db
from models import Email
from seed_emails import load_sample_emails


def add_new_emails():
    """Insert any emails from JSON that are not already in the DB (by subject + sender)."""
    init_db()
    db = SessionLocal()
    try:
        existing = {(e.subject, e.sender) for e in db.query(Email.subject, Email.sender).all()}
        emails_data = load_sample_emails()
        added = 0
        for item in emails_data:
            key = (item["subject"], item["sender"])
            if key in existing:
                continue
            db.add(Email(
                subject=item["subject"],
                sender=item["sender"],
                body=item["body"],
                is_phishing=item["is_phishing"],
            ))
            existing.add(key)
            added += 1
        db.commit()
        if added > 0:
            print(f"Added {added} new email(s). Total in DB: {db.query(Email).count()}")
        return added
    finally:
        db.close()


if __name__ == "__main__":
    add_new_emails()
