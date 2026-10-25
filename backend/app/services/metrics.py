"""Forecast accuracy metrics."""

from __future__ import annotations

from datetime import date
from typing import Optional

import numpy as np
import pandas as pd


EPS = 1.0  # MW floor for MAPE denominator


def compute_metrics(df: pd.DataFrame) -> dict:
    """Expect columns forecast_mw, actual_mw. Returns MAE, RMSE, MAPE, bias, n."""
    if df.empty:
        return {
            "mae_mw": 0.0,
            "rmse_mw": 0.0,
            "mape_pct": 0.0,
            "bias_mw": 0.0,
            "n": 0,
            "mean_actual_mw": 0.0,
            "mean_forecast_mw": 0.0,
        }

    work = df.dropna(subset=["forecast_mw", "actual_mw"]).copy()
    n = len(work)
    if n == 0:
        return {
            "mae_mw": 0.0,
            "rmse_mw": 0.0,
            "mape_pct": 0.0,
            "bias_mw": 0.0,
            "n": 0,
            "mean_actual_mw": 0.0,
            "mean_forecast_mw": 0.0,
        }

    err = work["forecast_mw"].astype(float) - work["actual_mw"].astype(float)
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    mape = float(
        np.mean(np.abs(err) / np.maximum(work["actual_mw"].astype(float), EPS)) * 100
    )
    bias = float(np.mean(err))
    return {
        "mae_mw": round(mae, 2),
        "rmse_mw": round(rmse, 2),
        "mape_pct": round(mape, 2),
        "bias_mw": round(bias, 2),
        "n": n,
        "mean_actual_mw": round(float(work["actual_mw"].mean()), 2),
        "mean_forecast_mw": round(float(work["forecast_mw"].mean()), 2),
    }


def daily_metrics(joined: pd.DataFrame) -> pd.DataFrame:
    if joined.empty:
        return pd.DataFrame()

    rows = []
    for sd, group in joined.groupby("settlement_date"):
        m = compute_metrics(group)
        rows.append({"settlement_date": sd, **m})
    return pd.DataFrame(rows).sort_values("settlement_date").reset_index(drop=True)


def pct_within_threshold(joined: pd.DataFrame, threshold_mw: float = 500.0) -> Optional[float]:
    work = joined.dropna(subset=["forecast_mw", "actual_mw"])
    if work.empty:
        return None
    err = (work["forecast_mw"] - work["actual_mw"]).abs()
    return round(float((err <= threshold_mw).mean() * 100), 2)


def join_forecast_actual(
    forecasts: pd.DataFrame, actuals: pd.DataFrame
) -> pd.DataFrame:
    if forecasts.empty:
        return pd.DataFrame()
    f = forecasts.rename(columns={"generation_mw": "forecast_mw"})
    a = actuals.rename(columns={"generation_mw": "actual_mw"})
    cols_f = ["settlement_date", "settlement_period", "start_time", "forecast_mw"]
    if "publish_time" in f.columns:
        cols_f.append("publish_time")
    merged = f[cols_f].merge(
        a[["settlement_date", "settlement_period", "actual_mw"]],
        on=["settlement_date", "settlement_period"],
        how="left",
    )
    merged["error_mw"] = merged["forecast_mw"] - merged["actual_mw"]
    return merged
