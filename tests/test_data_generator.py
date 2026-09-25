import pandas as pd

from src.data_generator import (
    generate_flights,
    generate_connections,
    generate_transfer_times,
)


def test_flights_have_required_columns():
    flights = generate_flights()

    required_columns = {
        "flight_id",
        "airline",
        "origin",
        "destination",
        "scheduled_arrival",
        "actual_arrival",
        "scheduled_departure",
        "delay_minutes",
        "status",
    }

    assert required_columns.issubset(flights.columns)


def test_flight_ids_are_unique():
    flights = generate_flights()

    assert flights["flight_id"].is_unique


def test_flight_required_fields_are_not_empty():
    flights = generate_flights()

    required_columns = [
        "flight_id",
        "airline",
        "origin",
        "destination",
        "status",
    ]

    for column in required_columns:
        assert flights[column].notna().all()
        assert (flights[column].astype(str).str.strip() != "").all()


def test_connections_reference_existing_flights():
    flights = generate_flights()
    connections = generate_connections(flights)

    flight_ids = set(flights["flight_id"])

    assert connections["inbound_flight_id"].isin(flight_ids).all()
    assert connections["onward_flight_id"].isin(flight_ids).all()


def test_connection_ids_are_unique():
    flights = generate_flights()
    connections = generate_connections(flights)

    assert connections["connection_id"].is_unique
    assert connections["passenger_id"].is_unique


def test_transfer_times_have_required_columns():
    transfer_times = generate_transfer_times()

    assert "airport_code" in transfer_times.columns
    assert "transfer_minutes" in transfer_times.columns
    assert transfer_times["airport_code"].notna().all()
    assert transfer_times["transfer_minutes"].notna().all()


def test_generation_is_reproducible():
    flights_first = generate_flights()
    flights_second = generate_flights()

    pd.testing.assert_frame_equal(
        flights_first,
        flights_second,
    )