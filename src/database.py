import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "operations.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the local SQLite database."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(DATABASE_PATH)


def initialise_database() -> None:
    """Create the required database tables."""

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS flights (
                flight_id TEXT PRIMARY KEY,
                airline TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                scheduled_departure TEXT NOT NULL,
                scheduled_arrival TEXT NOT NULL,
                actual_arrival TEXT,
                delay_minutes INTEGER NOT NULL,
                status TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS connections (
                connection_id TEXT PRIMARY KEY,
                passenger_id TEXT NOT NULL,
                inbound_flight_id TEXT NOT NULL,
                onward_flight_id TEXT NOT NULL,
                minimum_connection_minutes INTEGER NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS airport_transfer_times (
                airport_code TEXT PRIMARY KEY,
                transfer_minutes INTEGER NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS connection_assessments (
                connection_id TEXT PRIMARY KEY,
                passenger_id TEXT NOT NULL,
                inbound_flight_id TEXT NOT NULL,
                onward_flight_id TEXT NOT NULL,
                available_minutes INTEGER NOT NULL,
                required_minutes INTEGER NOT NULL,
                status TEXT NOT NULL,
                priority_score INTEGER NOT NULL,
                priority TEXT NOT NULL,
                buffer_minutes INTEGER NOT NULL
            )
            """
        )


def save_dataframe(
    dataframe: pd.DataFrame,
    table_name: str,
) -> None:
    """Replace the contents of a database table with a dataframe."""

    with get_connection() as connection:

        dataframe.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )


def load_table(table_name: str) -> pd.DataFrame:
    """Load a database table into a pandas dataframe."""

    with get_connection() as connection:

        return pd.read_sql_query(
            f"SELECT * FROM {table_name}",
            connection,
        )