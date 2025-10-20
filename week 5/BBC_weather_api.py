"""
Fetch BBC Weather forecast for a city (Yerevan by default) and save a mapping
of localDate -> enhancedWeatherDescription as q5.json

This script expects the following environment variables (or will use defaults):
- BBC_API_KEY: your API key (if required). If not provided, script will still try public endpoints.
- LOCATOR_URL: locator service base URL (defaults to the public locator used in examples)
- BROKER_URL: weather broker base URL

Usage:
    python BBC_weather_api.py --city Yerevan

Output: writes `q5.json` in the current folder.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from typing import Dict, Any
from bs4 import BeautifulSoup
import dotenv

import pandas as pd
import requests

dotenv.load_dotenv()

BBC_API_KEY = os.getenv("BBC_API_KEY")
# DEFAULT_LOCATOR = "https://weather.api.bbci.co.uk/locations/v1/locations"
DEFAULT_LOCATOR = "https://locator-service.api.bbci.co.uk/locations"
DEFAULT_BROKER = "https://www.bbc.com/weather"


def find_location_id(city: str, locator_url: str, api_key: str | None = None) -> str:
    params = {"stack": "aws", "locale": "en", "filter": "international", "place-types": "settlement,airport,district", "order": "importance", "s": city, "a": "true", "format": "json"}
    headers = {"User-Agent": "python-requests/1.0"}
    if api_key:
        params["api_key"] = api_key
    resp = requests.get(locator_url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data['response']['results']['results'][0]['id']


def fetch_forecast(location_id: str, broker_url: str, api_key: str | None = None) -> BeautifulSoup:
    headers = {"User-Agent": "python-requests/1.0"}
    url = f"{broker_url}/{location_id}"
    print(f"Fetching forecast from URL: {url}")
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, 'html.parser')


def extract_date_description_map(forecast_soup: BeautifulSoup) -> Dict[str, str]:
    out: Dict[str, str] = {}
    daily_summary = forecast_soup.find('div', attrs={'class': 'wr-day-summary'})
    daily_summary_list = re.findall('[a-zA-Z][^A-Z]*', daily_summary.text) # type: ignore #split the string on uppercase
    datelist = pd.date_range(datetime.datetime.today(), periods=len(daily_summary_list)).tolist()
    datelist = [datelist[i].date().strftime('%Y-%m-%d') for i in range(len(datelist))]
    for ind, i in enumerate(datelist):
        out[i] = daily_summary_list[ind]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch BBC Weather forecast for a city and save q5.json")
    parser.add_argument("--city", default="Yerevan", help="City name to search (default: Yerevan)")
    args = parser.parse_args(argv)

    api_key = os.environ.get("BBC_API_KEY", BBC_API_KEY)
    locator = os.environ.get("LOCATOR_URL", DEFAULT_LOCATOR)
    broker = os.environ.get("BROKER_URL", DEFAULT_BROKER)

    try:
        location_id = find_location_id(args.city, locator, api_key)
        print(f"Found location id: {location_id}")
    except Exception as e:
        print(f"Failed to find location id: {e}")
        return 2

    try:
        forecast = fetch_forecast(location_id, broker, api_key)
    except Exception as e:
        print(f"Failed to fetch forecast: {e}")
        return 3

    try:
        mapping = extract_date_description_map(forecast)
    except Exception as e:
        print(f"Failed to extract mapping: {e}")
        return 4

    out_path = "week 5/q5.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(mapping)} entries to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
