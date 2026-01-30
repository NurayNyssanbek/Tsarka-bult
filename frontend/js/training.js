/**
 * Training page: load an email, show Phishing / Not Phishing buttons,
 * submit answer, show feedback (correct/incorrect + risk score), then next email.
 */
(function () {
  if (!getToken() || !getUser()) {
    window.location.href = "index.html";
    return;
  }

  const user = getUser();
  document.getElementById("navUser").textContent = user.username || user.email || "";

  document.getElementById("logoutLink").addEventListener("click", (e) => {
    e.preventDefault();
    clearAuth();
    window.location.href = "index.html";
  });

  let currentEmail = null;
  const noEmailsEl = document.getElementById("noEmails");
  const emailSection = document.getElementById("emailSection");
  const loadingEl = document.getElementById("loading");
  const feedbackEl = document.getElementById("feedback");
  const btnNext = document.getElementById("btnNext");
  const btnPhishing = document.getElementById("btnPhishing");
  const btnNotPhishing = document.getElementById("btnNotPhishing");
  const progressEl = document.getElementById("trainingProgress");

  async function loadNextEmail() {
    loadingEl.classList.remove("hidden");
    emailSection.classList.add("hidden");
    noEmailsEl.classList.add("hidden");
    feedbackEl.classList.add("hidden");
    btnNext.classList.add("hidden");

    // Re-enable the answer buttons so the next email is clickable (they were disabled after submitting)
    btnPhishing.disabled = false;
    btnNotPhishing.disabled = false;

    try {
      // List emails (exclude already answered)
      const listRes = await apiFetch("/emails/?exclude_answered=true");
      if (!listRes.ok) throw new Error("Failed to list emails");
      const list = await listRes.json();

      if (list.length === 0) {
        loadingEl.classList.add("hidden");
        noEmailsEl.classList.remove("hidden");
        return;
      }

      if (progressEl) {
        progressEl.textContent = list.length === 1
          ? "1 email remaining"
          : list.length + " emails remaining";
      }

      // Pick first one and load full email
      const first = list[0];
      const getRes = await apiFetch("/emails/" + first.id);
      if (!getRes.ok) throw new Error("Failed to load email");
      currentEmail = await getRes.json();

      document.getElementById("emailSender").textContent = currentEmail.sender;
      document.getElementById("emailSubject").textContent = currentEmail.subject;
      document.getElementById("emailBody").textContent = currentEmail.body;

      loadingEl.classList.add("hidden");
      emailSection.classList.remove("hidden");
    } catch (e) {
      loadingEl.innerHTML = '<p class="alert alert-error">Could not load emails. Is the backend running?</p>';
    }
  }

  async function submitAnswer(isPhishing) {
    if (!currentEmail) return;

    btnPhishing.disabled = true;
    btnNotPhishing.disabled = true;

    try {
      const res = await apiFetch("/results/submit", {
        method: "POST",
        body: JSON.stringify({ email_id: currentEmail.id, answer: isPhishing }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || "Failed to submit answer.");
        btnPhishing.disabled = false;
        btnNotPhishing.disabled = false;
        return;
      }
      // Keep buttons disabled until "Next email" is clicked and loadNextEmail() re-enables them

      const data = await res.json();
      feedbackEl.classList.remove("hidden");
      feedbackEl.className = "result-feedback " + (data.correct ? "correct" : "incorrect");
      feedbackEl.innerHTML =
        (data.correct ? "✓ Correct!" : "✗ Incorrect. This email was " + (data.email_was_phishing ? "phishing." : "legitimate.")) +
        "<div class='risk'>Risk score (rule-based): " + data.risk_score + "/100. " + (data.feedback || "") + "</div>";

      btnNext.classList.remove("hidden");
    } catch (e) {
      alert("Network error.");
      btnPhishing.disabled = false;
      btnNotPhishing.disabled = false;
    }
  }

  btnPhishing.addEventListener("click", () => submitAnswer(true));
  btnNotPhishing.addEventListener("click", () => submitAnswer(false));

  btnNext.addEventListener("click", () => loadNextEmail());

  loadNextEmail();
})();
