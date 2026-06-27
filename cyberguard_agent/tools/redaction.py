from __future__ import annotations

import re

# Deliberately simple, transparent redaction. It reduces accidental disclosure in
# the prototype but is not represented as a complete data-loss-prevention solution.
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
API_KEY_PATTERN = re.compile(
    r"\b(?:AIza[\w-]{20,}|sk-[\w-]{16,}|ghp_[\w]{20,}|AKIA[\w]{16,})\b"
)
PASSWORD_PATTERN = re.compile(r"(?i)\b(password|passwd|secret)\s*[:=]\s*\S+")


def redact_sensitive_text(text: str) -> tuple[str, int]:
    """Redact common accidental secrets and email-like identifiers from text."""
    count = 0

    def replace(_: re.Match, label: str) -> str:
        nonlocal count
        count += 1
        return label

    text = EMAIL_PATTERN.sub(lambda match: replace(match, "[REDACTED_EMAIL]"), text)
    text = API_KEY_PATTERN.sub(lambda match: replace(match, "[REDACTED_API_KEY]"), text)
    text = PASSWORD_PATTERN.sub(lambda match: replace(match, "[REDACTED_SECRET]"), text)
    return text.strip(), count
