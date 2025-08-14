#!/usr/bin/env python3
import os
import time
import csv
import json
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HunterClient:
    BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.credits_used = 0
        self.rate_limit_delay = float(os.getenv('HUNTER_DELAY_SECONDS', '1.0'))
        
    def search_domain(self, domain: str, limit: int = 10) -> Dict:
        endpoint = f"{self.BASE_URL}/domain-search"
        params = {
            'domain': domain,
            'api_key': self.api_key,
            'limit': limit
        }
        
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'data' in result:
                self.credits_used += 1
                return result['data']
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching domain {domain}: {e}")
            return {}
    
    def verify_email(self, email: str) -> Dict:
        endpoint = f"{self.BASE_URL}/email-verifier"
        params = {
            'email': email,
            'api_key': self.api_key
        }
        
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'data' in result:
                self.credits_used += 1
                return result['data']
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error verifying email {email}: {e}")
            return {}
    
    def get_account_info(self) -> Dict:
        endpoint = f"{self.BASE_URL}/account"
        params = {'api_key': self.api_key}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get('data', {})
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting account info: {e}")
            return {}


class EmailEnricher:
    def __init__(self, hunter_client: HunterClient):
        self.hunter = hunter_client
        self.max_verifications = int(os.getenv('HUNTER_MAX_VERIFICATIONS', '1000'))
        self.max_searches = int(os.getenv('HUNTER_MAX_SEARCHES', '500'))
        self.confidence_threshold = int(os.getenv('HUNTER_CONFIDENCE_THRESHOLD', '70'))
        self.save_every_n = int(os.getenv('HUNTER_SAVE_EVERY_N', '50'))
        
        self.stats = {
            'emails_found': 0,
            'emails_verified': 0,
            'invalid_emails': 0,
            'searches_performed': 0,
            'verifications_performed': 0,
            'credits_used': 0
        }
    
    def extract_domain(self, website: str) -> Optional[str]:
        if not website:
            return None
            
        if not website.startswith(('http://', 'https://')):
            website = f'http://{website}'
            
        try:
            parsed = urlparse(website)
            domain = parsed.netloc.lower()
            
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain if domain else None
        except Exception as e:
            logger.error(f"Error extracting domain from {website}: {e}")
            return None
    
    def find_email_for_venue(self, venue: Dict) -> Optional[str]:
        website = venue.get('website', '').strip()
        if not website:
            return None
            
        domain = self.extract_domain(website)
        if not domain:
            return None
            
        if self.stats['searches_performed'] >= self.max_searches:
            logger.warning("Reached maximum search limit")
            return None
            
        logger.info(f"Searching for emails at domain: {domain}")
        search_result = self.hunter.search_domain(domain, limit=5)
        self.stats['searches_performed'] += 1
        
        if not search_result or 'emails' not in search_result:
            return None
            
        emails = search_result['emails']
        if not emails:
            return None
            
        best_email = self.select_best_email(emails)
        if best_email:
            self.stats['emails_found'] += 1
            logger.info(f"Found email: {best_email}")
            
        return best_email
    
    def select_best_email(self, emails: List[Dict]) -> Optional[str]:
        role_priority = [
            'info', 'contact', 'hello', 'enquiries', 'bookings',
            'reservations', 'admin', 'office', 'reception'
        ]
        
        filtered_emails = [
            e for e in emails 
            if e.get('confidence', 0) >= self.confidence_threshold
        ]
        
        if not filtered_emails:
            filtered_emails = emails
        
        for role in role_priority:
            for email_data in filtered_emails:
                email = email_data.get('value', '')
                if role in email.lower():
                    return email
        
        filtered_emails.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        for email_data in filtered_emails:
            email = email_data.get('value', '')
            if '@' in email:
                return email
        
        return None
    
    def verify_email_address(self, email: str) -> Tuple[bool, str]:
        if not email or '@' not in email:
            return False, 'invalid'
            
        if self.stats['verifications_performed'] >= self.max_verifications:
            logger.warning("Reached maximum verification limit")
            return True, 'unverified'
            
        logger.info(f"Verifying email: {email}")
        result = self.hunter.verify_email(email)
        self.stats['verifications_performed'] += 1
        
        if not result:
            return True, 'unverified'
            
        status = result.get('result', 'unverifiable')
        score = result.get('score', 0)
        
        if status == 'deliverable' or score >= 70:
            self.stats['emails_verified'] += 1
            return True, 'verified'
        elif status == 'undeliverable' or score < 30:
            self.stats['invalid_emails'] += 1
            return False, 'invalid'
        else:
            return True, 'risky'
    
    def enrich_venue(self, venue: Dict) -> Dict:
        enriched = venue.copy()
        current_email = venue.get('email', '').strip()
        
        if current_email:
            is_valid, status = self.verify_email_address(current_email)
            enriched['email_status'] = status
            
            if not is_valid:
                logger.info(f"Invalid email detected: {current_email}")
                enriched['email'] = ''
                enriched['old_email'] = current_email
                current_email = ''
        
        if not current_email:
            found_email = self.find_email_for_venue(venue)
            if found_email:
                enriched['email'] = found_email
                enriched['email_source'] = 'hunter'
                enriched['email_status'] = 'new'
        
        return enriched
    
    def process_batch(self, venues: List[Dict], output_file: str = None) -> List[Dict]:
        enriched_venues = []
        
        account_info = self.hunter.get_account_info()
        if account_info:
            available_credits = account_info.get('requests', {}).get('available', 0)
            logger.info(f"Hunter API credits available: {available_credits}")
        
        for i, venue in enumerate(venues, 1):
            logger.info(f"Processing venue {i}/{len(venues)}: {venue.get('name', 'Unknown')}")
            
            enriched = self.enrich_venue(venue)
            enriched_venues.append(enriched)
            
            if output_file and i % self.save_every_n == 0:
                self.save_progress(enriched_venues, output_file)
                logger.info(f"Progress saved after {i} venues")
        
        self.stats['credits_used'] = self.hunter.credits_used
        
        if output_file:
            self.save_progress(enriched_venues, output_file)
            
        return enriched_venues
    
    def save_progress(self, venues: List[Dict], output_file: str):
        if not venues:
            return
            
        fieldnames = list(venues[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(venues)
        
        logger.info(f"Saved {len(venues)} venues to {output_file}")
    
    def generate_report(self) -> Dict:
        report = {
            'summary': self.stats,
            'cost_estimate': {
                'searches': self.stats['searches_performed'] * 0.01,
                'verifications': self.stats['verifications_performed'] * 0.005,
                'total': (self.stats['searches_performed'] * 0.01) + 
                        (self.stats['verifications_performed'] * 0.005)
            }
        }
        
        logger.info("Enrichment Report:")
        logger.info(f"  Emails found: {self.stats['emails_found']}")
        logger.info(f"  Emails verified: {self.stats['emails_verified']}")
        logger.info(f"  Invalid emails: {self.stats['invalid_emails']}")
        logger.info(f"  API credits used: {self.stats['credits_used']}")
        logger.info(f"  Estimated cost: ${report['cost_estimate']['total']:.2f}")
        
        return report


def main():
    api_key = os.getenv('HUNTER_API_KEY')
    if not api_key:
        logger.error("HUNTER_API_KEY not found in environment variables")
        return
    
    input_file = 'essex_venues_enriched.csv'
    output_file = 'essex_venues_hunter_enriched.csv'
    
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return
    
    venues = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        venues = list(reader)
    
    logger.info(f"Loaded {len(venues)} venues from {input_file}")
    
    hunter_client = HunterClient(api_key)
    enricher = EmailEnricher(hunter_client)
    
    dry_run = os.getenv('HUNTER_DRY_RUN', 'false').lower() == 'true'
    if dry_run:
        logger.info("DRY RUN MODE - No API calls will be made")
        sample_size = min(10, len(venues))
        logger.info(f"Processing sample of {sample_size} venues")
        venues = venues[:sample_size]
    
    enriched_venues = enricher.process_batch(venues, output_file)
    
    report = enricher.generate_report()
    
    with open('hunter_enrichment_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Enrichment complete. Output saved to {output_file}")
    logger.info(f"Report saved to hunter_enrichment_report.json")


if __name__ == "__main__":
    main()