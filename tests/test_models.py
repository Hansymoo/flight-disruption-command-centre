import pytest
from pydantic import ValidationError

from src.models import (
    AirportTransferTime,
    Connection,
    Flight,
)


def test_valid_flight():
    flight = Flight(
        flight_id="FL0001",
        airline="AEROX",
        origin="FIC",
        destination="ZPR",
        scheduled_departure="2026-10-01T10:00:00",
        scheduled_arrival="2026-10-01T12:00:00",
        actual_arrival="2026-10-01T12:15:00",
        delay_minutes=15,
        status="DELAYED",
    )

    assert flight.flight_id == "FL0001"
    assert flight.delay_minutes == 15


def test_invalid_flight_status():
    with pytest.raises(ValidationError):
        Flight(
            flight_id="FL0001",
            airline="AEROX",
            origin="FIC",
            destination="ZPR",
            scheduled_departure="2026-10-01T10:00:00",
            scheduled_arrival="2026-10-01T12:00:00",
            actual_arrival="2026-10-01T12:00:00",
            delay_minutes=0,
            status="UNKNOWN",
        )


def test_negative_delay_is_rejected():
    with pytest.raises(ValidationError):
        Flight(
            flight_id="FL0001",
            airline="AEROX",
            origin="FIC",
            destination="ZPR",
            scheduled_departure="2026-10-01T10:00:00",
            scheduled_arrival="2026-10-01T12:00:00",
            actual_arrival="2026-10-01T12:00:00",
            delay_minutes=-10,
            status="ON_TIME",
        )


def test_cancelled_flight_can_have_no_actual_arrival():
    flight = Flight(
        flight_id="FL0002",
        airline="SKYX",
        origin="NXA",
        destination="QRT",
        scheduled_departure="2026-10-01T11:00:00",
        scheduled_arrival="2026-10-01T13:00:00",
        actual_arrival=None,
        delay_minutes=0,
        status="CANCELLED",
    )

    assert flight.actual_arrival is None


def test_valid_connection():
    connection = Connection(
        connection_id="CON0001",
        passenger_id="PAX00001",
        inbound_flight_id="FL0001",
        onward_flight_id="FL0002",
        minimum_connection_minutes=60,
    )

    assert connection.minimum_connection_minutes == 60


def test_invalid_connection_time():
    with pytest.raises(ValidationError):
        Connection(
            connection_id="CON0001",
            passenger_id="PAX00001",
            inbound_flight_id="FL0001",
            onward_flight_id="FL0002",
            minimum_connection_minutes=10,
        )


def test_valid_transfer_time():
    transfer = AirportTransferTime(
        airport_code="FIC",
        transfer_minutes=45,
    )

    assert transfer.transfer_minutes == 45