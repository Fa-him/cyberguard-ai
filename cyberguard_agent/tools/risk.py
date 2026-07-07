from __future__ import annotations

from typing import Any


def risk_label(score: int) -> str:
    """Map a 1-25 risk score to a clear, human-readable priority."""
    if score >= 17:
        return "Critical - escalate promptly"
    if score >= 10:
        return "High - prioritise same-day review"
    if score >= 5:
        return "Moderate - plan corrective action"
    return "Low - monitor and improve controls"


def calculate_risk(likelihood: int, impact: int) -> dict[str, Any]:
    """Calculate a transparent 5 x 5 cyber-risk score.

    Args:
        likelihood: Integer from 1 (rare) to 5 (almost certain).
        impact: Integer from 1 (minimal) to 5 (severe).

    Returns:
        A dictionary containing the score, label, and method. Invalid values are
        rejected rather than silently corrected so users can review the inputs.
    """
    if not isinstance(likelihood, int) or not isinstance(impact, int):
        return {"status": "error", "message": "Likelihood and impact must be integers."}
    if not 1 <= likelihood <= 5 or not 1 <= impact <= 5:
        return {
            "status": "error",
            "message": "Likelihood and impact must both be between 1 and 5.",
        }

    score = likelihood * impact
    return {
        "status": "success",
        "likelihood": likelihood,
        "impact": impact,
        "score": score,
        "priority": risk_label(score),
        "method": "risk score = likelihood x impact",
    }
