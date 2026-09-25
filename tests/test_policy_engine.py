import pandas as pd

from src.policy_engine import (
    build_operations_brief,
    get_recommended_action,
    load_policy,
)


def test_policy_file_can_be_loaded():

    policy = load_policy()

    assert "Connection Rescue Operations Policy" in policy


def test_critical_case_gets_rebooking_action():

    action = get_recommended_action(
        priority="CRITICAL",
        status="MISSED",
    )

    assert "rebooking" in action.lower()


def test_high_priority_case_gets_monitoring_action():

    action = get_recommended_action(
        priority="HIGH",
        status="AT_RISK",
    )

    assert "monitor" in action.lower()


def test_safe_case_requires_no_immediate_intervention():

    action = get_recommended_action(
        priority="LOW",
        status="SAFE",
    )

    assert "no immediate intervention" in action.lower()


def test_operations_brief_contains_key_metrics():

    assessment = pd.DataFrame(
        {
            "priority": [
                "CRITICAL",
                "HIGH",
                "LOW",
            ],
            "status": [
                "MISSED",
                "AT_RISK",
                "SAFE",
            ],
        }
    )

    brief = build_operations_brief(
        assessment
    )

    assert "Missed connections: 1" in brief
    assert "At-risk connections: 1" in brief
    assert "Critical priority cases: 1" in brief
    assert "High priority cases: 1" in brief