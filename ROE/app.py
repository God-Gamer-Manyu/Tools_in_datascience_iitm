from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import csv
import json
from typing import Optional
from datetime import datetime, timezone

app = FastAPI(title="Sensor Stats API")

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_PATH = Path(__file__).parent / "q-fastapi-timeseries-cache.csv"

# Simple in-memory cache: key -> result dict
_cache = {}

def _make_key(location: Optional[str], sensor: Optional[str], start_date: Optional[str], end_date: Optional[str]) -> str:
    # deterministic key for query parameters
    return json.dumps({
        "location": location or "",
        "sensor": sensor or "",
        "start_date": start_date or "",
        "end_date": end_date or "",
    }, sort_keys=True)

def _parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip()
    # try ISO first
    try:
        dt = datetime.fromisoformat(s)
        # normalize: if datetime has tzinfo, convert to UTC and return as naive
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        pass
    # try common formats
    fmts = ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S")
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            # parsed formats are naive; return as-is
            return dt
        except Exception:
            continue
    # if we couldn't parse, raise ValueError for clear feedback
    raise ValueError(f"Unsupported date format: {s}")

def _compute_stats_from_csv(location: Optional[str], sensor: Optional[str], start_date: Optional[str], end_date: Optional[str]):
    key = _make_key(location, sensor, start_date, end_date)
    # return cached result if present
    if key in _cache:
        return _cache[key], True

    sd = None
    ed = None
    try:
        sd = _parse_date(start_date) if start_date else None
        ed = _parse_date(end_date) if end_date else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not CSV_PATH.exists():
        raise HTTPException(status_code=500, detail=f"CSV file not found: {CSV_PATH}")

    count = 0
    ssum = 0.0
    minv = None
    maxv = None

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # read timestamp field - be a bit flexible about column name
            ts_raw = row.get("timestamp") or row.get("time") or row.get("datetime")
            if not ts_raw:
                continue
            try:
                ts = _parse_date(ts_raw)
            except Exception:
                # skip rows with unparsable timestamps
                continue

            if ts is None:
                continue

            if location and row.get("location") != location:
                continue
            if sensor and row.get("sensor") != sensor:
                continue
            if sd is not None and ts < sd:
                continue
            if ed is not None and ts > ed:
                continue

            val_raw = row.get("value")
            if val_raw is None or val_raw == "":
                continue
            try:
                val = float(val_raw)
            except Exception:
                continue

            count += 1
            ssum += val
            if minv is None or val < minv:
                minv = val
            if maxv is None or val > maxv:
                maxv = val

    avg = (ssum / count) if count else None

    result = {"stats": {"count": count, "avg": avg, "min": minv, "max": maxv}}
    # store in cache
    _cache[key] = result
    return result, False


@app.get("/stats")
def stats(
    location: Optional[str] = Query(None),
    sensor: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """Return simple stats (count, avg, min, max) filtered by optional query params.

    All parameters are optional. Dates may be ISO-like (e.g. 2023-05-01 or 2023-05-01T12:00:00).
    """
    result, cached = _compute_stats_from_csv(location, sensor, start_date, end_date)
    headers = {"X-Cache": "HIT" if cached else "MISS"}
    return JSONResponse(content=result, headers=headers)


if __name__ == "__main__":
    import uvicorn

    # Run with: python ROE/app.py
    # We disable `reload` here because the reload mechanism requires the
    # application to be importable by module path (e.g. "ROE.app:app") from
    # the monitor subprocess — which can fail in some environments and cause
    # a ModuleNotFoundError. To develop with auto-reload, run uvicorn from the
    # command line (see README) instead.
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
