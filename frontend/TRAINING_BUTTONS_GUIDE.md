# Why "Phishing" / "Not Phishing" Buttons Stop Working After the First Email

## 1. What’s going wrong?

- **First email:** You click "Phishing" or "Not Phishing" → answer is saved → feedback appears → you click "Next email".
- **Second email:** The new email loads, but clicking "Phishing" or "Not Phishing" does nothing. Only a full page refresh fixes it.

So the buttons work once, then stop until you refresh.

---

## 2. Why it happens (simple explanation)

When you click an answer, the code **disables** both buttons so you can’t submit twice:

```javascript
btnPhishing.disabled = true;
btnNotPhishing.disabled = true;
```

After that, when you click **"Next email"**, the app loads the next email and shows it, but it **never turns the buttons back on**. So for the second (and every later) email, the buttons are still disabled.

- **Disabled** = the element is still visible but does not respond to clicks.
- So: first email → buttons enabled → you click → they get disabled → next email loads → buttons stay disabled → clicks do nothing.

Refreshing the page loads the HTML again, so the buttons start in their default state (enabled), which is why it seems to work again after refresh.

---

## 3. Fix in plain JavaScript (what we did)

We need to **re-enable the buttons whenever we show a new email**.

In `loadNextEmail()` we do two things:

1. At the **start** of loading the next email (before the API call), turn the buttons back on so they’re ready for the new email:

```javascript
async function loadNextEmail() {
  // ... hide feedback, "Next" button, etc. ...

  // Re-enable the answer buttons so the next email is clickable
  btnPhishing.disabled = false;
  btnNotPhishing.disabled = false;

  try {
    // ... fetch next email and update the page ...
  }
}
```

2. Use the **same** button variables everywhere (at the top of the script and in both `loadNextEmail` and `submitAnswer`), so we’re always enabling/disabling the real buttons.

With this, every new email has clickable buttons without refreshing.

**If it still doesn’t work:** your browser may be using an old copy of `training.js`. Do a hard refresh (e.g. **Ctrl+Shift+R** or **Cmd+Shift+R**) or clear cache so the updated script loads.

---

## 4. Same idea in React

In React you drive the UI with **state**. For the buttons, the important idea is: “are we showing a new email? Then the buttons must be clickable.”

### Option A: State for “buttons disabled”

- After the user submits an answer, set `buttonsDisabled` to `true`.
- When you load the **next** email (e.g. in the “Next email” handler), set `buttonsDisabled` back to `false` **before** or **when** you set the new email in state.

Example shape:

```jsx
function TrainingPage() {
  const [currentEmail, setCurrentEmail] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);

  async function loadNextEmail() {
    setFeedback(null);
    setButtonsDisabled(false);  // ← Make buttons clickable for the new email

    const listRes = await fetch('/api/emails/?exclude_answered=true', { ... });
    const list = await listRes.json();
    if (list.length === 0) return;

    const emailRes = await fetch(`/api/emails/${list[0].id}`, { ... });
    const email = await emailRes.json();
    setCurrentEmail(email);
  }

  async function submitAnswer(isPhishing) {
    setButtonsDisabled(true);  // Prevent double submit

    const res = await fetch('/api/results/submit', {
      method: 'POST',
      body: JSON.stringify({ email_id: currentEmail.id, answer: isPhishing }),
    });
    const data = await res.json();
    setFeedback(data);
    // Don’t set buttonsDisabled back to true here; do it when loading next email
  }

  return (
    <>
      {currentEmail && (
        <>
          <div>{/* show currentEmail.subject, .sender, .body */}</div>
          <button
            disabled={buttonsDisabled}
            onClick={() => submitAnswer(true)}
          >
            Phishing
          </button>
          <button
            disabled={buttonsDisabled}
            onClick={() => submitAnswer(false)}
          >
            Not Phishing
          </button>
          {feedback && (
            <>
              <div>{/* show feedback */}</div>
              <button onClick={loadNextEmail}>Next email</button>
            </>
          )}
        </>
      )}
    </>
  );
}
```

Rule: **when you move to the next email (`loadNextEmail`), set `buttonsDisabled` to `false`** so the new email’s buttons work.

### Option B: Derive “disabled” from “have we already answered this email?”

You can also derive “buttons disabled” from state, e.g. “we have feedback for the current email”:

```jsx
const showFeedback = feedback !== null;
// Then: disabled={showFeedback}
// And in loadNextEmail: setFeedback(null); setCurrentEmail(newEmail);
```

So when you clear feedback and set the next email, the buttons become enabled again. Same idea: **new email → buttons must be enabled**.

---

## 5. Summary

| What | Plain JS | React |
|------|----------|--------|
| Cause | Buttons are set `disabled = true` after submit and never set back to `false` when loading the next email. | Same idea: state keeps buttons disabled and isn’t reset when loading the next email. |
| Fix | In `loadNextEmail()`, set `btnPhishing.disabled = false` and `btnNotPhishing.disabled = false` (before or when showing the new email). | In the “load next email” logic, set `buttonsDisabled` to `false` (or clear the “answered” state) when you set the new email. |
| Rule | Every time you show a **new** email, the answer buttons must be **enabled**. | Same. |

If you use the current `training.js` (with the re-enable in `loadNextEmail`) and still see the issue, do a hard refresh so the browser loads the updated script.
