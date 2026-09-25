from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd


SEED = 42

AIRPORTS = ["FIC", "NXA", "QRT", "VLM", "ZPR"]
AIRLINES = ["SKYX", "AEROX", "FLYN", "NOVAIR"]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def generate_flights(num_flights: int = 40) -> pd.DataFrame:
    """Generate synthetic fictional flight records."""

    random.seed(SEED)

    base_time = datetime(2026, 10, 1, 6, 0)

    records = []

    for index in range(1, num_flights + 1):
        origin, destination = random.sample(AIRPORTS, 2)

        scheduled_departure = base_time + timedelta(
            minutes=random.randint(0, 900)
        )

        flight_duration = random.randint(60, 240)

        scheduled_arrival = scheduled_departure + timedelta(
            minutes=flight_duration
        )

        status = random.choices(
            ["ON_TIME", "DELAYED", "CANCELLED"],
            weights=[70, 25, 5],
            k=1,
        )[0]

        if status == "ON_TIME":
            delay_minutes = 0
            actual_arrival = scheduled_arrival

        elif status == "DELAYED":
            delay_minutes = random.randint(15, 180)
            actual_arrival = scheduled_arrival + timedelta(
                minutes=delay_minutes
            )

        else:
            delay_minutes = 0
            actual_arrival = pd.NaT

        records.append(
            {
                "flight_id": f"FL{index:04d}",
                "airline": random.choice(AIRLINES),
                "origin": origin,
                "destination": destination,
                "scheduled_arrival": scheduled_arrival,
                "actual_arrival": actual_arrival,
                "scheduled_departure": scheduled_departure,
                "delay_minutes": delay_minutes,
                "status": status,
            }
        )

    return pd.DataFrame(records)


def generate_connections(
    flights: pd.DataFrame,
    num_connections: int = 80,
) -> pd.DataFrame:
    """Generate synthetic passenger connection records."""

    random.seed(SEED)

    records = []

    valid_inbound = flights[
        flights["status"] != "CANCELLED"
    ].reset_index(drop=True)

    for index in range(1, num_connections + 1):
        inbound = valid_inbound.sample(
            n=1,
            random_state=SEED + index,
        ).iloc[0]

        minimum_connection = random.choice(
            [45, 60, 75, 90]
        )

        possible_onward = flights[
            (flights["status"] != "CANCELLED")
            & (flights["flight_id"] != inbound["flight_id"])
            & (flights["origin"] == inbound["destination"])
            & (
                flights["scheduled_departure"]
                >= inbound["actual_arrival"]
                + timedelta(minutes=minimum_connection)
            )
        ]

        if possible_onward.empty:
            possible_onward = flights[
                (flights["status"] != "CANCELLED")
                & (flights["flight_id"] != inbound["flight_id"])
                & (flights["origin"] == inbound["destination"])
            ]

        if possible_onward.empty:
            possible_onward = flights[
                (flights["status"] != "CANCELLED")
                & (flights["flight_id"] != inbound["flight_id"])
            ]

        onward = possible_onward.sample(
            n=1,
            random_state=SEED + index + 200,
        ).iloc[0]

        records.append(
            {
                "connection_id": f"CON{index:04d}",
                "passenger_id": f"PAX{index:05d}",
                "inbound_flight_id": inbound["flight_id"],
                "onward_flight_id": onward["flight_id"],
                "minimum_connection_minutes": minimum_connection,
            }
        )

    return pd.DataFrame(records)


def generate_transfer_times() -> pd.DataFrame:
    """Generate fictional airport transfer-time records."""

    random.seed(SEED)

    return pd.DataFrame(
        [
            {
                "airport_code": airport,
                "transfer_minutes": random.choice(
                    [30, 40, 45, 50, 60]
                ),
            }
            for airport in AIRPORTS
        ]
    )


def generate_all_data() -> None:
    """Generate and save all synthetic datasets."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    flights = generate_flights()
    connections = generate_connections(flights)
    transfer_times = generate_transfer_times()

    flights.to_csv(
        DATA_DIR / "flights.csv",
        index=False,
    )

    connections.to_csv(
        DATA_DIR / "connections.csv",
        index=False,
    )

    transfer_times.to_csv(
        DATA_DIR / "airport_transfer_times.csv",
        index=False,
    )


if __name__ == "__main__":
    generate_all_data()
    print("Synthetic datasets generated successfully.")