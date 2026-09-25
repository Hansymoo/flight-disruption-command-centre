from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = BASE_DIR / "docs" / "operations_policy.md"


def load_policy() -> str:
    """Load the local operational policy."""

    if not POLICY_PATH.exists():
        return "Operations policy unavailable."

    return POLICY_PATH.read_text(
        encoding="utf-8"
    )


def get_recommended_action(
    priority: str,
    status: str,
) -> str:
    """Return a deterministic operational recommendation."""

    if status == "MISSED" or priority == "CRITICAL":
        return (
            "Review alternative routing and prioritise "
            "time-sensitive rebooking."
        )

    if priority == "HIGH":
        return (
            "Monitor connection closely and review "
            "alternative onward options."
        )

    if priority == "MEDIUM":
        return (
            "Continue monitoring and recalculate risk "
            "after significant updates."
        )

    return (
        "No immediate intervention required; "
        "continue monitoring."
    )


def build_operations_brief(
    assessment,
) -> str:
    """Generate a concise operational brief."""

    critical = (
        assessment["priority"] == "CRITICAL"
    ).sum()

    high = (
        assessment["priority"] == "HIGH"
    ).sum()

    missed = (
        assessment["status"] == "MISSED"
    ).sum()

    at_risk = (
        assessment["status"] == "AT_RISK"
    ).sum()

    brief = f"""
OPERATIONS BRIEF
================

Connection assessments: {len(assessment)}

Missed connections: {missed}
At-risk connections: {at_risk}

Critical priority cases: {critical}
High priority cases: {high}

Recommended focus:
- Review critical and missed connections first.
- Monitor high-priority cases closely.
- Recalculate connection risk after significant disruption updates.
- Record operational actions taken for affected cases.
"""

    return brief.strip()