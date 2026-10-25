"""Derive outturn wind generation from FUELHH rows."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.normalize import parse_iso, settlement_date_from_start, settlement_period_for_start


def build_outturn(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Keep latest publishTime per startTime for WIND fuelType."""
    if not rows:
        return pd.DataFrame(
            columns=[
                "settlement_date",
                "settlement_period",
                "start_time",
                "generation_mw",
                "publish_time",
            ]
        )

    records = []
    for row in rows:
        if str(row.get("fuelType", "")).upper() != "WIND":
            continue
        start = parse_iso(row["startTime"])
        publish = parse_iso(row["publishTime"])
        generation = float(row["generation"])
        settlement_date = row.get("settlementDate")
        if settlement_date:
            sd = pd.Timestamp(settlement_date).date()
        else:
            sd = settlement_date_from_start(start)
        sp = int(row.get("settlementPeriod") or settlement_period_for_start(start))
        records.append(
            {
                "settlement_date": sd,
                "settlement_period": sp,
                "start_time": start,
                "generation_mw": generation,
                "publish_time": publish,
            }
        )

    df = pd.DataFrame(records)
    if df.empty:
        return df
    df = df.sort_values("publish_time")
    out = df.groupby("start_time", as_index=False).tail(1).reset_index(drop=True)
    return out[
        [
            "settlement_date",
            "settlement_period",
            "start_time",
            "generation_mw",
            "publish_time",
        ]
    ]
