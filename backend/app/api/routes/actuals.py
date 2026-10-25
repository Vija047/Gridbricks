from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.models.schemas import ActualPoint, ActualsResponse
from app.services.store import Store

router = APIRouter(prefix="/api/v1", tags=["actuals"])


@router.get("/actuals", response_model=ActualsResponse)
def get_actuals(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
) -> ActualsResponse:
    settings = get_settings()
    scope_start = date.fromisoformat(settings.scope_start)
    scope_end = date.fromisoformat(settings.scope_end)
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from must be <= to")
    if from_date < scope_start or to_date > scope_end:
        raise HTTPException(
            status_code=400,
            detail=f"Dates must be within {scope_start} and {scope_end}",
        )

    store = Store()
    store.ensure_db()
    df = store.load_actuals(from_date, to_date)
    points = [
        ActualPoint(
            settlement_date=row.settlement_date,
            settlement_period=int(row.settlement_period),
            start_time=row.start_time.to_pydatetime()
            if hasattr(row.start_time, "to_pydatetime")
            else row.start_time,
            generation_mw=float(row.generation_mw),
        )
        for row in df.itertuples(index=False)
    ]
    return ActualsResponse(from_date=from_date, to_date=to_date, points=points)
