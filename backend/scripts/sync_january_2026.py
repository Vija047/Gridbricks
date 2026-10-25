#!/usr/bin/env python3
"""Fetch January 2026 FUELHH (WIND) + WINDFOR from Elexon and build SQLite store.

WINDFOR stream is queried by publishDateTime windows (settlementDate filters are
unreliable on this dataset) and filtered client-side to startTimes in Jan 2026.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.clients.elexon import ElexonClient  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.services.actuals import build_outturn  # noqa: E402
from app.services.forecast_selection import (  # noqa: E402
    rows_to_frame,
    select_all_january,
)
from app.services.store import Store  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sync")


def daterange(start: date, end: date) -> list[date]:
    days = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += timedelta(days=1)
    return days


def export_seed(store: Store) -> None:
    seed_dir = BACKEND_ROOT / "data" / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)
    actuals = store.load_actuals()
    forecasts = store.load_decision_forecasts()

    def frame_to_records(df: pd.DataFrame) -> list[dict]:
        records = []
        for row in df.itertuples(index=False):
            rec = {}
            for col in df.columns:
                val = getattr(row, col)
                if isinstance(val, pd.Timestamp):
                    rec[col] = val.isoformat().replace("+00:00", "Z")
                elif isinstance(val, datetime):
                    rec[col] = val.isoformat().replace("+00:00", "Z")
                elif isinstance(val, date):
                    rec[col] = val.isoformat()
                elif val is None or (isinstance(val, float) and pd.isna(val)):
                    rec[col] = None
                else:
                    rec[col] = val if not (isinstance(val, float) and pd.isna(val)) else None
            records.append(rec)
        return records

    (seed_dir / "actuals_outturn.json").write_text(
        json.dumps(frame_to_records(actuals)), encoding="utf-8"
    )
    (seed_dir / "forecasts_decision.json").write_text(
        json.dumps(frame_to_records(forecasts)), encoding="utf-8"
    )
    # Slim seed DB (processed tables only — not raw Elexon dumps)
    seed_db = seed_dir / "wind_jan2026.db"
    if seed_db.exists():
        seed_db.unlink()
    slim = Store(seed_db)
    slim.init_schema()
    slim.replace_actuals(actuals)
    slim.replace_forecasts_decision(forecasts)
    slim.set_meta("last_sync_at", store.get_meta("last_sync_at") or "")
    slim.set_meta("data_source", "seed")
    import sqlite3

    with sqlite3.connect(seed_db) as conn:
        conn.execute("VACUUM")
    logger.info("Seed exported to %s (slim db %s bytes)", seed_dir, seed_db.stat().st_size)


def main() -> None:
    settings = get_settings()
    scope_start = date.fromisoformat(settings.scope_start)
    scope_end = date.fromisoformat(settings.scope_end)
    publish_start = date.fromisoformat(settings.forecast_publish_from)

    client = ElexonClient(settings.elexon_base_url)
    store = Store()
    store.init_schema()
    store.clear_all()

    # --- Actuals ---
    all_fuelhh: list[dict] = []
    for chunk_from, chunk_to in client.iter_date_chunks(scope_start, scope_end, 5):
        logger.info("Fetching FUELHH WIND %s → %s", chunk_from, chunk_to)
        rows = client.fetch_fuelhh_wind(chunk_from, chunk_to)
        logger.info("  got %s rows", len(rows))
        all_fuelhh.extend(rows)

    store.insert_fuelhh_raw(all_fuelhh)
    outturn = build_outturn(all_fuelhh)
    store.replace_actuals(outturn)
    logger.info("Outturn intervals: %s", len(outturn))

    # --- Forecasts by publish day (reliable filter) ---
    seen: set[tuple[str, str]] = set()
    all_windfor: list[dict] = []
    for pub_day in daterange(publish_start, scope_end):
        pub_from = datetime(pub_day.year, pub_day.month, pub_day.day, 0, 0, tzinfo=timezone.utc)
        pub_to = datetime(
            pub_day.year, pub_day.month, pub_day.day, 23, 59, 59, tzinfo=timezone.utc
        )
        logger.info("Fetching WINDFOR publishes on %s", pub_day)
        rows = client.fetch_windfor_by_publish(pub_from, pub_to)
        kept = 0
        for row in rows:
            start = row.get("startTime", "")
            # Keep forecasts targeting Jan 2026 (and late Dec for SP boundary safety)
            if not (start.startswith("2026-01") or start.startswith("2025-12-31")):
                continue
            key = (row["startTime"], row["publishTime"])
            if key in seen:
                continue
            seen.add(key)
            all_windfor.append(row)
            kept += 1
        logger.info("  raw %s, kept unique in-scope %s (total %s)", len(rows), kept, len(all_windfor))

    store.insert_windfor_raw(all_windfor)
    windfor_df = rows_to_frame(all_windfor)
    logger.info("Expanded forecast rows: %s", len(windfor_df))

    decision = select_all_january(
        windfor_df,
        daterange(scope_start, scope_end),
        settings.decision_cutoff_local_time,
        settings.decision_timezone,
    )
    store.replace_forecasts_decision(decision)
    covered = (
        decision.groupby("settlement_date")["generation_mw"].apply(lambda s: s.notna().any()).sum()
    )
    logger.info(
        "Decision forecasts written: %s rows; days with data: %s", len(decision), int(covered)
    )

    store.set_meta("last_sync_at", datetime.now(timezone.utc).isoformat())
    store.set_meta("data_source", "elexon_live")
    export_seed(store)
    logger.info("Sync complete → %s", store.db_path)


if __name__ == "__main__":
    main()
