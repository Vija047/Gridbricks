"""Select decision-relevant WINDFOR forecasts for day-ahead procurement."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from app.services.normalize import (
    decision_cutoff_utc,
    expand_hourly_to_half_hours,
    parse_iso,
    settlement_date_from_start,
    settlement_period_for_start,
    start_times_for_settlement_date,
)


def rows_to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        start = parse_iso(row["startTime"])
        publish = parse_iso(row["publishTime"])
        generation = float(row["generation"])
        for expanded_start, mw in expand_hourly_to_half_hours(start, generation):
            records.append(
                {
                    "start_time": expanded_start,
                    "publish_time": publish,
                    "generation_mw": mw,
                    "settlement_date": settlement_date_from_start(expanded_start),
                    "settlement_period": settlement_period_for_start(expanded_start),
                }
            )
    if not records:
        return pd.DataFrame(
            columns=[
                "start_time",
                "publish_time",
                "generation_mw",
                "settlement_date",
                "settlement_period",
            ]
        )
    return pd.DataFrame(records)


def select_decision_forecast(
    windfor_rows: list[dict[str, Any]] | pd.DataFrame,
    delivery_date: date,
    cutoff_local_time: str = "11:00",
    timezone_name: str = "Europe/London",
) -> pd.DataFrame:
    """For each of 48 SPs on delivery_date, pick latest publish <= cutoff."""
    cutoff = decision_cutoff_utc(delivery_date, cutoff_local_time, timezone_name)
    if isinstance(windfor_rows, pd.DataFrame):
        df = windfor_rows.copy()
    else:
        df = rows_to_frame(windfor_rows)

    grid = start_times_for_settlement_date(delivery_date)
    if df.empty:
        return pd.DataFrame(
            [
                {
                    "settlement_date": delivery_date,
                    "settlement_period": i + 1,
                    "start_time": st,
                    "generation_mw": None,
                    "publish_time": None,
                    "decision_cutoff": cutoff,
                }
                for i, st in enumerate(grid)
            ]
        )

    # Prefer exact 30-min points: if both :00 and expanded :30 exist from hourly,
    # later sort+groupby keeps the latest publish; if an exact half-hour exists
    # with same publish, keep one row per start_time after filter.
    eligible = df[
        (df["settlement_date"] == delivery_date) & (df["publish_time"] <= cutoff)
    ].copy()

    selected_rows = []
    for i, st in enumerate(grid):
        subset = eligible[eligible["start_time"] == st]
        if subset.empty:
            selected_rows.append(
                {
                    "settlement_date": delivery_date,
                    "settlement_period": i + 1,
                    "start_time": st,
                    "generation_mw": None,
                    "publish_time": None,
                    "decision_cutoff": cutoff,
                }
            )
            continue
        best = subset.sort_values("publish_time").iloc[-1]
        selected_rows.append(
            {
                "settlement_date": delivery_date,
                "settlement_period": i + 1,
                "start_time": st,
                "generation_mw": float(best["generation_mw"]),
                "publish_time": best["publish_time"],
                "decision_cutoff": cutoff,
            }
        )
    return pd.DataFrame(selected_rows)


def select_all_january(
    windfor_df: pd.DataFrame,
    dates: list[date],
    cutoff_local_time: str,
    timezone_name: str,
) -> pd.DataFrame:
    frames = [
        select_decision_forecast(windfor_df, d, cutoff_local_time, timezone_name)
        for d in dates
    ]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
