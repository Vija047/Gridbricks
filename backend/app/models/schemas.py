from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class MetaResponse(BaseModel):
    scope_start: date
    scope_end: date
    decision_cutoff_local_time: str
    decision_timezone: str
    last_sync_at: Optional[datetime] = None
    actuals_days: int = 0
    forecast_days: int = 0
    resolution_note: str = (
        "FUELHH is half-hourly. WINDFOR may be hourly; hourly MW is assigned "
        "to both settlement periods in that hour when a 30-min point is missing."
    )


class IntervalPoint(BaseModel):
    settlement_date: date
    settlement_period: int = Field(ge=1, le=48)
    start_time: datetime
    forecast_mw: Optional[float] = None
    actual_mw: Optional[float] = None
    error_mw: Optional[float] = None
    publish_time: Optional[datetime] = None


class DecisionForecastResponse(BaseModel):
    delivery_date: date
    decision_cutoff: datetime
    cutoff_local: str
    publish_times_used: list[datetime] = []
    latest_publish_time: Optional[datetime] = None
    intervals: list[IntervalPoint]


class ActualPoint(BaseModel):
    settlement_date: date
    settlement_period: int
    start_time: datetime
    generation_mw: float


class ActualsResponse(BaseModel):
    from_date: date
    to_date: date
    points: list[ActualPoint]


class DailyMetrics(BaseModel):
    settlement_date: date
    mae_mw: float
    rmse_mw: float
    mape_pct: float
    bias_mw: float
    n: int
    mean_actual_mw: float
    mean_forecast_mw: float


class AccuracySummaryResponse(BaseModel):
    from_date: date
    to_date: date
    overall: DailyMetrics
    daily: list[DailyMetrics]
    pct_within_500_mw: Optional[float] = None


class AccuracySeriesResponse(BaseModel):
    delivery_date: date
    intervals: list[IntervalPoint]
    mae_mw: Optional[float] = None
    rmse_mw: Optional[float] = None
    mape_pct: Optional[float] = None
    bias_mw: Optional[float] = None
