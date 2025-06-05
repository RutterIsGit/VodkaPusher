"""Utilities to enrich business data using Google Programmable Search API."""

import csv
import os
import time
from pathlib import Path
from typing import List, Dict, Optional

import requests

# The API key and search engine ID (cx) must be provided either via the
# function parameters or via the environment variables below. Obtain an API key
# by creating a project in the Google Developers Console and enabling the
# "Custom Search JSON API". Then create an API key and a Programmable Search
# Engine and note its "cx" identifier.
API_KEY_ENV = "GOOGLE_API_KEY"
CX_ENV = "GOOGLE_CX"

CSV_PATH = Path("essex_licensed_venues.csv")


def search_business_url(name: str, postcode: str, *, api_key: str, cx: str) -> Optional[str]:
    """Return the first website URL found for the business via Google search."""
    query = f"{name} {postcode}"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": 1,
    }
    try:
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if items:
            return items[0].get("link")
    except Exception as e:
        print(f"Google search error for {name!r} {postcode}: {e}")
    return None


def enrich_rows_with_google(rows: List[Dict[str, str]], api_key: str, cx: str) -> None:
    """Update rows in-place with website URLs using Google search."""
    for idx, row in enumerate(rows, 1):
        if not row.get("website") and row.get("name") and row.get("postcode"):
            url = search_business_url(row["name"], row["postcode"], api_key=api_key, cx=cx)
            if url:
                row["website"] = url
            if idx % 5 == 0:
                time.sleep(1)


def enrich_csv_file(path: Path = CSV_PATH, api_key: Optional[str] = None, cx: Optional[str] = None) -> None:
    """Load `path`, fill missing websites, and overwrite the file."""
    api_key = api_key or os.getenv(API_KEY_ENV)
    cx = cx or os.getenv(CX_ENV)
    if not api_key or not cx:
        raise RuntimeError(
            "Google API credentials missing. Provide api_key and cx or set the "
            f"{API_KEY_ENV} and {CX_ENV} environment variables." )

    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    enrich_rows_with_google(rows, api_key, cx)

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    try:
        enrich_csv_file()
    except RuntimeError as exc:
        print(exc)
