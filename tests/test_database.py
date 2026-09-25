import sqlite3

import pandas as pd

from src.database import (
    initialise_database,
    save_dataframe,
    load_table,
)


def test_database_tables_can_be_created(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "test.db"

    monkeypatch.setattr(
        "src.database.DATABASE_PATH",
        database_path,
    )

    initialise_database()

    with sqlite3.connect(database_path) as connection:

        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """,
            connection,
        )

    table_names = set(tables["name"])

    assert "flights" in table_names
    assert "connections" in table_names
    assert "airport_transfer_times" in table_names
    assert "connection_assessments" in table_names


def test_dataframe_can_be_saved_and_loaded(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "test.db"

    monkeypatch.setattr(
        "src.database.DATABASE_PATH",
        database_path,
    )

    dataframe = pd.DataFrame(
        {
            "flight_id": ["FL0001"],
            "status": ["DELAYED"],
        }
    )

    save_dataframe(
        dataframe,
        "test_flights",
    )

    loaded = load_table(
        "test_flights",
    )

    assert len(loaded) == 1
    assert loaded.loc[0, "flight_id"] == "FL0001"
    assert loaded.loc[0, "status"] == "DELAYED"