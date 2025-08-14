"""
Filtering utilities for the venue enrichment pipeline.
"""

from typing import Dict, List, Tuple
from config.filters import (
    should_exclude_business_name,
    should_exclude_domain,
    get_filter_reason
)


class FilterStatistics:
    """Track filtering statistics throughout the pipeline."""
    
    def __init__(self):
        self.total_processed = 0
        self.filtered_by_business_name = 0
        self.filtered_by_domain = 0
        self.filtered_by_property_listing = 0
        self.filtered_no_website = 0
        self.passed_all_filters = 0
        self.filter_log = []
    
    def log_filter(self, venue_name: str, reason: str, filter_type: str):
        """Log a filtered venue."""
        self.filter_log.append({
            'venue_name': venue_name,
            'reason': reason,
            'filter_type': filter_type
        })
        
        if filter_type == 'business_name':
            self.filtered_by_business_name += 1
        elif filter_type == 'domain':
            self.filtered_by_domain += 1
        elif filter_type == 'property_listing':
            self.filtered_by_property_listing += 1
        elif filter_type == 'no_website':
            self.filtered_no_website += 1
    
    def process_venue(self, venue: Dict[str, str]) -> Tuple[bool, str]:
        """
        Process a venue and determine if it should be filtered.
        Returns: (should_continue, filter_reason)
        """
        self.total_processed += 1
        
        name = venue.get('name', '')
        website = venue.get('website', '')
        
        # Check business name
        if should_exclude_business_name(name):
            reason = get_filter_reason(name=name)
            self.log_filter(name, reason, 'business_name')
            return False, reason
        
        # Check if has website
        if not website:
            self.log_filter(name, 'No website', 'no_website')
            return False, 'No website'
        
        # Check domain
        if should_exclude_domain(website):
            reason = get_filter_reason(url=website)
            filter_type = 'property_listing' if 'property' in reason.lower() else 'domain'
            self.log_filter(name, reason, filter_type)
            return False, reason
        
        self.passed_all_filters += 1
        return True, ''
    
    def get_summary(self) -> str:
        """Get a formatted summary of filter statistics."""
        summary = [
            "FILTER STATISTICS",
            "=" * 60,
            f"Total venues processed:        {self.total_processed}",
            f"Passed all filters:            {self.passed_all_filters}",
            f"Filtered by business name:     {self.filtered_by_business_name}",
            f"Filtered by domain:            {self.filtered_by_domain}",
            f"Filtered by property listing:  {self.filtered_by_property_listing}",
            f"Filtered - no website:         {self.filtered_no_website}",
            "-" * 60,
            f"Total filtered:                {self.total_processed - self.passed_all_filters}",
            f"Pass rate:                     {self.passed_all_filters / self.total_processed * 100:.1f}%" if self.total_processed > 0 else "N/A"
        ]
        return "\n".join(summary)
    
    def save_log(self, filepath: str):
        """Save detailed filter log to file."""
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if self.filter_log:
                writer = csv.DictWriter(f, fieldnames=['venue_name', 'reason', 'filter_type'])
                writer.writeheader()
                writer.writerows(self.filter_log)