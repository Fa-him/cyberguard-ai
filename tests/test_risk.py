import pytest

from cyberguard_agent.tools.controls import (
    get_control_guidance,
    list_control_categories,
)
from cyberguard_agent.tools.redaction import redact_sensitive_text
from cyberguard_agent.tools.risk import calculate_risk, risk_label


@pytest.mark.parametrize(
    ("likelihood", "impact", "expected_score", "expected_priority"),
    [
        (1, 1, 1, "Low - monitor and improve controls"),
        (3, 4, 12, "High - prioritise same-day review"),
        (5, 5, 25, "Critical - escalate promptly"),
    ],
)
def test_valid_risk_scores_are_transparent(
    likelihood: int,
    impact: int,
    expected_score: int,
    expected_priority: str,
):
    result = calculate_risk(likelihood, impact)
    assert result["status"] == "success"
    assert result["score"] == expected_score
    assert result["priority"] == expected_priority
    assert result["method"] == "risk score = likelihood x impact"


@pytest.mark.parametrize(
    ("likelihood", "impact"),
    [
        (0, 5),
        (5, 0),
        (6, 1),
        (1, 6),
        ("3", 4),
        (3, 4.5),
    ],
)
def test_invalid_risk_values_are_rejected(likelihood, impact):
    result = calculate_risk(likelihood, impact)
    assert result["status"] == "error"


def test_risk_labels_cover_boundary_values():
    assert risk_label(4).startswith("Low")
    assert risk_label(5).startswith("Moderate")
    assert risk_label(10).startswith("High")
    assert risk_label(17).startswith("Critical")


def test_redaction_reduces_obvious_sensitive_text():
    fake_api_key = "sk-" + ("x" * 20)
    cleaned, count = redact_sensitive_text(
        f"Contact alice@example.com with password=demo-value and key {fake_api_key}"
    )
    assert count == 3
    assert "alice@example.com" not in cleaned
    assert "password=demo-value" not in cleaned
    assert fake_api_key not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "[REDACTED_SECRET]" in cleaned
    assert "[REDACTED_API_KEY]" in cleaned


def test_known_control_category_returns_defensive_guidance():
    guidance = get_control_guidance(" phishing ")
    assert guidance["status"] == "success"
    assert guidance["category"] == "phishing"
    assert guidance["title"] == "Phishing and suspicious messages"
    assert guidance["actions"]


def test_unknown_control_category_is_rejected():
    guidance = get_control_guidance("unknown")
    assert guidance["status"] == "error"
    assert "Unknown category" in guidance["message"]


def test_control_categories_are_sorted_and_known():
    categories = list_control_categories()["categories"]
    assert categories == sorted(categories)
    assert "phishing" in categories
    assert "incident_response" in categories
