"""Utilities to enrich business data using Google Programmable Search API."""

import csv
import os
import time
from pathlib import Path
from typing import List, Dict, Optional

import requests
from dotenv import load_dotenv

from config.filters import should_exclude_business_name, get_filter_reason
from utils.filtering import FilterStatistics

# Load environment variables from .env file
load_dotenv()

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




def enrich_rows_with_google(rows: List[Dict[str, str]], api_key: str, cx: str, max_requests: int = 1000, delay_seconds: float = 0.5, filter_stats: FilterStatistics = None) -> None:
    """Update rows in-place with website URLs using Google search.
    
    Args:
        rows: List of dictionaries containing business data
        api_key: Google API key
        cx: Google Custom Search Engine ID
        max_requests: Maximum number of API requests to make (default: 1000)
        delay_seconds: Delay between requests in seconds (default: 0.5)
        filter_stats: FilterStatistics object for tracking filters (optional)
    """
    requests_made = 0
    
    # Apply business name filters at the start
    rows_needing_enrichment = []
    for idx, row in enumerate(rows):
        if not row.get("website") and row.get("name") and row.get("postcode"):
            if should_exclude_business_name(row.get("name", "")):
                if filter_stats:
                    filter_stats.log_filter(
                        row.get("name", ""),
                        get_filter_reason(name=row.get("name", "")),
                        'business_name'
                    )
            else:
                rows_needing_enrichment.append((idx, row))
    
    total_to_enrich = len(rows_needing_enrichment)
    print(f"Found {total_to_enrich} rows needing website enrichment after filtering")
    
    if total_to_enrich > max_requests:
        print(f"WARNING: Only processing first {max_requests} rows to avoid excessive API usage")
        rows_needing_enrichment = rows_needing_enrichment[:max_requests]
    
    for i, (idx, row) in enumerate(rows_needing_enrichment):
        print(f"Processing {i+1}/{min(total_to_enrich, max_requests)}: {row['name']} ({row['postcode']})")
        
        url = search_business_url(row["name"], row["postcode"], api_key=api_key, cx=cx)
        if url:
            row["website"] = url
            print(f"  Found: {url}")
        else:
            print(f"  No website found")
        
        requests_made += 1
        
        # Rate limiting - Google Custom Search API allows 100 queries per day for free tier
        # Adding delay to be respectful and avoid hitting rate limits
        time.sleep(delay_seconds)


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
        api_key = os.getenv(API_KEY_ENV)
        cx = os.getenv(CX_ENV)
        
        # Debug output
        print(f"API Key loaded: {'Yes' if api_key else 'No'}")
        print(f"CX (Search Engine ID) loaded: {'Yes' if cx else 'No'}")
        
        if not api_key:
            print(f"\nError: {API_KEY_ENV} not found in environment variables.")
            print("Please add it to your .env file as: GOOGLE_API_KEY=your_api_key_here")
        
        if not cx:
            print(f"\nError: {CX_ENV} not found in environment variables.")
            print("Please add it to your .env file as: GOOGLE_CX=your_search_engine_id_here")
            print("You can find your Search Engine ID at: https://programmablesearchengine.google.com/")
        
        if not api_key or not cx:
            raise RuntimeError(
                "Google API credentials missing. Please check the messages above."
            )
        
        # Initialize filter statistics
        filter_stats = FilterStatistics()
        
        # Load the original CSV
        path = CSV_PATH
        print(f"Loading data from {path}")
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        print(f"Loaded {len(rows)} total rows")
        
        # Count existing websites
        existing_websites = sum(1 for row in rows if row.get("website"))
        print(f"Rows with existing websites: {existing_websites}")
        
        # Enrich rows with Google search
        # Set max_requests to prevent excessive API usage
        # Google Custom Search API free tier allows 100 queries per day
        # Setting a reasonable limit with ability to override via environment variable
        max_requests = int(os.getenv("GOOGLE_MAX_REQUESTS", "2500"))
        delay_seconds = float(os.getenv("GOOGLE_DELAY_SECONDS", "0.5"))
        
        print(f"\nStarting enrichment (max requests: {max_requests}, delay: {delay_seconds}s)")
        enrich_rows_with_google(rows, api_key, cx, max_requests=max_requests, delay_seconds=delay_seconds, filter_stats=filter_stats)
        
        # Save to new file (no additional filtering needed as it's done upfront)
        output_path = Path("essex_venues_google.csv")
        print(f"\nSaving enriched data to {output_path}")
        with output_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        
        # Print filter statistics
        print("\n" + filter_stats.get_summary())
        
        # Save filter log
        filter_stats.save_log("google_enricher_filter_log.csv")
        print(f"\nFilter log saved to: google_enricher_filter_log.csv")
        
        # Final statistics
        final_websites = sum(1 for row in rows if row.get("website"))
        print(f"\nEnrichment complete!")
        print(f"Total rows: {len(rows)}")
        print(f"Final rows with websites: {final_websites}")
        
    except Exception as exc:
        print(f"Error: {exc}")
