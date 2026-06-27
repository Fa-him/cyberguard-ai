from cyberguard_agent.tools.redaction import redact_sensitive_text
from cyberguard_agent.tools.risk import calculate_risk, risk_label


def test_risk_score_is_transparent():
    result = calculate_risk(3, 4)
    assert result["status"] == "success"
    assert result["score"] == 12
    assert result["priority"] == "High — prioritise same-day review"


def test_invalid_risk_values_are_rejected():
    result = calculate_risk(0, 5)
    assert result["status"] == "error"


def test_risk_labels_cover_boundary_values():
    assert risk_label(4).startswith("Low")
    assert risk_label(5).startswith("Moderate")
    assert risk_label(10).startswith("High")
    assert risk_label(17).startswith("Critical")


def test_redaction_reduces_obvious_sensitive_text():
    cleaned, count = redact_sensitive_text(
        "Contact alice@example.com with password=hello and key sk-12345678901234567890"
    )
    assert count == 3
    assert "alice@example.com" not in cleaned
    assert "password=hello" not in cleaned
