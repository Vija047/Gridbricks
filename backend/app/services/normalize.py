"""Timestamp and settlement-period helpers."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo


def parse_iso(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        text = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def settlement_period_for_start(start: datetime) -> int:
    """Map UTC startTime on a settlement day to SP 1-48 (GB market day).

    Settlement day runs 00:00–23:30 Europe/London. We derive SP from the
    settlementDate field when available; otherwise from London local time.
    """
    london = start.astimezone(ZoneInfo("Europe/London"))
    minutes = london.hour * 60 + london.minute
    return minutes // 30 + 1


def start_times_for_settlement_date(settlement_date: date) -> list[datetime]:
    """Return 48 half-hourly startTimes (UTC) for a GB settlement date."""
    tz = ZoneInfo("Europe/London")
    local_midnight = datetime(
        settlement_date.year,
        settlement_date.month,
        settlement_date.day,
        0,
        0,
        tzinfo=tz,
    )
    return [
        (local_midnight + timedelta(minutes=30 * i)).astimezone(timezone.utc)
        for i in range(48)
    ]


def decision_cutoff_utc(
    delivery_date: date,
    cutoff_local_time: str,
    timezone_name: str,
) -> datetime:
    """Cutoff is cutoff_local_time on D-1 in the given timezone, returned as UTC."""
    hour, minute = (int(x) for x in cutoff_local_time.split(":"))
    tz = ZoneInfo(timezone_name)
    d_minus_1 = delivery_date - timedelta(days=1)
    local = datetime(
        d_minus_1.year, d_minus_1.month, d_minus_1.day, hour, minute, tzinfo=tz
    )
    return local.astimezone(timezone.utc)


def expand_hourly_to_half_hours(
    start_utc: datetime, generation_mw: float
) -> list[tuple[datetime, float]]:
    """If start is on the hour, emit both :00 and :30 half-hours with same MW."""
    if start_utc.minute == 0 and start_utc.second == 0:
        return [
            (start_utc, generation_mw),
            (start_utc + timedelta(minutes=30), generation_mw),
        ]
    return [(start_utc, generation_mw)]


def settlement_date_from_start(start: datetime) -> date:
    return start.astimezone(ZoneInfo("Europe/London")).date()
