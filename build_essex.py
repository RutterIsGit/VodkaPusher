import os, zipfile, io, requests, csv, time
from pathlib import Path
from bs4 import BeautifulSoup   # pip install beautifulsoup4 lxml

OUT = Path("essex_licensed_venues.csv")
cols = ["name","business_type","website","lat","lon",
        "address_line1","address_line2","postcode"]

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

def find_osm_website(name, postcode):
    """Lookup a business website in OSM via Overpass using name and postcode."""
    def esc(v: str) -> str:
        return v.replace('"', '\\"')

    query = f"""
    [out:json][timeout:25];
    (
      node["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["website"];
      node["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["contact:website"];
      way["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["website"];
      way["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["contact:website"];
      relation["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["website"];
      relation["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["contact:website"];
    );
    out tags;
    """

    try:
        resp = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Overpass error for {name!r} {postcode}: {e}")
        return None

    for el in data.get("elements", []):
        tags = el.get("tags", {})
        if "website" in tags:
            return tags["website"]
        if "contact:website" in tags:
            return tags["contact:website"]
    return None

def main():
    rows = []
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

    # Attempt to enrich with website information from OpenStreetMap
    print("Querying OpenStreetMap for missing websites...")
    for idx, row in enumerate(deduped_rows, 1):
        if not row["website"] and row["postcode"] and row["name"]:
            url = find_osm_website(row["name"], row["postcode"])
            if url:
                row["website"] = url
            # polite pause every few requests to avoid hammering the API
            if idx % 10 == 0:
                time.sleep(1)

    print(f"Writing {len(deduped_rows):,} rows → {OUT}")
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(deduped_rows)

if __name__ == "__main__":
    main()
