/**
 * Dashboard: load stats and history, show user info, handle logout.
 */
(function () {
  if (!getToken() || !getUser()) {
    window.location.href = "index.html";
    return;
  }

  const user = getUser();
  document.getElementById("navUser").textContent = user.username || user.email || "User";

  document.getElementById("logoutLink").addEventListener("click", (e) => {
    e.preventDefault();
    clearAuth();
    window.location.href = "index.html";
  });

  loadStats();
  loadHistory();
})();

async function loadStats() {
  const el = document.getElementById("stats");
  try {
    const res = await apiFetch("/results/stats");
    if (!res.ok) throw new Error("Failed to load stats");
    const s = await res.json();

    el.innerHTML = `
      <div class="stat-card">
        <div class="value">${s.total_answered}</div>
        <div class="label">Answered</div>
      </div>
      <div class="stat-card">
        <div class="value">${s.correct_count}</div>
        <div class="label">Correct</div>
      </div>
      <div class="stat-card">
        <div class="value">${s.accuracy_percent}%</div>
        <div class="label">Accuracy</div>
      </div>
      <div class="stat-card">
        <div class="value">${s.total_emails}</div>
        <div class="label">Total emails</div>
      </div>
    `;
  } catch {
    el.innerHTML = '<p class="text-muted">Could not load stats. Is the backend running?</p>';
  }
}

async function loadHistory() {
  const el = document.getElementById("history");
  try {
    const res = await apiFetch("/results/history?limit=10");
    if (!res.ok) throw new Error("Failed to load history");
    const list = await res.json();

    if (list.length === 0) {
      el.innerHTML = "No verdicts yet. Run a scan to see history.";
      return;
    }

    el.innerHTML = list
      .map(
        (r) =>
          `<div class="history-item">
            #${r.email_id} — ${r.answer ? "Phishing" : "Legitimate"} — ${r.correct ? "✓" : "✗"} — ${new Date(r.timestamp).toLocaleString()}
          </div>`
      )
      .join("");
  } catch {
    el.innerHTML = "Could not load history.";
  }
}
