"""Search GitHub for users in Hyderabad with >80 followers and print newest account creation date.

Behavior:
- Uses GitHub Search API: /search/users?q=location:Hyderabad+followers:>80&sort=joined&order=desc
- Fetches user profile(s) and checks created_at against cutoff (ignore users created after cutoff)
- Prints the created_at (ISO 8601) of the newest user satisfying the cutoff.

Provide a GITHUB_TOKEN via environment variable to increase rate limits (optional).
"""
from __future__ import annotations

import os
import sys
import time
from typing import Optional

import requests
from datetime import datetime, timezone


GITHUB_API = "https://api.github.com"
SEARCH_ENDPOINT = GITHUB_API + "/search/users"

# Cutoff: ignore users created after this timestamp (inclusive: we accept <= cutoff)
CUTOFF_ISO = "2025-10-20T09:43:05Z"
CUTOFF_DT = datetime.strptime(CUTOFF_ISO, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def iso_to_dt(iso: str) -> datetime:
    # GitHub returns times like '2024-01-01T00:00:00Z' (UTC)
    try:
        return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        # try to parse fractional seconds
        try:
            # remove Z then parse
            if iso.endswith("Z"):
                iso2 = iso[:-1]
                return datetime.fromisoformat(iso2).replace(tzinfo=timezone.utc)
        except Exception:
            pass
    raise ValueError(f"Unrecognized ISO format: {iso}")


def get_headers() -> dict:
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "github-new-user-script/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def find_newest_user_created_at(location: str = "Hyderabad", min_followers: int = 80, max_pages: int = 10, per_page: int = 30) -> Optional[str]:
    # Build search query
    q = f"location:{location} followers:>{min_followers}"
    headers = get_headers()

    for page in range(1, max_pages + 1):
        params = {"q": q, "sort": "joined", "order": "desc", "per_page": per_page, "page": page}
        resp = requests.get(SEARCH_ENDPOINT, params=params, headers=headers, timeout=15)
        if resp.status_code == 403:
            # rate limit or forbidden; wait a bit and retry once
            time.sleep(1)
            resp = requests.get(SEARCH_ENDPOINT, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items") or []
        if not items:
            break

        # Items are ordered by joined desc (newest first). Iterate and inspect created_at from profile.
        for it in items:
            user_url = it.get("url")
            if not user_url:
                continue
            # fetch profile
            p = requests.get(user_url, headers=headers, timeout=15)
            if p.status_code == 403:
                time.sleep(1)
                p = requests.get(user_url, headers=headers, timeout=15)
            p.raise_for_status()
            profile = p.json()
            created_at = profile.get("created_at")
            if not created_at:
                continue
            try:
                dt = iso_to_dt(created_at)
            except Exception:
                continue
            # ignore if created after cutoff
            if dt <= CUTOFF_DT:
                # print as ISO 8601 (GitHub format already fits)
                return created_at
            # otherwise skip this ultra-new user and continue

    return None


def main() -> int:
    result = find_newest_user_created_at()
    if result:
        # print only the ISO date
        print(result)
        return 0
    # nothing found
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
