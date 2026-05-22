from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd


PROJECT_COLUMNS = [
    "message_id",
    "source_system",
    "message_timestamp",
    "mother_id",
    "mother_birth_date",
    "postal_code_prefix",
    "pregnancy_id",
    "gestational_age_weeks",
    "gravida",
    "parity",
    "delivery_id",
    "delivery_date",
    "delivery_mode",
    "place_of_birth",
    "child_id",
    "child_sex",
    "birth_weight_grams",
    "apgar_5min",
    "admission_nicu",
]


def initialize_database(
    db_path: str | Path,
    schema_path: str | Path,
) -> None:
    """
    Initialize the SQLite database using the provided SQL schema.

    Args:
        db_path: Path to the SQLite database file.
        schema_path: Path to the SQL schema file.
    """

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        with open(schema_path, "r", encoding="utf-8") as file:
            conn.executescript(file.read())


def load_valid_records(
    db_path: str | Path,
    records: Iterable[Dict[str, Any]],
) -> None:
    """
    Load validated records into the perinatal_records table.

    Existing records are cleared before insertion to keep the
    pipeline rerunnable and idempotent.

    Args:
        db_path: Path to the SQLite database file.
        records: Iterable of validated perinatal records.
    """

    df = pd.DataFrame(list(records))

    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM perinatal_records")

        if df.empty:
            return

        df = df[PROJECT_COLUMNS]

        df.to_sql(
            "perinatal_records",
            conn,
            if_exists="append",
            index=False,
        )


def load_rejected_records(
    db_path: str | Path,
    rejected: List[Dict[str, Any]],
) -> None:
    """
    Load rejected records and validation errors into the rejected_records table.

    Args:
        db_path: Path to the SQLite database file.
        rejected: List of rejected records with error details.
    """

    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM rejected_records")

        if not rejected:
            return

        df = pd.DataFrame(rejected)

        df.to_sql(
            "rejected_records",
            conn,
            if_exists="append",
            index=False,
        )