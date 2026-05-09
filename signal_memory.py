import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Optional

# SQLite database file
DB_PATH = Path(__file__).parent / "signals.db"


def _get_connection() -> sqlite3.Connection:

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def init_db() -> None:

    with _get_connection() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT NOT NULL,

                pair TEXT NOT NULL,

                interval TEXT NOT NULL,

                signal TEXT NOT NULL,

                confidence INTEGER,

                trend TEXT,

                expiry TEXT,

                result TEXT
            )
            """
        )

        conn.commit()


def log_signal(
    *,
    pair: str,
    interval: str,
    signal: str,
    confidence: int,
    trend: str,
    expiry: str,
    result: Optional[str] = None,
) -> None:

    ts = datetime.datetime.utcnow().isoformat()

    with _get_connection() as conn:

        conn.execute(
            """
            INSERT INTO signals (

                timestamp,
                pair,
                interval,
                signal,
                confidence,
                trend,
                expiry,
                result

            )

            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                ts,
                pair,
                interval,
                signal,
                confidence,
                trend,
                expiry,
                result,
            ),
        )

        conn.commit()


def recent_signals(
    limit: int = 20
) -> List[Dict]:

    with _get_connection() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM signals
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


def win_rate(
    *,
    pair: Optional[str] = None,
    days: int = 7
) -> float:

    with _get_connection() as conn:

        condition = "result IS NOT NULL"

        params: List = []

        if pair:

            condition += " AND pair = ?"

            params.append(pair)

        if days:

            since = (
                datetime.datetime.utcnow()
                - datetime.timedelta(days=days)
            ).isoformat()

            condition += " AND timestamp >= ?"

            params.append(since)

        total_row = conn.execute(
            f"""
            SELECT COUNT(*) AS cnt
            FROM signals
            WHERE {condition}
            """,
            params,
        ).fetchone()

        total = total_row["cnt"]

        if total == 0:

            return 0.0

        win_row = conn.execute(
            f"""
            SELECT COUNT(*) AS cnt
            FROM signals
            WHERE {condition}
            AND result = 'WIN'
            """,
            params,
        ).fetchone()

        wins = win_row["cnt"]

        return wins / total