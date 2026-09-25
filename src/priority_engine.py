def calculate_priority_score(
    status: str,
    delay_minutes: int,
    available_minutes: int,
    required_minutes: int,
) -> int:
    """
    Calculate an operational priority score from 0 to 100.
    Higher scores indicate greater urgency.
    """

    score = 0

    # Connection status
    if status == "MISSED":
        score += 60
    elif status == "AT_RISK":
        score += 40
    else:
        score += 10

    # Flight delay
    if delay_minutes >= 120:
        score += 25
    elif delay_minutes >= 60:
        score += 15
    elif delay_minutes >= 30:
        score += 10

    # Remaining connection buffer
    buffer_minutes = available_minutes - required_minutes

    if buffer_minutes < 0:
        score += 15
    elif buffer_minutes <= 15:
        score += 10
    elif buffer_minutes <= 30:
        score += 5

    return min(score, 100)


def classify_priority(score: int) -> str:
    """Convert a numerical score into an operational priority."""

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"