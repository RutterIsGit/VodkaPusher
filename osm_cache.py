#!/usr/bin/env python3
"""OSM Cache system for offline fallback and persistence"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta

class OSMCache:
    """Cache system for OSM data with offline fallback"""
    
    def __init__(self, cache_dir: str = "cache/osm", cache_ttl_days: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.cache_file = self.cache_dir / "venue_websites.json"
        self.stats_file = self.cache_dir / "cache_stats.json"
        self._load_cache()
    
    def _load_cache(self):
        """Load existing cache from disk"""
        self.cache = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "additions": 0,
            "last_update": None
        }
        
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = data.get("venues", {})
                    print(f"Loaded {len(self.cache)} cached venue websites")
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.cache = {}
        
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                pass
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            data = {
                "venues": self.cache,
                "updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.stats["last_update"] = datetime.now().isoformat()
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get_website(self, name: str, postcode: str) -> Optional[str]:
        """Get cached website for venue"""
        key = f"{name.lower()}|{postcode}"
        
        if key in self.cache:
            entry = self.cache[key]
            # Check if cache entry is still valid
            if entry.get("timestamp"):
                cached_time = datetime.fromisoformat(entry["timestamp"])
                if datetime.now() - cached_time < self.cache_ttl:
                    self.stats["hits"] += 1
                    return entry.get("website")
            else:
                # Old cache format, still use it
                self.stats["hits"] += 1
                return entry.get("website")
        
        self.stats["misses"] += 1
        return None
    
    def set_website(self, name: str, postcode: str, website: Optional[str]):
        """Cache website for venue"""
        key = f"{name.lower()}|{postcode}"
        self.cache[key] = {
            "website": website,
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "postcode": postcode
        }
        self.stats["additions"] += 1
        
        # Save every 50 additions
        if self.stats["additions"] % 50 == 0:
            self._save_cache()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        return {
            "total_cached": len(self.cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "last_update": self.stats.get("last_update")
        }
    
    def finalize(self):
        """Save cache when done"""
        self._save_cache()
        print(f"\nCache Statistics:")
        stats = self.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")


class OSMOfflineData:
    """Provide offline OSM data from pre-downloaded extracts"""
    
    def __init__(self, data_dir: str = "cache/osm"):
        self.data_dir = Path(data_dir)
        self.essex_pubs_file = self.data_dir / "essex_pubs_osm.json"
        self.venues = []
        self._load_offline_data()
    
    def _load_offline_data(self):
        """Load pre-downloaded OSM data"""
        if self.essex_pubs_file.exists():
            try:
                with open(self.essex_pubs_file, 'r') as f:
                    data = json.load(f)
                    self.venues = data.get("venues", [])
                    print(f"Loaded {len(self.venues)} offline OSM venues")
            except Exception as e:
                print(f"Error loading offline data: {e}")
    
    def find_website(self, name: str, postcode: str) -> Optional[str]:
        """Find website in offline data"""
        name_lower = name.lower()
        
        # Try exact postcode match first
        for venue in self.venues:
            if (venue.get("name", "").lower() == name_lower and 
                venue.get("postcode") == postcode and
                venue.get("website")):
                return venue["website"]
        
        # Try fuzzy name match with postcode
        for venue in self.venues:
            if (venue.get("postcode") == postcode and
                venue.get("website") and
                name_lower in venue.get("name", "").lower()):
                return venue["website"]
        
        return None
    
    def download_essex_data(self):
        """Download Essex pub data from OSM (run this separately when API is available)"""
        print("This would download Essex OSM data when API is available")
        # This would be run separately when OSM is accessible
        # to create the offline data file