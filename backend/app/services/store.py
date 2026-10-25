"""SQLite persistence for January 2026 wind data."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from app.config import BACKEND_ROOT, get_settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fuelhh_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    publish_time TEXT NOT NULL,
    settlement_date TEXT,
    settlement_period INTEGER,
    fuel_type TEXT,
    generation REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS windfor_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    publish_time TEXT NOT NULL,
    generation REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS actuals_outturn (
    settlement_date TEXT NOT NULL,
    settlement_period INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    generation_mw REAL NOT NULL,
    publish_time TEXT,
    PRIMARY KEY (settlement_date, settlement_period)
);

CREATE TABLE IF NOT EXISTS forecasts_decision (
    settlement_date TEXT NOT NULL,
    settlement_period INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    generation_mw REAL,
    publish_time TEXT,
    decision_cutoff TEXT,
    PRIMARY KEY (settlement_date, settlement_period)
);
"""


def _iso(value: Any) -> Optional[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class Store:
    def __init__(self, db_path: Optional[Path] = None):
        settings = get_settings()
        self.db_path = db_path or settings.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def set_meta(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
            conn.commit()

    def get_meta(self, key: str) -> Optional[str]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT value FROM meta WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else None

    def clear_all(self) -> None:
        with self.connect() as conn:
            for table in (
                "fuelhh_raw",
                "windfor_raw",
                "actuals_outturn",
                "forecasts_decision",
                "meta",
            ):
                conn.execute(f"DELETE FROM {table}")
            conn.commit()

    def insert_fuelhh_raw(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        with self.connect() as conn:
            conn.executemany(
                "INSERT INTO fuelhh_raw(start_time, publish_time, settlement_date, "
                "settlement_period, fuel_type, generation) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        r["startTime"],
                        r["publishTime"],
                        r.get("settlementDate"),
                        r.get("settlementPeriod"),
                        r.get("fuelType"),
                        float(r["generation"]),
                    )
                    for r in rows
                ],
            )
            conn.commit()
        return len(rows)

    def insert_windfor_raw(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        with self.connect() as conn:
            conn.executemany(
                "INSERT INTO windfor_raw(start_time, publish_time, generation) "
                "VALUES (?, ?, ?)",
                [
                    (r["startTime"], r["publishTime"], float(r["generation"]))
                    for r in rows
                ],
            )
            conn.commit()
        return len(rows)

    def replace_actuals(self, df: pd.DataFrame) -> int:
        with self.connect() as conn:
            conn.execute("DELETE FROM actuals_outturn")
            if not df.empty:
                conn.executemany(
                    "INSERT INTO actuals_outturn"
                    "(settlement_date, settlement_period, start_time, generation_mw, publish_time) "
                    "VALUES (?, ?, ?, ?, ?)",
                    [
                        (
                            _iso(row.settlement_date)[:10]
                            if hasattr(row.settlement_date, "isoformat")
                            else str(row.settlement_date)[:10],
                            int(row.settlement_period),
                            _iso(row.start_time),
                            float(row.generation_mw),
                            _iso(row.publish_time),
                        )
                        for row in df.itertuples(index=False)
                    ],
                )
            conn.commit()
        return len(df)

    def replace_forecasts_decision(self, df: pd.DataFrame) -> int:
        with self.connect() as conn:
            conn.execute("DELETE FROM forecasts_decision")
            if not df.empty:
                conn.executemany(
                    "INSERT INTO forecasts_decision"
                    "(settlement_date, settlement_period, start_time, generation_mw, "
                    "publish_time, decision_cutoff) VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        (
                            str(row.settlement_date)[:10],
                            int(row.settlement_period),
                            _iso(row.start_time),
                            None
                            if row.generation_mw is None
                            or (
                                isinstance(row.generation_mw, float)
                                and pd.isna(row.generation_mw)
                            )
                            else float(row.generation_mw),
                            _iso(getattr(row, "publish_time", None)),
                            _iso(getattr(row, "decision_cutoff", None)),
                        )
                        for row in df.itertuples(index=False)
                    ],
                )
            conn.commit()
        return len(df)

    def load_actuals(
        self, from_date: Optional[date] = None, to_date: Optional[date] = None
    ) -> pd.DataFrame:
        sql = "SELECT * FROM actuals_outturn WHERE 1=1"
        params: list[Any] = []
        if from_date:
            sql += " AND settlement_date >= ?"
            params.append(from_date.isoformat())
        if to_date:
            sql += " AND settlement_date <= ?"
            params.append(to_date.isoformat())
        sql += " ORDER BY settlement_date, settlement_period"
        with self.connect() as conn:
            df = pd.read_sql_query(sql, conn, params=params)
        if df.empty:
            return df
        df["settlement_date"] = pd.to_datetime(df["settlement_date"]).dt.date
        df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
        if "publish_time" in df.columns:
            df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
        return df

    def load_decision_forecasts(
        self, delivery_date: Optional[date] = None
    ) -> pd.DataFrame:
        sql = "SELECT * FROM forecasts_decision WHERE 1=1"
        params: list[Any] = []
        if delivery_date:
            sql += " AND settlement_date = ?"
            params.append(delivery_date.isoformat())
        sql += " ORDER BY settlement_date, settlement_period"
        with self.connect() as conn:
            df = pd.read_sql_query(sql, conn, params=params)
        if df.empty:
            return df
        df["settlement_date"] = pd.to_datetime(df["settlement_date"]).dt.date
        df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
        df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True, errors="coerce")
        df["decision_cutoff"] = pd.to_datetime(
            df["decision_cutoff"], utc=True, errors="coerce"
        )
        return df

    def coverage_counts(self) -> dict[str, int]:
        with self.connect() as conn:
            actuals = conn.execute(
                "SELECT COUNT(DISTINCT settlement_date) AS n FROM actuals_outturn"
            ).fetchone()["n"]
            forecasts = conn.execute(
                "SELECT COUNT(DISTINCT settlement_date) AS n FROM forecasts_decision "
                "WHERE generation_mw IS NOT NULL"
            ).fetchone()["n"]
        return {"actuals_days": actuals, "forecast_days": forecasts}

    def ensure_db(self) -> bool:
        """Return True if DB has data; try seed load if empty."""
        self.init_schema()
        counts = self.coverage_counts()
        if counts["actuals_days"] > 0 and counts["forecast_days"] > 0:
            return True
        seed_dir = BACKEND_ROOT / "data" / "seed"
        seed_db = seed_dir / "wind_jan2026.db"
        if seed_db.exists():
            # Prefer copying slim seed DB when live DB is empty
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.db_path.write_bytes(seed_db.read_bytes())
            counts = self.coverage_counts()
            if counts["actuals_days"] > 0:
                return True
        actuals_json = seed_dir / "actuals_outturn.json"
        forecasts_json = seed_dir / "forecasts_decision.json"
        if actuals_json.exists() and forecasts_json.exists():
            self._load_json_seed(actuals_json, forecasts_json)
            return True
        return False

    def _load_json_seed(self, actuals_path: Path, forecasts_path: Path) -> None:
        actuals = json.loads(actuals_path.read_text(encoding="utf-8"))
        forecasts = json.loads(forecasts_path.read_text(encoding="utf-8"))
        with self.connect() as conn:
            conn.execute("DELETE FROM actuals_outturn")
            conn.execute("DELETE FROM forecasts_decision")
            conn.executemany(
                "INSERT INTO actuals_outturn"
                "(settlement_date, settlement_period, start_time, generation_mw, publish_time) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        r["settlement_date"],
                        r["settlement_period"],
                        r["start_time"],
                        r["generation_mw"],
                        r.get("publish_time"),
                    )
                    for r in actuals
                ],
            )
            conn.executemany(
                "INSERT INTO forecasts_decision"
                "(settlement_date, settlement_period, start_time, generation_mw, "
                "publish_time, decision_cutoff) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        r["settlement_date"],
                        r["settlement_period"],
                        r["start_time"],
                        r.get("generation_mw"),
                        r.get("publish_time"),
                        r.get("decision_cutoff"),
                    )
                    for r in forecasts
                ],
            )
            conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                ("last_sync_at", datetime.now(timezone.utc).isoformat()),
            )
            conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                ("data_source", "seed_json"),
            )
            conn.commit()
