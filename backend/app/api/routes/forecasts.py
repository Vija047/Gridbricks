import math
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.models.schemas import DecisionForecastResponse, IntervalPoint
from app.services.metrics import join_forecast_actual
from app.services.normalize import decision_cutoff_utc
from app.services.store import Store

router = APIRouter(prefix="/api/v1", tags=["forecasts"])


def _clean(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "to_pydatetime"):
        return v.to_pydatetime()
    return v


def _validate_scope(delivery_date: date) -> None:
    settings = get_settings()
    start = date.fromisoformat(settings.scope_start)
    end = date.fromisoformat(settings.scope_end)
    if delivery_date < start or delivery_date > end:
        raise HTTPException(
            status_code=400,
            detail=f"delivery_date must be within {start} and {end}",
        )


@router.get("/forecasts/decision", response_model=DecisionForecastResponse)
def decision_forecast(
    delivery_date: date = Query(..., description="Settlement / delivery date (YYYY-MM-DD)"),
) -> DecisionForecastResponse:
    _validate_scope(delivery_date)
    settings = get_settings()
    store = Store()
    store.ensure_db()

    forecasts = store.load_decision_forecasts(delivery_date)
    if forecasts.empty:
        raise HTTPException(status_code=404, detail="No forecast data for this date")

    actuals = store.load_actuals(delivery_date, delivery_date)
    joined = join_forecast_actual(forecasts, actuals)

    cutoff = decision_cutoff_utc(
        delivery_date,
        settings.decision_cutoff_local_time,
        settings.decision_timezone,
    )
    publish_times = sorted(
        {
            t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            for t in forecasts["publish_time"].dropna().tolist()
        }
    )
    latest = publish_times[-1] if publish_times else None

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

    return DecisionForecastResponse(
        delivery_date=delivery_date,
        decision_cutoff=cutoff,
        cutoff_local=(
            f"{settings.decision_cutoff_local_time} {settings.decision_timezone} "
            f"on D−1 before {delivery_date.isoformat()}"
        ),
        publish_times_used=publish_times,
        latest_publish_time=latest,
        intervals=intervals,
    )
