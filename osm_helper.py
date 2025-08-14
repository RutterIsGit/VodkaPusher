#!/usr/bin/env python3
"""Robust OpenStreetMap helper with fallback servers and error handling"""

import requests
import time
import json
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta

class OSMHelper:
    """Helper class for OpenStreetMap Overpass API queries with robust error handling"""
    
    # Multiple Overpass API servers for fallback
    SERVERS = [
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass-api.de/api/interpreter", 
        "https://overpass.openstreetmap.ru/api/interpreter",
        "https://overpass.openstreetmap.fr/api/interpreter"
    ]
    
    def __init__(self, timeout: int = 30, retry_delay: float = 1.0):
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.last_request_time = {}
        self.failed_servers = set()
        self.request_count = 0
        
    def _rate_limit(self, server: str):
        """Implement rate limiting per server"""
        if server in self.last_request_time:
            elapsed = time.time() - self.last_request_time[server]
            if elapsed < self.retry_delay:
                time.sleep(self.retry_delay - elapsed)
        self.last_request_time[server] = time.time()
    
    def query(self, query_string: str, max_retries: int = 2) -> Optional[Dict]:
        """
        Execute an Overpass query with automatic server fallback
        
        Args:
            query_string: The Overpass QL query
            max_retries: Maximum retries per server
            
        Returns:
            Query results as dict or None if all servers fail
        """
        errors = []
        
        for server in self.SERVERS:
            if server in self.failed_servers:
                continue
                
            for attempt in range(max_retries):
                try:
                    self._rate_limit(server)
                    
                    response = requests.get(
                        server,
                        params={"data": query_string},
                        timeout=self.timeout,
                        headers={"User-Agent": "PubScraper/1.0"}
                    )
                    
                    if response.status_code == 200:
                        self.request_count += 1
                        return response.json()
                    elif response.status_code == 429:
                        # Rate limited - wait longer
                        wait_time = min(60, 2 ** (attempt + 2))
                        errors.append(f"{server}: Rate limited, waiting {wait_time}s")
                        time.sleep(wait_time)
                    elif response.status_code >= 500:
                        # Server error - try next server
                        errors.append(f"{server}: Server error {response.status_code}")
                        break
                    else:
                        errors.append(f"{server}: HTTP {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    errors.append(f"{server}: Timeout after {self.timeout}s")
                except requests.exceptions.ConnectionError as e:
                    errors.append(f"{server}: Connection error")
                    self.failed_servers.add(server)
                    break
                except Exception as e:
                    errors.append(f"{server}: {str(e)[:100]}")
                    
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        
        # Log all errors if all servers failed
        if errors:
            print(f"OSM query failed. Errors: {'; '.join(errors[:3])}")
        
        return None
    
    def find_website(self, name: str, postcode: str) -> Optional[str]:
        """
        Find website URL for a venue by name and postcode
        
        Args:
            name: Venue name
            postcode: UK postcode
            
        Returns:
            Website URL or None if not found
        """
        def esc(v: str) -> str:
            return v.replace('"', '\\"').replace('\\', '\\\\')
        
        # Try exact match first
        query = f"""
        [out:json][timeout:25];
        (
          nwr["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["website"];
          nwr["name"="{esc(name)}"]["addr:postcode"="{postcode}"]["contact:website"];
        );
        out center;
        """
        
        result = self.query(query)
        if result:
            for el in result.get("elements", []):
                tags = el.get("tags", {})
                if "website" in tags:
                    return tags["website"]
                if "contact:website" in tags:
                    return tags["contact:website"]
        
        # Try case-insensitive match
        query_fuzzy = f"""
        [out:json][timeout:25];
        (
          nwr["name"~"{esc(name)}",i]["addr:postcode"="{postcode}"]["website"];
          nwr["name"~"{esc(name)}",i]["addr:postcode"="{postcode}"]["contact:website"];
        );
        out center;
        """
        
        result = self.query(query_fuzzy)
        if result:
            for el in result.get("elements", []):
                tags = el.get("tags", {})
                if "website" in tags:
                    return tags["website"]
                if "contact:website" in tags:
                    return tags["contact:website"]
        
        return None
    
    def get_essex_venues(self) -> List[Dict]:
        """
        Get all pubs and bars in Essex
        
        Returns:
            List of venue dictionaries
        """
        # Query for Essex pubs using area
        query = """
        [out:json][timeout:90];
        area["name"="Essex"]["admin_level"="6"]->.essex;
        (
          node["amenity"~"pub|bar|biergarten"](area.essex);
          way["amenity"~"pub|bar|biergarten"](area.essex);
          node["tourism"="hotel"]["bar"="yes"](area.essex);
          way["tourism"="hotel"]["bar"="yes"](area.essex);
        );
        out center tags;
        """
        
        result = self.query(query)
        if not result:
            return []
        
        venues = []
        for el in result.get("elements", []):
            tags = el.get("tags", {})
            
            # Extract venue data
            venue = {
                "name": tags.get("name", ""),
                "website": tags.get("website") or tags.get("contact:website", ""),
                "lat": el.get("lat") or el.get("center", {}).get("lat", ""),
                "lon": el.get("lon") or el.get("center", {}).get("lon", ""),
                "postcode": tags.get("addr:postcode", ""),
                "address": tags.get("addr:street", ""),
                "amenity": tags.get("amenity", ""),
                "source": "OSM"
            }
            
            if venue["name"]:  # Only include if has a name
                venues.append(venue)
        
        return venues


# Standalone function for backward compatibility
def find_osm_website_robust(name: str, postcode: str) -> Optional[str]:
    """
    Backward compatible function to find website from OSM
    
    Args:
        name: Venue name
        postcode: UK postcode
        
    Returns:
        Website URL or None
    """
    helper = OSMHelper(timeout=30)
    return helper.find_website(name, postcode)