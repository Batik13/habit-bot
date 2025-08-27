from __future__ import annotations
import datetime as dt

def today_ymd(tz: dt.tzinfo | None = None) -> str:
    tz = tz or dt.timezone.utc
    return dt.datetime.now(tz).date().isoformat()

def now_iso_utc() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()