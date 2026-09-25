from datetime import datetime

import pandas as pd

from src.risk_engine import (
    assess_connections,
    calculate_connection_status,
)


def test_connection_is_safe():
    status = calculate_connection_status(
        actual_arrival=datetime(2026, 10, 1, 10, 0),
        onward_departure=datetime(2026, 10, 1, 12, 0),
        transfer_minutes=30,
        minimum_connection_minutes=45,
    )

    assert status == "SAFE"


def test_connection_is_at_risk():
    status = calculate_connection_status(
        actual_arrival=datetime(2026, 10, 1, 10, 0),
        onward_departure=datetime(2026, 10, 1, 11, 25),
        transfer_minutes=30,
        minimum_connection_minutes=45,
    )

    assert status == "AT_RISK"


def test_connection_is_missed():
    status = calculate_connection_status(
        actual_arrival=datetime(2026, 10, 1, 10, 0),
        onward_departure=datetime(2026, 10, 1, 11, 0),
        transfer_minutes=30,
        minimum_connection_minutes=45,
    )

    assert status == "MISSED"