from datetime import datetime, timedelta, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(fmt)


def time_ago(dt: datetime) -> str:
    now = utc_now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago"
    else:
        days = seconds // 86400
        return f"{days}d ago"


def add_minutes(dt: datetime, minutes: int) -> datetime:
    return dt + timedelta(minutes=minutes)


def add_hours(dt: datetime, hours: int) -> datetime:
    return dt + timedelta(hours=hours)


def start_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def is_within_last_hours(dt: datetime, hours: int) -> bool:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    cutoff = utc_now() - timedelta(hours=hours)
    return dt >= cutoff