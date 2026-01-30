# UI Redesign & Adding More Emails – Beginner Guide

This guide explains what was improved, which files control the UI vs the data, and how to add new emails in the future.

---

## 1. UI/UX Improvements Summary

### What changed

- **Layout and spacing**  
  Consistent spacing (variables like `--space-md`, `--space-lg`), clearer hierarchy, and a max-width container so content is easy to read on large screens.

- **Visual separation**  
  The training page now has:
  - An **email card** (header “From”, subject, body) in its own bordered block.
  - A separate **action area** with the label “What do you think? Choose one:” and the two buttons below it.

- **Phishing / Not Phishing buttons**  
  Buttons are larger (min-height 52px), use stronger colors (red for Phishing, green for Not Phishing), and have hover/focus styles so they’re more noticeable and accessible.

- **Overall look**  
  Dark theme with a cybersecurity feel: darker backgrounds, subtle borders, and shadows so cards and buttons stand out. Progress text (e.g. “5 emails remaining”) appears above the email.

- **Navigation**  
  Emails load one by one without a full page reload; after you answer, you click “Next email” to load the next. Buttons stay clickable for every new email (re-enabled when the next email loads).

---

## 2. Which Files Control What

| Goal | Files to edit |
|------|----------------|
| **Overall look (colors, spacing, buttons, cards)** | `frontend/css/style.css` |
| **Training page structure (email card, labels, buttons)** | `frontend/training.html` |
| **Training behavior (load email, submit answer, next)** | `frontend/js/training.js` |
| **Add or change training emails** | `backend/data/sample_emails.json` (see below) |

- **CSS** = layout, colors, sizes, borders, shadows.  
- **HTML** = structure and labels (headings, “From”, subject, body, “What do you think?”, Phishing / Not Phishing, Next).  
- **JS** = loading emails, handling button clicks, showing feedback, loading next email.  
- **JSON** = list of emails the backend serves; adding entries here adds more training emails (after restart or running the add script).

---

## 3. How Emails Are Stored and Loaded

- Emails are stored in a **JSON file**: `backend/data/sample_emails.json`.
- Each email is one object in an array with: `subject`, `sender`, `body`, `is_phishing` (true = phishing, false = legitimate).
- On startup, the backend:
  1. Creates the database and tables if needed.
  2. If the emails table is empty, it **seeds** all emails from the JSON file.
  3. It then runs an **append** step: any email in the JSON that isn’t already in the DB (same subject + sender) is added.
- The frontend never reloads the page for the next email: it calls the API, gets the next email, and updates the same page (smooth navigation).

---

## 4. How to Add New Emails in the Future

### Step 1: Edit the JSON file

Open `backend/data/sample_emails.json` and add a new object to the array. Copy the structure of existing emails:

```json
{
  "subject": "Your subject line here",
  "sender": "sender@example.com",
  "body": "Email body text.\n\nUse \\n for new lines.",
  "is_phishing": true
}
```

- `"is_phishing": true` = phishing email; `false` = legitimate.  
- In `body`, use `\n` for line breaks.

### Step 2: Load the new emails into the database

**Option A – Restart the backend (easiest)**  
Stop the backend (Ctrl+C) and start it again (`uvicorn main:app --reload ...`). On startup it runs the append step and adds any new emails from the JSON (without deleting existing ones).

**Option B – Run the add script by hand**  
From the `backend` folder run:

```bash
python add_emails.py
```

This does the same append step: new emails (by subject + sender) are added; existing ones are skipped.

**Option C – Fresh database**  
If you want to wipe all data and reload only what’s in the JSON: delete the file `backend/phishing_training.db`, then start the backend again. The DB is recreated and all emails in the JSON are seeded.

---

## 5. Example: Adding One New Phishing Email

In `backend/data/sample_emails.json`, add this object (e.g. at the end of the array, before the closing `]`):

```json
{
  "subject": "Your Microsoft account has been locked",
  "sender": "noreply@microsoft-account.ga",
  "body": "Dear User,\n\nYour Microsoft account has been locked due to suspicious activity.\n\nVerify now: http://microsoft-account.ga/verify\n\nYou have 24 hours to restore access.\n\nMicrosoft Account Team",
  "is_phishing": true
}
```

Save the file, restart the backend (or run `python add_emails.py`), then open the training page: the new email will appear in the rotation. No frontend code changes are required.

---

## 6. Example: Changing the Look of the Buttons (CSS)

To make the Phishing / Not Phishing buttons even larger or change colors, edit `frontend/css/style.css`.

Example – larger training action buttons:

```css
.training-actions .btn {
  padding: 1.25rem 1.5rem;
  font-size: 1.15rem;
  min-height: 60px;
}
```

Example – different danger (Phishing) color:

```css
.btn-danger {
  background: #dc3545;
  color: #fff;
}
```

---

## 7. Example: React Version of the Same Ideas

If you rebuild the training page in React, the same logic applies:

- **State:** e.g. `currentEmail`, `feedback`, `buttonsDisabled`.
- **Load next email:** set `buttonsDisabled` to `false` when you set the new email (so buttons work for every email).
- **Submit answer:** set `buttonsDisabled` to `true`, call the API, then show feedback and a “Next email” button.
- **Data:** emails still come from your backend API (which reads from the DB populated from the JSON file).

```jsx
// Conceptual React snippet
const [currentEmail, setCurrentEmail] = useState(null);
const [feedback, setFeedback] = useState(null);
const [buttonsDisabled, setButtonsDisabled] = useState(false);

async function loadNextEmail() {
  setFeedback(null);
  setButtonsDisabled(false);  // Keep buttons clickable for new email
  const res = await fetch('/api/emails/?exclude_answered=true', { headers: { Authorization: `Bearer ${token}` } });
  const list = await res.json();
  if (list.length === 0) return;
  const emailRes = await fetch(`/api/emails/${list[0].id}`, { headers: { Authorization: `Bearer ${token}` } });
  const email = await emailRes.json();
  setCurrentEmail(email);
}

// In JSX: two buttons with disabled={buttonsDisabled}, onClick for Phishing / Not Phishing
```

---

## 8. Quick Reference

| Task | Action |
|------|--------|
| Change colors, spacing, button size | Edit `frontend/css/style.css` |
| Change training page layout or labels | Edit `frontend/training.html` |
| Change how emails load or buttons behave | Edit `frontend/js/training.js` |
| Add new training emails | Add objects to `backend/data/sample_emails.json`, then restart backend or run `python add_emails.py` |
| Reset all data and reload emails from JSON | Delete `backend/phishing_training.db` and restart backend |
