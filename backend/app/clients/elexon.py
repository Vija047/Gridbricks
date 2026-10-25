"""HTTP client for Elexon Insights BMRS stream datasets."""

from __future__ import annotations

import logging
import time
from datetime import date, datetime, timedelta
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class ElexonClient:
    def __init__(self, base_url: str, timeout: float = 120.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def _get(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        url = f"{self.base_url}{path}"
        params = {**params, "format": "json"}
        last_err: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.get(url, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    if isinstance(data, list):
                        return data
                    if isinstance(data, dict) and "data" in data:
                        return data["data"]
                    return []
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                logger.warning(
                    "Elexon request failed (attempt %s/%s): %s %s — %s",
                    attempt,
                    self.max_retries,
                    path,
                    params,
                    exc,
                )
                time.sleep(min(2**attempt, 8))
        raise RuntimeError(f"Elexon fetch failed after retries: {last_err}")

    def fetch_fuelhh_wind(self, date_from: date, date_to: date) -> list[dict[str, Any]]:
        return self._get(
            "/datasets/FUELHH/stream",
            {
                "fuelType": "WIND",
                "settlementDateFrom": date_from.isoformat(),
                "settlementDateTo": date_to.isoformat(),
            },
        )

    def fetch_windfor(
        self,
        date_from: date,
        date_to: date,
        publish_from: Optional[datetime] = None,
        publish_to: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "settlementDateFrom": date_from.isoformat(),
            "settlementDateTo": date_to.isoformat(),
        }
        if publish_from is not None:
            params["publishDateTimeFrom"] = publish_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        if publish_to is not None:
            params["publishDateTimeTo"] = publish_to.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self._get("/datasets/WINDFOR/stream", params)

    def fetch_windfor_by_publish(
        self, publish_from: datetime, publish_to: datetime
    ) -> list[dict[str, Any]]:
        """Query WINDFOR by publish window only (most reliable filter)."""
        return self._get(
            "/datasets/WINDFOR/stream",
            {
                "publishDateTimeFrom": publish_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "publishDateTimeTo": publish_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )

    def iter_date_chunks(
        self, start: date, end: date, chunk_days: int = 3
    ) -> list[tuple[date, date]]:
        chunks: list[tuple[date, date]] = []
        cur = start
        while cur <= end:
            chunk_end = min(cur + timedelta(days=chunk_days - 1), end)
            chunks.append((cur, chunk_end))
            cur = chunk_end + timedelta(days=1)
        return chunks
