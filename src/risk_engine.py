from datetime import datetime, timedelta

import pandas as pd


def calculate_connection_status(
    actual_arrival: datetime,
    onward_departure: datetime,
    transfer_minutes: int,
    minimum_connection_minutes: int,
) -> str:
    """
    Determine whether a passenger can realistically make
    their onward connection.
    """

    required_time = (
    actual_arrival
    + timedelta(minutes=int(transfer_minutes))
    + timedelta(minutes=int(minimum_connection_minutes))
)

    if onward_departure < required_time:
        return "MISSED"

    if onward_departure <= required_time + timedelta(minutes=15):
        return "AT_RISK"

    return "SAFE"


def assess_connections(
    flights: pd.DataFrame,
    connections: pd.DataFrame,
    transfer_times: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate connection risk for every passenger connection.
    """

    flight_lookup = flights.set_index("flight_id")
    transfer_lookup = transfer_times.set_index("airport_code")

    results = []

    for _, connection in connections.iterrows():
        inbound = flight_lookup.loc[
            connection["inbound_flight_id"]
        ]

        onward = flight_lookup.loc[
            connection["onward_flight_id"]
        ]

        if pd.isna(inbound["actual_arrival"]):
            status = "MISSED"
            available_minutes = 0
            required_minutes = (
                connection["minimum_connection_minutes"]
            )

        else:
            transfer_minutes = transfer_lookup.loc[
                inbound["destination"],
                "transfer_minutes",
            ]

            actual_arrival = pd.to_datetime(
                inbound["actual_arrival"]
            )

            onward_departure = pd.to_datetime(
                onward["scheduled_departure"]
            )

            available_minutes = int(
                (
                    onward_departure - actual_arrival
                ).total_seconds()
                / 60
            )

            required_minutes = (
                transfer_minutes
                + connection["minimum_connection_minutes"]
            )

            status = calculate_connection_status(
                actual_arrival=actual_arrival,
                onward_departure=onward_departure,
                transfer_minutes=transfer_minutes,
                minimum_connection_minutes=connection[
                    "minimum_connection_minutes"
                ],
            )

        results.append(
            {
                "connection_id": connection["connection_id"],
                "passenger_id": connection["passenger_id"],
                "inbound_flight_id": connection["inbound_flight_id"],
                "onward_flight_id": connection["onward_flight_id"],
                "available_minutes": available_minutes,
                "required_minutes": required_minutes,
                "status": status,
            }
        )

    return pd.DataFrame(results)