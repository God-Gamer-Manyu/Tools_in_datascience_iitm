"""
IMDb scraper (clean) — extract up to 25 titles with rating 4.0–6.0

This script targets the modern IMDb markup (summary items inside
`ul.ipc-metadata-list`) and falls back to the legacy `.lister-item.mode-advanced`
layout when necessary.

Output: writes `q2.json` containing an array of objects with fields: id, title, year, rating

Usage:
    python scraping_imdb_with_javascript.py

Note: Install dependencies first:
    python -m pip install requests beautifulsoup4
"""
from __future__ import annotations

import json
import re
import sys
import time
from typing import List

import requests
from bs4 import BeautifulSoup


SEARCH_URL = (
    "https://www.imdb.com/search/title/?title_type=feature,tv_movie&"
    "user_rating=4,6&count=50"
)


def fetch_url(url: str, retries: int = 3, backoff: float = 1.0) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            last_err = e
            time.sleep(backoff * (2 ** attempt))
    if last_err:
        raise last_err
    raise RuntimeError("Failed to fetch URL and no exception recorded")


def parse_search_page(html: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results: List[dict] = []

    # Modern layout: summary items inside ul.ipc-metadata-list
    container = soup.select_one("ul.ipc-metadata-list")
    if container:
        entries = container.select("li.ipc-metadata-list-summary-item") or container.select("li")
        for entry in entries:
            # prefer the modern title link wrapper when present
            link = entry.select_one("a.ipc-title-link-wrapper")
            if link:
                # scope subsequent selects to the wrapper's parent so later queries find the expected nodes
                entry = link.parent.parent
            if not entry:
                continue
            a = entry.select_one("a[href*='/title/tt']")
            if not a:
                continue
            href = str(a.get("href", ""))
            m = re.search(r"/title/(tt\d+)/", href)
            if not m:
                continue
            imdb_id = m.group(1)
            # title
            title_tag = a.select_one("h3.ipc-title__text") or a.select_one("h3")
            title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
            # title = title.partition(' ')[2]

            print(f"DEBUG: processing entry for title '{title}'")

            # rating (several modern variants)
            rating_tag = (
                entry.select_one("span.ipc-rating-star--rating")
                or entry.select_one("span.ipc-inline-rating__rating")
                or entry.select_one("span.ratings-imdb-rating")
            )
            rating_text = rating_tag.get_text(strip=True) if rating_tag else ""
            print(f"DEBUG: found rating '{rating_text}'")

            # year: search for first 4-digit year inside entry text
            txt = entry.get_text(separator=" ", strip=True)
            ymatch = re.search(r"(19\d{2}|20\d{2})", txt)
            year = ymatch.group(1) if ymatch else ""

            print(f"DEBUG: found year '{year}'")

            try:
                rating_val = float(rating_text) if rating_text else None
            except Exception:
                rating_val = None

            if rating_val is None:
                continue
            if not (4.0 <= rating_val <= 6.0):
                continue

            results.append({"id": imdb_id, "title": title, "year": year, "rating": f"{rating_val:.1f}"})
            if len(results) >= 25:
                break

        if results:
            return results

    # Fallback to legacy layout
    items = soup.select(".lister-item.mode-advanced")
    for it in items:
        header = it.select_one("h3.lister-item-header a")
        if not header:
            continue
        href = str(header.get("href", ""))
        m = re.search(r"/title/(tt\d+)/", href)
        if not m:
            continue
        imdb_id = m.group(1)
        title = header.get_text(strip=True)

        year_tag = it.select_one("h3.lister-item-header .lister-item-year")
        year_text = year_tag.get_text(strip=True) if year_tag else ""
        year_match = re.search(r"(19\d{2}|20\d{2})", year_text)
        year = year_match.group(1) if year_match else ""

        rating_tag = it.select_one(".ratings-imdb-rating strong")
        rating_text = rating_tag.get_text(strip=True) if rating_tag else ""

        try:
            rating_val = float(rating_text) if rating_text else None
        except Exception:
            rating_val = None

        if rating_val is None:
            continue
        if not (4.0 <= rating_val <= 6.0):
            continue

        results.append({"id": imdb_id, "title": title, "year": year, "rating": f"{rating_val:.1f}"})
        if len(results) >= 25:
            break

    return results


def main() -> int:
    print("Fetching IMDb advanced search page (ratings 4.0 - 6.0)")
    try:
        html = fetch_url(SEARCH_URL)
    except Exception as e:
        print(f"Failed to fetch search page: {e}")
        return 2

    print("Parsing page and extracting titles...")
    try:
        items = parse_search_page(html)
    except Exception as e:
        print(f"Failed to parse page: {e}")
        return 3

    out_path = "week 5/q2.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(items)} items to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
