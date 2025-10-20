"""Country Wikipedia Outline API

Runs a FastAPI app with endpoint /api/outline?country=<name>
It fetches the Wikipedia page for the given country, extracts H1-H6 headings
and returns a Markdown outline.

Example response (text/markdown):

## Contents

# Vanuatu

## Etymology

## History

### Prehistory
...

Run with:
    cd "week 5" 
    uvicorn country_wikipedia_api:app --host 127.0.0.1 --port 8000

"""
from __future__ import annotations

import html
import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Country Wikipedia Outline API")

# Allow GET from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


WIKIPEDIA_BASE = "https://en.wikipedia.org/wiki/"


def find_wikipedia_url(country: str) -> str:
    # Basic safe slug: replace spaces with underscores and strip
    slug = country.strip().replace(" ", "_")
    return WIKIPEDIA_BASE + slug


def extract_headings(html_text: str) -> List[tuple[int, str]]:
    """Parse HTML and return a list of (level, text) for each heading in order."""
    soup = BeautifulSoup(html_text, "html.parser")
    # Wikipedia content is inside #mw-content-text; search within it if present
    content = soup.select_one("#mw-content-text") or soup
    headings: List[tuple[int, str]] = []
    for tag in content.find_all(re.compile(r"^h[1-6]$")):
        # tag.name should be like 'h2' — guard in case parser returns atypical nodes
        tag_name = getattr(tag, "name", None)
        if not tag_name or len(tag_name) < 2 or not tag_name[1].isdigit():
            continue
        level = int(tag_name[1])
        # get visible text
        text = tag.get_text(" ", strip=True)
        # unescape HTML entities
        text = html.unescape(text)
        if text:
            headings.append((level, text))
    return headings


def headings_to_markdown(title: Optional[str], headings: List[tuple[int, str]]) -> str:
    lines: List[str] = ["## Contents", ""]
    if title:
        lines.append(f"# {title}")
        lines.append("")
    for level, text in headings:
        # Map heading level to number of leading # (H1 -> #, H2 -> ##, etc.)
        hashes = "#" * level
        lines.append(f"{hashes} {text}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


@app.get("/api/outline", response_class=Response, responses={200: {"content": {"text/markdown": {}}}})
def outline(country: str = Query(..., description="Country name or Wikipedia slug")):
    """Return a Markdown outline of the Wikipedia page headings for `country`."""
    url = find_wikipedia_url(country)
    try:
        resp = requests.get(url, headers={"User-Agent": "python-requests/2.x"}, timeout=10)
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Wikipedia returned an error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Wikipedia page: {e}")

    headings = extract_headings(resp.text)
    md = headings_to_markdown(country, headings)
    return Response(content=md, media_type="text/markdown")
