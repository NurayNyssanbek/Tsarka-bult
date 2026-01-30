/**
 * Auth helper: get/set JWT token and user in localStorage.
 * Used by login, register, dashboard, and training pages.
 */
const AUTH_TOKEN_KEY = "phishing_training_token";
const AUTH_USER_KEY = "phishing_training_user";

// Base URL of the backend API (change if you run backend elsewhere)
const API_BASE = "http://localhost:8000/api";

function getToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

function getUser() {
  try {
    const u = localStorage.getItem(AUTH_USER_KEY);
    return u ? JSON.parse(u) : null;
  } catch {
    return null;
  }
}

function setUser(user) {
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user || {}));
}

function clearAuth() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

/**
 * Make authenticated fetch to API.
 * Adds Authorization: Bearer <token> header.
 */
async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    clearAuth();
    window.location.href = "index.html";
    return;
  }
  return res;
}

/**
 * Redirect to dashboard if already logged in (for login/register pages).
 */
function redirectIfLoggedIn() {
  if (getToken() && getUser()) {
    window.location.href = "dashboard.html";
  }
}
