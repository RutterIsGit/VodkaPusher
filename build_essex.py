import os, zipfile, io, requests, csv, time
from pathlib import Path
from difflib import SequenceMatcher
from bs4 import BeautifulSoup   # pip install beautifulsoup4 lxml
from config.filters import should_exclude_business_name
from utils.filtering import FilterStatistics

OUT = Path("essex_licensed_venues.csv")
cols = ["name","business_type","website","lat","lon",
        "address_line1","address_line2","postcode"]

# Chains that typically do not sell alcohol and should be excluded
EXCLUDED_CHAINS = [
    "McDonald's",
    "Subway",
    "KFC",
    "Burger King",
    "Starbucks",
    "Costa",
    "Greggs",
    "Pret A Manger",
    "Domino",
    "Pizza Hut",
]


def _normalise(text: str) -> str:
    """Lower-case alphanumeric characters only for fuzzy matching."""
    return "".join(c for c in text.lower() if c.isalnum())


def is_excluded_chain(name: str, threshold: float = 0.8) -> bool:
    """Return True if the name resembles a known non-alcohol chain."""
    n = _normalise(name)
    for chain in EXCLUDED_CHAINS:
        c = _normalise(chain)
        if c in n:
            return True
        if SequenceMatcher(None, n, c).ratio() >= threshold:
            return True
    return False

def parse_fhrs(xml_bytes):
    root = BeautifulSoup(xml_bytes, "xml")
    for est in root.find_all("EstablishmentDetail"):
        bt = est.BusinessType.string if est.BusinessType else None
        if bt not in ("Restaurant/Cafe/Canteen","Pub/bar/nightclub"):
            continue
        website_tag = est.find("BusinessWebsite")
        addr_parts = []
        if est.AddressLine2 and est.AddressLine2.string:
            addr_parts.append(est.AddressLine2.string)
        if est.AddressLine3 and est.AddressLine3.string:
            addr_parts.append(est.AddressLine3.string)
        if est.AddressLine4 and est.AddressLine4.string:
            addr_parts.append(est.AddressLine4.string)
        yield {
            "name": est.BusinessName.string if est.BusinessName else "",
            "business_type": bt.split("/")[0].title() if bt else "",
            "website": website_tag.get_text("").strip() if website_tag else "",
            "lat": est.Latitude.string if est.Latitude else "",
            "lon": est.Longitude.string if est.Longitude else "",
            "address_line1": est.AddressLine1.string if est.AddressLine1 else "",
            "address_line2": ", ".join(addr_parts),
            "postcode": est.PostCode.string if est.PostCode else "",
        }

def fetch(url):
    print("↳ Fetching:", url.split("/")[-1])
    try:
        response = requests.get(url, timeout=90)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return b""

def find_osm_website(name, postcode, cache=None, offline_data=None):
    """Lookup a business website in OSM via Overpass using name and postcode."""
    # First check cache
    if cache:
        cached_website = cache.get_website(name, postcode)
        if cached_website is not None:
            return cached_website
    
    # Try online query
    try:
        from osm_helper import OSMHelper
        helper = OSMHelper(timeout=10)  # Shorter timeout since we have fallbacks
        website = helper.find_website(name, postcode)
        
        # Cache the result (even if None)
        if cache:
            cache.set_website(name, postcode, website)
        
        return website
    except (ImportError, Exception) as e:
        # If online fails, try offline data
        if offline_data:
            website = offline_data.find_website(name, postcode)
            if website and cache:
                cache.set_website(name, postcode, website)
            return website
    
    # Final fallback to original implementation
    try:
        # Fallback to original implementation if helper not available
        def esc(v: str) -> str:
            return v.replace('"', '\\"')

        query = f"""
        [out:json][timeout:25];
        (
          nwr["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["website"];
          nwr["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["contact:website"];
        );
        out center;
        """

        resp = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query},
            timeout=30,  # Changed timeout to 30 seconds
        )
        resp.raise_for_status()
        data = resp.json()
<<<<<<< HEAD
    except requests.exceptions.Timeout:
        print(f"Overpass request timed out for {name!r} {postcode}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Overpass request error for {name!r} {postcode}: {e}")
        return None

    for el in data.get("elements", []):
        tags = el.get("tags", {})
        if "contact:website" in tags: # Prioritize contact:website
            return tags["contact:website"]
        if "website" in tags:
            return tags["website"]
        return None
    except Exception as e:
        print(f"Overpass error for {name!r} {postcode}: {e}")
        return None

def main(skip_osm=False):
    """
    Main function to build Essex venue list.
    
    Args:
        skip_osm: If True, skip OSM enrichment entirely (useful when OSM is down)
    """
    rows = []
    filter_stats = FilterStatistics()
    
    # Check for environment variable to skip OSM
    if os.getenv("SKIP_OSM", "").lower() in ("true", "1", "yes"):
        skip_osm = True
        print("SKIP_OSM environment variable set - skipping OSM enrichment")
    for la_id in (109,110,113,117,119,121,125,128,134,143,148,152,196,199):
        print(f"Processing LA ID: {la_id}")
        xml_content = fetch(
            f"https://ratings.food.gov.uk/OpenDataFiles/FHRS{la_id}en-GB.xml")
        if xml_content:
            rows.extend(parse_fhrs(xml_content))
        else:
            print(f"Skipping LA ID {la_id} due to fetch error.")

    # Optional: bring in the Open-Pubs CSV and append pubs we don't already have
    print("Downloading Open-Pubs CSV...")
    opubs = requests.get(
        "https://www.getthedata.com/downloads/open_pubs.csv.zip",
        timeout=90)
    if opubs.status_code != 200:
        print(f"Error downloading Open-Pubs CSV: {opubs.status_code}")
        opubs_content = None
    else:
        opubs_content = opubs.content
    if opubs_content:
        with zipfile.ZipFile(io.BytesIO(opubs_content)) as z:
            with z.open(z.namelist()[0]) as f:
                fieldnames = [
                    "fsa_id", "name", "address", "postcode", "easting", "northing",
                    "latitude", "longitude", "local_authority"
                ]
                rdr = csv.DictReader(io.TextIOWrapper(f), fieldnames=fieldnames)
                # Skip the first row (header row inside the data file)
                next(rdr)
                print("Open Pubs CSV fields:", fieldnames)
                total_rows = 0
                appended_rows = 0
                for r in rdr:
                    total_rows += 1
                    rows.append({
                        "name": r["name"],
                        "business_type": "Pub",
                        "website": "",
                        "lat": r["latitude"], "lon": r["longitude"],
                        "address_line1": r["address"],
                        "address_line2": "",
                        "postcode": r["postcode"],
                    })
                    appended_rows += 1
                print(f"Open Pubs rows read: {total_rows}, appended: {appended_rows}")
    else:
        print("Skipping Open-Pubs CSV due to download error.")

    # Filter rows to only those with a postcode starting with CM, SS, CO, IG, or RM
    postcode_prefixes = ("CM", "SS", "CO", "IG", "RM")
    filtered_rows = [r for r in rows if any(r["postcode"].upper().startswith(prefix) for prefix in postcode_prefixes)]

    # De-duplicate based on (name.lower(), postcode)
    unique = {}
    for r in filtered_rows:
        key = (r["name"].lower(), r["postcode"])
        if key not in unique:
            unique[key] = r

    deduped_rows = list(unique.values())

    # Remove chains unlikely to sell alcohol before enriching with websites
    deduped_rows = [r for r in deduped_rows if not is_excluded_chain(r["name"])]

    # Attempt to enrich with website information from OpenStreetMap
    if skip_osm:
        print("Skipping OpenStreetMap enrichment (disabled)")
    else:
        print("Querying OpenStreetMap for missing websites...")
        
        # Initialize cache and offline fallback
        try:
            from osm_cache import OSMCache, OSMOfflineData
            cache = OSMCache()
            offline_data = OSMOfflineData()
            print(f"  Using cache with {cache.get_stats()['total_cached']} entries")
        except ImportError:
            cache = None
            offline_data = None
            print("  Warning: Cache system not available")
        
        osm_enriched = 0
        osm_failed = 0
        osm_skipped = 0
        osm_cached = 0
        
        for idx, row in enumerate(deduped_rows, 1):
            if not row["website"] and row["postcode"] and row["name"]:
                try:
                    # Check if we got it from cache
                    was_cached = cache and cache.get_website(row["name"], row["postcode"]) is not None
                    
                    url = find_osm_website(row["name"], row["postcode"], cache, offline_data)
                    if url:
                        row["website"] = url
                        osm_enriched += 1
                        if was_cached:
                            osm_cached += 1
                        else:
                            print(f"  ✓ Found website for {row['name'][:30]}: {url[:50]}")
                    else:
                        osm_failed += 1
                except Exception as e:
                    osm_failed += 1
                    print(f"  ✗ Error for {row['name'][:30]}: {str(e)[:50]}")
                
                # Progress indicator
                if idx % 10 == 0:
                    print(f"  Progress: {idx}/{len(deduped_rows)} checked, {osm_enriched} enriched ({osm_cached} from cache)")
                    # Only sleep for non-cached requests
                    if not was_cached:
                        time.sleep(1)  # polite pause every few requests
            else:
                osm_skipped += 1
        
        # Save cache
        if cache:
            cache.finalize()
        
        print(f"\nOSM Enrichment Results:")
        print(f"  - Enriched: {osm_enriched}")
        print(f"  - From cache: {osm_cached}")
        print(f"  - Not found: {osm_failed}")
        print(f"  - Skipped (already has website): {osm_skipped}")

    # Apply business name filter BEFORE Google enrichment to save API calls
    print("\nApplying business name filters...")
    pre_filter_count = len(deduped_rows)
    filtered_rows = []
    for row in deduped_rows:
        if not should_exclude_business_name(row.get('name', '')):
            filtered_rows.append(row)
        else:
            filter_stats.log_filter(row.get('name', ''), 'Excluded business type', 'business_name')
    
    print(f"Filtered out {pre_filter_count - len(filtered_rows)} venues before enrichment")
    
    # Optional: use Google Programmable Search to fill any remaining blanks
    g_api_key = os.getenv("GOOGLE_API_KEY")
    g_cx = os.getenv("GOOGLE_CX")
    if g_api_key and g_cx:
        try:
            import google_website_enricher
            google_website_enricher.enrich_rows_with_google(filtered_rows, g_api_key, g_cx, filter_stats=filter_stats)
        except Exception as exc:
            print(f"Google enrichment failed: {exc}")
    else:
        print("Skipping Google enrichment. Set GOOGLE_API_KEY and GOOGLE_CX to enable.")

    print(f"\nWriting {len(filtered_rows):,} rows → {OUT}")
    
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filtered_rows)
    
    # Save filter log
    if filter_stats.filter_log:
        filter_stats.save_log("build_essex_filter_log.csv")
        print(f"Filter log saved to: build_essex_filter_log.csv")

if __name__ == "__main__":
    main()
