# Sensor Stats FastAPI Service

Files added:

- `app.py` - FastAPI application exposing `GET /stats` for computing count/avg/min/max from `q-fastapi-timeseries-cache.csv`.
- `requirements.txt` - dependencies (fastapi, uvicorn).

Usage

1. Install deps (recommended in a virtualenv):

   python -m pip install -r ROE/requirements.txt

2. Run the service:

    - Run directly (recommended for simple runs). This starts the server without auto-reload:

          python ROE/app.py

    - For development with auto-reload use uvicorn from the command-line and make sure the `ROE` package is on Python's import path. Example (run from the repository root):

          python -m uvicorn ROE.app:app --reload --port 8000

       If uvicorn can't import `ROE` you can provide the application directory explicitly:

          python -m uvicorn ROE.app:app --reload --app-dir "d:/Rtamanyu/_IIt Madras/2nd year/sem 1/Tools in datascience" --port 8000

       Note: starting the script with `python ROE/app.py` and enabling `reload=True` inside the script can cause a ModuleNotFoundError in the reloader subprocess. The direct-run approach in this repository disables reload by default to avoid that issue.

Endpoint

GET /stats

Query parameters (all optional):
- `location` - filter by location (exact match)
- `sensor` - filter by sensor (exact match)
- `start_date` - include rows with timestamp >= this value (ISO-like)
- `end_date` - include rows with timestamp <= this value (ISO-like)

Response JSON:

```
{
  "stats": { "count": <int>, "avg": <float|null>, "min": <float|null>, "max": <float|null> }
}
```

Headers:
- `X-Cache`: `HIT` when the same query result was served from in-memory cache, `MISS` when freshly computed.

Notes
- The implementation uses a simple in-memory dictionary cache; restarting the server clears the cache.
- If no rows match the filters, `count` is `0` and `avg`, `min`, `max` are `null`.
- Dates accept ISO-like strings (e.g. `2023-05-01` or `2023-05-01T12:00:00`).
