"""Pure-function tests for forecast selection and metrics."""

from datetime import date, datetime, timezone

from app.services.forecast_selection import select_decision_forecast
from app.services.metrics import compute_metrics
import pandas as pd


def test_decision_cutoff_selects_latest_before_gate():
    rows = [
        {
            "startTime": "2026-01-15T12:00:00Z",
            "publishTime": "2026-01-14T08:00:00Z",
            "generation": 1000,
        },
        {
            "startTime": "2026-01-15T12:00:00Z",
            "publishTime": "2026-01-14T10:30:00Z",
            "generation": 1100,
        },
        {
            "startTime": "2026-01-15T12:00:00Z",
            "publishTime": "2026-01-14T12:00:00Z",  # after 11:00 London (=11:00 UTC in Jan)
            "generation": 9999,
        },
    ]
    out = select_decision_forecast(rows, date(2026, 1, 15), "11:00", "Europe/London")
    noon = out[out["settlement_period"] == 25]  # 12:00 London in winter = SP 25
    # Hourly expand: 12:00 and 12:30 both get 1100
    vals = out[out["start_time"].dt.hour == 12]["generation_mw"].dropna().unique()
    assert 1100.0 in vals
    assert 9999.0 not in out["generation_mw"].dropna().values


def test_metrics_mae():
    df = pd.DataFrame(
        {
            "forecast_mw": [100.0, 200.0],
            "actual_mw": [90.0, 220.0],
        }
    )
    m = compute_metrics(df)
    assert m["n"] == 2
    assert m["mae_mw"] == 15.0
    assert m["bias_mw"] == -5.0
