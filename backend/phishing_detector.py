"""
Rule-based phishing detection algorithm.
Analyzes email subject, sender, and body for suspicious patterns.
Returns a risk score (0-100) and can be extended with new rules.
"""
import re
from typing import List, Tuple

# ----- Extensible pattern lists (easy to add new keywords) -----

# Words that often appear in phishing (urgency, fear, reward)
PHISHING_KEYWORDS = [
    "urgent", "immediately", "verify", "suspend", "account", "password",
    "click here", "confirm", "winner", "prize", "congratulations",
    "limited time", "act now", "expire", "suspended", "locked",
    "unusual activity", "security alert", "verify your identity",
    "update your account", "billing problem", "payment failed",
    "irs", "tax refund", "inheritance", "wire transfer", "bitcoin",
    "dear customer", "dear user", "dear account holder",
]

# Suspicious URL patterns (shorteners, IPs, misspellings)
SUSPICIOUS_URL_PATTERNS = [
    r"bit\.ly", r"tinyurl", r"goo\.gl", r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # IP in URL
    r"login.*\.(tk|ml|ga|cf)", r"paypal.*\.(tk|ml|ga)", r"amazon.*\.(tk|ml)",
    r"http://[^s]",  # HTTP (not HTTPS) - less secure
]

# Sender/domain red flags
SUSPICIOUS_SENDER_PATTERNS = [
    r"noreply@", r"no-reply@", r"support@.*\.(tk|ml|ga|cf)",
    r"[\d]{6,}@",  # Many digits in local part
]

# Compile regexes once for performance
URL_REGEX = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE
)


def _count_matches(text: str, patterns: List[str]) -> int:
    """Count how many patterns appear in text (case-insensitive)."""
    if not text:
        return 0
    text_lower = text.lower()
    return sum(1 for p in patterns if p.lower() in text_lower)


def _count_regex_matches(text: str, patterns: List[str]) -> int:
    """Count how many regex patterns match in text."""
    if not text:
        return 0
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))


def _extract_urls(text: str) -> List[str]:
    """Extract all URLs from text for URL-based checks."""
    return URL_REGEX.findall(text or "")


def calculate_risk_score(subject: str, sender: str, body: str) -> Tuple[int, str]:
    """
    Rule-based phishing risk score (0-100) and short feedback.
    Higher score = more likely phishing. Extensible by adding rules.
    """
    score = 0
    reasons = []

    # 1. Keyword-based (phishing keywords in subject + body)
    combined = f"{subject or ''} {body or ''}"
    keyword_count = _count_matches(combined, PHISHING_KEYWORDS)
    if keyword_count > 0:
        points = min(keyword_count * 8, 35)
        score += points
        reasons.append(f"Found {keyword_count} suspicious keyword(s)")

    # 2. Urgency phrases (weighted higher)
    urgency = ["urgent", "immediately", "act now", "limited time", "verify now"]
    urgency_count = _count_matches(combined, urgency)
    if urgency_count > 0:
        score += min(urgency_count * 10, 25)
        reasons.append("Urgency language detected")

    # 3. Suspicious URLs
    urls = _extract_urls(combined)
    for url in urls:
        if _count_regex_matches(url, SUSPICIOUS_URL_PATTERNS) > 0:
            score += 15
            reasons.append("Suspicious URL pattern")
            break

    # 4. Sender checks
    if _count_regex_matches(sender or "", SUSPICIOUS_SENDER_PATTERNS) > 0:
        score += 20
        reasons.append("Suspicious sender")

    # 5. Generic greeting ("Dear customer" instead of name)
    if "dear customer" in (body or "").lower() or "dear user" in (body or "").lower():
        score += 10
        reasons.append("Generic greeting")

    # Cap at 100
    score = min(score, 100)

    feedback = "; ".join(reasons) if reasons else "Few obvious red flags detected."
    return score, feedback
