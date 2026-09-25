from src.priority_engine import (
    calculate_priority_score,
    classify_priority,
)


def test_missed_connection_has_high_score():
    score = calculate_priority_score(
        status="MISSED",
        delay_minutes=120,
        available_minutes=20,
        required_minutes=75,
    )

    assert score >= 80


def test_at_risk_connection_has_medium_or_high_score():
    score = calculate_priority_score(
        status="AT_RISK",
        delay_minutes=60,
        available_minutes=80,
        required_minutes=75,
    )

    assert 40 <= score <= 100


def test_safe_connection_has_lower_score():
    score = calculate_priority_score(
        status="SAFE",
        delay_minutes=0,
        available_minutes=180,
        required_minutes=60,
    )

    assert score < 40


def test_priority_classification():
    assert classify_priority(90) == "CRITICAL"
    assert classify_priority(70) == "HIGH"
    assert classify_priority(50) == "MEDIUM"
    assert classify_priority(20) == "LOW"


def test_score_cannot_exceed_100():
    score = calculate_priority_score(
        status="MISSED",
        delay_minutes=500,
        available_minutes=0,
        required_minutes=120,
    )

    assert score == 100