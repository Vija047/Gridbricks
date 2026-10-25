import math
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.models.schemas import (
    AccuracySeriesResponse,
    AccuracySummaryResponse,
    DailyMetrics,
    IntervalPoint,
)
from app.services.metrics import (
    compute_metrics,
    daily_metrics,
    join_forecast_actual,
    pct_within_threshold,
)
from app.services.store import Store

router = APIRouter(prefix="/api/v1", tags=["accuracy"])


def _clean(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "to_pydatetime"):
        return v.to_pydatetime()
    return v


@router.get("/accuracy/summary", response_model=AccuracySummaryResponse)
def accuracy_summary(
    from_date: date = Query(default=None, alias="from"),
    to_date: date = Query(default=None, alias="to"),
) -> AccuracySummaryResponse:
    settings = get_settings()
    from_date = from_date or date.fromisoformat(settings.scope_start)
    to_date = to_date or date.fromisoformat(settings.scope_end)

    store = Store()
    store.ensure_db()
    forecasts = store.load_decision_forecasts()
    if forecasts.empty:
        raise HTTPException(status_code=404, detail="No forecast data available")
    forecasts = forecasts[
        (forecasts["settlement_date"] >= from_date)
        & (forecasts["settlement_date"] <= to_date)
    ]
    actuals = store.load_actuals(from_date, to_date)
    joined = join_forecast_actual(forecasts, actuals)
    overall = compute_metrics(joined)
    daily = daily_metrics(joined)
    overall_metrics = DailyMetrics(
        settlement_date=from_date,
        **overall,
    )
    daily_list = [
        DailyMetrics(
            settlement_date=row.settlement_date,
            mae_mw=float(row.mae_mw),
            rmse_mw=float(row.rmse_mw),
            mape_pct=float(row.mape_pct),
            bias_mw=float(row.bias_mw),
            n=int(row.n),
            mean_actual_mw=float(row.mean_actual_mw),
            mean_forecast_mw=float(row.mean_forecast_mw),
        )
        for row in daily.itertuples(index=False)
    ]
    return AccuracySummaryResponse(
        from_date=from_date,
        to_date=to_date,
        overall=overall_metrics,
        daily=daily_list,
        pct_within_500_mw=pct_within_threshold(joined, 500.0),
    )


@router.get("/accuracy/series", response_model=AccuracySeriesResponse)
def accuracy_series(
    delivery_date: date = Query(...),
) -> AccuracySeriesResponse:
    settings = get_settings()
    start = date.fromisoformat(settings.scope_start)
    end = date.fromisoformat(settings.scope_end)
    if delivery_date < start or delivery_date > end:
        raise HTTPException(status_code=400, detail="delivery_date out of scope")

    store = Store()
    store.ensure_db()
    forecasts = store.load_decision_forecasts(delivery_date)
    if forecasts.empty:
        raise HTTPException(status_code=404, detail="No data for date")
    actuals = store.load_actuals(delivery_date, delivery_date)
    joined = join_forecast_actual(forecasts, actuals)
    m = compute_metrics(joined)
    intervals = [
        IntervalPoint(
            settlement_date=r["settlement_date"],
            settlement_period=int(r["settlement_period"]),
            start_time=_clean(r["start_time"]),
            forecast_mw=_clean(r.get("forecast_mw")),
            actual_mw=_clean(r.get("actual_mw")),
            error_mw=_clean(r.get("error_mw")),
            publish_time=_clean(r.get("publish_time")),
        )
        for _, r in joined.iterrows()
    ]
    return AccuracySeriesResponse(
        delivery_date=delivery_date,
        intervals=intervals,
        mae_mw=m["mae_mw"] if m["n"] else None,
        rmse_mw=m["rmse_mw"] if m["n"] else None,
        mape_pct=m["mape_pct"] if m["n"] else None,
        bias_mw=m["bias_mw"] if m["n"] else None,
    )
