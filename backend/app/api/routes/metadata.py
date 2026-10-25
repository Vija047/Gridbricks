from datetime import date, datetime

from fastapi import APIRouter

from app.config import get_settings
from app.models.schemas import MetaResponse
from app.services.store import Store

router = APIRouter(prefix="/api/v1", tags=["meta"])


@router.get("/meta", response_model=MetaResponse)
def get_meta() -> MetaResponse:
    settings = get_settings()
    store = Store()
    store.ensure_db()
    counts = store.coverage_counts()
    last = store.get_meta("last_sync_at")
    last_sync = datetime.fromisoformat(last.replace("Z", "+00:00")) if last else None
    return MetaResponse(
        scope_start=date.fromisoformat(settings.scope_start),
        scope_end=date.fromisoformat(settings.scope_end),
        decision_cutoff_local_time=settings.decision_cutoff_local_time,
        decision_timezone=settings.decision_timezone,
        last_sync_at=last_sync,
        actuals_days=counts["actuals_days"],
        forecast_days=counts["forecast_days"],
    )
