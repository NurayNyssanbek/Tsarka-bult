# Phishing Awareness Training Web Application

A full-stack educational app for phishing awareness training: users register, log in, and practice identifying phishing vs. legitimate emails. The backend uses **FastAPI**, **SQLite**, **bcrypt**, and **JWT**; the frontend is vanilla **HTML/CSS/JS** and mobile-friendly.

## Features

- **User authentication**: Registration and login with bcrypt-hashed passwords and JWT sessions
- **Frontend**: Login, register, dashboard (stats + history), and training page with "Phishing" / "Not Phishing" buttons
- **Backend**: FastAPI serving emails, accepting answers, computing correctness and rule-based risk score, storing data in SQLite
- **Database**: Users, Results, and Emails tables (schema below)
- **Phishing detection**: Rule-based algorithm (keywords, suspicious URLs, urgency phrases) with risk score and feedback
- **Progress**: Dashboard shows correct answers, accuracy, and history; system is extensible for new patterns

## Project structure

```
.
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings (JWT, DB URL, CORS)
│   ├── database.py          # SQLAlchemy engine and session
│   ├── models.py            # User, Email, Result tables
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # bcrypt + JWT helpers
│   ├── phishing_detector.py # Rule-based risk score
│   ├── seed_emails.py       # Load sample emails from JSON
│   ├── data/
│   │   └── sample_emails.json
│   ├── routers/
│   │   ├── auth.py          # POST /api/auth/register, /api/auth/login
│   │   ├── emails.py        # GET /api/emails/, /api/emails/{id}
│   │   └── results.py       # POST /api/results/submit, GET /api/results/stats, /api/results/history
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Login
│   ├── register.html        # Registration
│   ├── dashboard.html       # Stats and training link
│   ├── training.html        # Email display + Phishing / Not Phishing
│   ├── css/style.css
│   └── js/
│       ├── auth.js          # Token, apiFetch, redirectIfLoggedIn
│       ├── dashboard.js     # Load stats and history
│       └── training.js      # Load email, submit answer, show feedback
└── README.md
```

## Database schema

- **users**: `id`, `username`, `email`, `password_hash`, `created_at`
- **emails**: `id`, `subject`, `sender`, `body`, `is_phishing`, `created_at`
- **results**: `id`, `user_id`, `email_id`, `answer`, `correct`, `risk_score`, `timestamp`

Tables are created on first run; sample emails are seeded from `backend/data/sample_emails.json`.

## Setup and run (step-by-step)

### 1. Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### 2. Frontend

Serve the `frontend` folder over HTTP (required for fetch to the API):

- **Option A**: VS Code "Live Server" – open `frontend` folder, start Live Server (e.g. port 5500).
- **Option B**: Python one-liner from project root:  
  `python -m http.server 5500 --directory frontend`

Then open: http://localhost:5500 (or the port your server uses).

### 3. Use the app

1. Open the frontend URL (e.g. http://localhost:5500).
2. Register a new account (username, email, password).
3. You’ll be logged in and redirected to the dashboard.
4. Click "Go to training", read each email, and choose **Phishing** or **Not Phishing**.
5. After each answer you see correctness and rule-based risk feedback; use "Next email" to continue.
6. Dashboard shows total answered, correct count, accuracy, and recent history.

## Security notes (for education)

- Passwords are hashed with **bcrypt**; never stored in plain text.
- Sessions use **JWT**; frontend sends `Authorization: Bearer <token>`.
- Change `SECRET_KEY` in production and use HTTPS.
- This is for **educational** phishing awareness only; do not use as production auth without hardening.

## Extending phishing patterns

Edit `backend/phishing_detector.py`:

- Add keywords to `PHISHING_KEYWORDS`.
- Add URL patterns to `SUSPICIOUS_URL_PATTERNS`.
- Add sender patterns to `SUSPICIOUS_SENDER_PATTERNS`.
- Optionally add new rules in `calculate_risk_score()` and return updated `score` and `feedback`.

New sample emails can be added to `backend/data/sample_emails.json` and re-run seeding (or add an admin endpoint to load them into the `emails` table).

## License

For educational use only.
