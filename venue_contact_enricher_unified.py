"""
Enhanced Venue Contact Enricher with Unified BrightData Integration.
Uses Browser API as primary method with Web Unlocker as fallback.
"""

import csv
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from dotenv import load_dotenv

from brightdata_browser_client import BrightDataClient
from config.filters import should_exclude_business_name, should_exclude_domain, get_filter_reason
from utils.filtering import FilterStatistics

load_dotenv()


class Config:
    """Load configuration from environment variables."""
    def __init__(self):
        # Helper function to parse env values
        def parse_env_int(key, default):
            value = os.getenv(key, default)
            if isinstance(value, str) and '#' in value:
                value = value.split('#')[0].strip()
            return int(value)
        
        def parse_env_float(key, default):
            value = os.getenv(key, default)
            if isinstance(value, str) and '#' in value:
                value = value.split('#')[0].strip()
            return float(value)
        
        self.max_requests = parse_env_int('ENRICHER_MAX_REQUESTS', '2000')
        self.delay_seconds = parse_env_float('ENRICHER_DELAY_SECONDS', '0.5')
        self.retry_attempts = 2  # Limited to 2 attempts
        self.timeout = parse_env_int('ENRICHER_TIMEOUT', '30')
        self.save_every_n = parse_env_int('ENRICHER_SAVE_EVERY_N', '50')
        self.use_brightdata = True


class EnhancedContactExtractor:
    """Extract and validate contact information from HTML."""
    
    # Invalid email patterns - files and resources
    INVALID_EMAIL_PATTERNS = [
        r'.*\.(png|jpg|jpeg|gif|bmp|svg|ico)@.*',  # Image files
        r'.*\.(css|js|json|xml|html|htm)@.*',      # Web resources
        r'.*\.(pdf|doc|docx|xls|xlsx|ppt|pptx)@.*', # Documents
        r'.*\.(mp3|mp4|avi|mov|wav)@.*',           # Media files
        r'.*\.(zip|rar|tar|gz|7z)@.*',             # Archives
        r'^[a-f0-9]{32}@.*',                       # MD5 hashes
        r'^[a-f0-9]{40}@.*',                       # SHA1 hashes
    ]
    
    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        """Validate email address with strict checks."""
        email_lower = email.lower()
        
        # Check against invalid patterns
        for pattern in cls.INVALID_EMAIL_PATTERNS:
            if re.match(pattern, email_lower):
                return False
        
        # Check for common invalid domains
        invalid_domains = ['example.com', 'email.com', 'domain.com', 'sentry.io',
                          'cloudflare', 'googleapis', 'gstatic', 'schema.org',
                          'fontawesome', 'w3.org', 'localhost']
        if any(domain in email_lower for domain in invalid_domains):
            return False
        
        # Check for role-based emails
        invalid_prefixes = ['noreply@', 'no-reply@', 'donotreply@', 'mailer-daemon@']
        if any(email_lower.startswith(prefix) for prefix in invalid_prefixes):
            return False
        
        # Basic email format validation
        email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        if not email_regex.match(email):
            return False
        
        # Length check
        if len(email) < 6 or len(email) > 100:
            return False
        
        return True
    
    @classmethod
    def extract_emails(cls, html: str) -> List[str]:
        """Extract valid email addresses from HTML."""
        # Pre-clean HTML
        cleaned_html = re.sub(r'(src|href)=["\'][^"\']*\.(png|jpg|jpeg|gif|css|js)[^"\']*["\']', '', html, flags=re.IGNORECASE)
        cleaned_html = re.sub(r'\b\w+[-@]\w+[-@]\w+\.(png|jpg|jpeg|gif|css|js)\b', '', cleaned_html, flags=re.IGNORECASE)
        
        # Also look for escaped emails in JSON/JavaScript
        # Handle various encoding formats
        escaped_html = html.replace('\\u0040', '@').replace('%40', '@').replace('\\\\u0040', '@')
        
        # Email pattern
        email_pattern = re.compile(r'\b[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Find emails in both cleaned and escaped versions
        all_emails = email_pattern.findall(cleaned_html) + email_pattern.findall(escaped_html)
        
        # Filter and validate
        valid_emails = []
        for email in all_emails:
            if cls.is_valid_email(email):
                valid_emails.append(email.lower())
        
        # Remove duplicates
        seen = set()
        unique_emails = []
        for email in valid_emails:
            if email not in seen:
                seen.add(email)
                unique_emails.append(email)
        
        return unique_emails
    
    @classmethod
    def extract_phones(cls, html: str) -> List[str]:
        """Extract UK phone numbers from HTML."""
        patterns = [
            # UK landline
            re.compile(r'\b0[12]\d{1,2}[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}\b'),
            # UK mobile
            re.compile(r'\b07\d{3}[\s\-\.]?\d{6}\b'),
            # UK non-geographic
            re.compile(r'\b0[38]\d{2}[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b'),
            # International format
            re.compile(r'\+44[\s\-\.]?[1-9]\d{1,2}[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}\b'),
            # With parentheses
            re.compile(r'\(\d{4,5}\)[\s\-\.]?\d{6,7}'),
        ]
        
        phones = []
        for pattern in patterns:
            matches = pattern.findall(html)
            for match in matches:
                cleaned = re.sub(r'[\s\-\.\(\)]', '', match)
                if len(cleaned) >= 10 and len(cleaned) <= 13:
                    phones.append(cleaned)
        
        return list(set(phones))




def fetch_with_retry(url: str, config: Config, brightdata_client: Optional[BrightDataClient] = None, 
                    attempt: int = 0) -> Tuple[Optional[str], str]:
    """
    Fetch URL with retry logic.
    Returns: (html_content, method_used)
    """
    # Validate URL
    if not url or not isinstance(url, str) or not url.strip():
        print(f"    Invalid URL: {url}")
        return None, 'invalid_url'
    
    url = url.strip()
    
    # Always use BrightData Browser API if available
    if brightdata_client and config.use_brightdata:
        print(f"    Attempt {attempt + 1}: Using BrightData Browser API...")
        try:
            html = brightdata_client.scrape_url(url, timeout=config.timeout)
            if html and len(html) > 100:
                return html, 'brightdata'
        except Exception as e:
            print(f"    BrightData failed: {e}")
    
    # Fallback to direct HTTP only if BrightData is not available or failed
    if not config.use_brightdata or attempt > 0:
        try:
            print(f"    Attempt {attempt + 1}: Trying direct HTTP as fallback...")
            response = requests.get(
                url, 
                timeout=30,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            if response.status_code == 200 and len(response.text) > 100:
                # Check if we got real content (not a captcha/block page)
                if 'captcha' not in response.text.lower() and 'blocked' not in response.text.lower():
                    return response.text, 'direct_http'
        except Exception as e:
            print(f"    Direct HTTP failed: {e}")
    
    # Retry if we haven't exhausted attempts
    if attempt < config.retry_attempts - 1:
        time.sleep(2 ** attempt)  # Exponential backoff
        return fetch_with_retry(url, config, brightdata_client, attempt + 1)
    
    return None, 'all_failed'


def process_venue(venue: Dict[str, str], config: Config, 
                 brightdata_client: Optional[BrightDataClient] = None,
                 filter_stats: Optional[FilterStatistics] = None) -> Dict[str, str]:
    """Process a single venue and extract contact info."""
    name = venue.get('name', '')
    website = venue.get('website', '')
    
    # Initialize result fields
    venue['email_found'] = ''
    venue['phone_found'] = ''
    venue['additional_emails'] = ''
    venue['additional_phones'] = ''
    venue['website_actual'] = ''
    venue['extraction_status'] = ''
    venue['extraction_notes'] = ''
    venue['extraction_method'] = ''
    venue['extraction_timestamp'] = datetime.now().isoformat()
    
    # Skip if no website
    if not website:
        venue['extraction_status'] = 'skipped'
        venue['extraction_notes'] = 'No website'
        if filter_stats:
            filter_stats.log_filter(name, 'No website', 'no_website')
        return venue
    
    # Skip excluded business names
    if should_exclude_business_name(name):
        venue['extraction_status'] = 'skipped'
        venue['extraction_notes'] = get_filter_reason(name=name)
        if filter_stats:
            filter_stats.log_filter(name, venue['extraction_notes'], 'business_name')
        return venue
    
    # Skip excluded domains (government, property listings, etc.)
    if should_exclude_domain(website):
        venue['extraction_status'] = 'skipped'
        venue['extraction_notes'] = get_filter_reason(url=website)
        if filter_stats:
            filter_type = 'property_listing' if 'property' in venue['extraction_notes'].lower() else 'domain'
            filter_stats.log_filter(name, venue['extraction_notes'], filter_type)
        return venue
    
    # Skip if already has email
    if venue.get('email') or venue.get('email_found'):
        venue['extraction_status'] = 'skipped'
        venue['extraction_notes'] = 'Already has email'
        return venue
    
    # Fetch website content
    start_time = time.time()
    html, method_used = fetch_with_retry(website, config, brightdata_client)
    fetch_time = time.time() - start_time
    
    venue['extraction_method'] = method_used
    
    if not html:
        venue['extraction_status'] = 'failed'
        venue['extraction_notes'] = f'Failed to fetch website after {config.retry_attempts} attempts'
        return venue
    
    # Extract contacts
    emails = EnhancedContactExtractor.extract_emails(html)
    phones = EnhancedContactExtractor.extract_phones(html)
    
    # Set primary and additional contacts
    if emails:
        venue['email_found'] = emails[0]
        if len(emails) > 1:
            venue['additional_emails'] = ';'.join(emails[1:4])
    
    if phones:
        venue['phone_found'] = phones[0]
        if len(phones) > 1:
            venue['additional_phones'] = ';'.join(phones[1:4])
    
    # For social media sites, try to find actual website
    domain = website.lower()
    if any(site in domain for site in ['facebook.com', 'tripadvisor', 'yelp.com']):
        website_pattern = re.compile(r'https?://(?!.*(facebook|tripadvisor|yelp))[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        external_sites = website_pattern.findall(html)
        if external_sites:
            venue['website_actual'] = external_sites[0]
    
    # Set status
    if venue['email_found'] or venue['phone_found']:
        venue['extraction_status'] = 'success'
        venue['extraction_notes'] = f"Found {len(emails)} emails, {len(phones)} phones in {fetch_time:.1f}s"
    else:
        venue['extraction_status'] = 'no_contact'
        venue['extraction_notes'] = f'No valid contact information found in {fetch_time:.1f}s'
    
    return venue


def enrich_venues():
    """Main function to enrich all venues."""
    config = Config()
    filter_stats = FilterStatistics()
    
    # Initialize BrightData client
    brightdata_client = None
    try:
        brightdata_client = BrightDataClient()
        print("BrightData client initialized successfully")
        print("Browser API and Web Unlocker API available")
        config.use_brightdata = True
    except ValueError as e:
        print(f"Warning: {e}")
        print("Falling back to direct HTTP requests only")
        config.use_brightdata = False
    
    input_file = "essex_venues_enriched.csv"
    output_file = "essex_venues_enriched_unified.csv"
    
    print(f"\nStarting enhanced venue contact enrichment")
    print(f"Configuration:")
    print(f"  Max requests: {config.max_requests}")
    print(f"  Max retries per venue: {config.retry_attempts}")
    print(f"  Delay between requests: {config.delay_seconds}s")
    print(f"  Save progress every: {config.save_every_n} venues")
    print(f"  Timeout: {config.timeout}s")
    print(f"  BrightData enabled: {config.use_brightdata}")
    print()
    
    # Read input venues
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        venues = list(reader)
        original_fieldnames = reader.fieldnames
    
    print(f"Loaded {len(venues)} venues from {input_file}")
    
    # Add extraction_method field if not present
    if 'extraction_method' not in original_fieldnames:
        output_fieldnames = list(original_fieldnames) + ['extraction_method']
    else:
        output_fieldnames = list(original_fieldnames)
    
    # Process venues
    processed_count = 0
    start_time = time.time()
    
    # Apply filters at the start before processing
    print("\nApplying filters...")
    venues_to_process = []
    
    for venue in venues:
        # Skip if already has email
        if venue.get('email') or venue.get('email_found'):
            continue
            
        # Apply filter checks
        should_process, reason = filter_stats.process_venue(venue)
        if should_process:
            venues_to_process.append(venue)
    
    print(f"\nAfter filtering:")
    print(f"  Venues to process: {len(venues_to_process)}")
    print(f"  Venues filtered out: {filter_stats.total_processed - len(venues_to_process)}")
    
    # Process filtered venues
    for i, venue in enumerate(venues_to_process):
        if processed_count >= config.max_requests:
            print(f"\nReached maximum requests limit ({config.max_requests})")
            break
        
        # Process venue
        print(f"\n[{i+1}/{len(venues_to_process)}] Processing: {venue.get('name', 'Unknown')[:50]:<50}")
        
        venue = process_venue(venue, config, brightdata_client, filter_stats)
        
        # Update in main list
        for j, v in enumerate(venues):
            if v.get('id') == venue.get('id') or v.get('name') == venue.get('name'):
                venues[j] = venue
                break
        
        processed_count += 1
        
        # Performance check
        elapsed = time.time() - start_time
        avg_time = elapsed / processed_count if processed_count > 0 else 0
        if avg_time > 10:
            print(f"  ⚠️  Warning: Average time per venue is {avg_time:.1f}s")
        
        time.sleep(config.delay_seconds)
        
        # Save progress periodically
        if processed_count % config.save_every_n == 0:
            print(f"\n  → Saving progress after {processed_count} venues...")
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=output_fieldnames)
                writer.writeheader()
                writer.writerows(venues)
    
    # Final save
    print(f"\n\nSaving final results to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(venues)
    
    # Calculate statistics
    elapsed_time = time.time() - start_time
    successful = sum(1 for v in venues if v.get('extraction_status') == 'success')
    with_email = sum(1 for v in venues if v.get('email_found'))
    with_phone = sum(1 for v in venues if v.get('phone_found'))
    
    # Print summary
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total venues:        {len(venues)}")
    print(f"Processed:           {processed_count}")
    print(f"Successful:          {successful}")
    print(f"With email:          {with_email}")
    print(f"With phone:          {with_phone}")
    print(f"Time elapsed:        {elapsed_time/60:.1f} minutes")
    print(f"Results saved to:    {output_file}")
    print(f"{'='*60}")
    
    # Print filter statistics
    print(f"\n{filter_stats.get_summary()}")
    
    # Save filter log
    filter_stats.save_log("venue_enricher_filter_log.csv")
    print(f"\nFilter log saved to: venue_enricher_filter_log.csv")


if __name__ == "__main__":
    try:
        enrich_venues()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()