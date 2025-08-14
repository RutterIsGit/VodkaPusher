"""
Quick script to check enrichment status and identify problematic venues.
"""

import csv
from collections import Counter


def analyze_enrichment_file(filename):
    """Analyze an enrichment CSV file and return statistics."""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        venues = list(reader)
    
    stats = {
        'total': len(venues),
        'with_email': sum(1 for v in venues if v.get('email_found')),
        'with_phone': sum(1 for v in venues if v.get('phone_found')),
        'status_counts': Counter(v.get('extraction_status', 'unknown') for v in venues),
        'facebook_urls': sum(1 for v in venues if 'facebook.com' in v.get('website', '')),
        'tripadvisor_urls': sum(1 for v in venues if 'tripadvisor' in v.get('website', '')),
        'png_emails': [v for v in venues if '.png' in v.get('email_found', '')],
        'failed_venues': [v for v in venues if v.get('extraction_status') == 'failed'][:5]
    }
    
    return stats


def main():
    """Compare original and fixed enrichment files."""
    print("Essex Venues Enrichment Status Check")
    print("=" * 60)
    
    # Analyze original file
    print("\nOriginal enriched file (essex_venues_enriched.csv):")
    print("-" * 60)
    
    try:
        original_stats = analyze_enrichment_file('essex_venues_enriched.csv')
        
        print(f"Total venues: {original_stats['total']}")
        print(f"With email: {original_stats['with_email']} ({original_stats['with_email']/original_stats['total']*100:.1f}%)")
        print(f"With phone: {original_stats['with_phone']} ({original_stats['with_phone']/original_stats['total']*100:.1f}%)")
        print(f"\nFacebook URLs: {original_stats['facebook_urls']}")
        print(f"TripAdvisor URLs: {original_stats['tripadvisor_urls']}")
        print(f"PNG emails found: {len(original_stats['png_emails'])}")
        
        print(f"\nStatus breakdown:")
        for status, count in original_stats['status_counts'].items():
            print(f"  {status}: {count}")
        
        if original_stats['png_emails']:
            print(f"\nExample PNG emails:")
            for v in original_stats['png_emails'][:3]:
                print(f"  - {v['name']}: {v['email_found']}")
        
    except FileNotFoundError:
        print("File not found!")
    
    # Check if fixed file exists
    print("\n\nFixed enriched file (essex_venues_enriched_fixed.csv):")
    print("-" * 60)
    
    try:
        fixed_stats = analyze_enrichment_file('essex_venues_enriched_fixed.csv')
        
        print(f"Total venues: {fixed_stats['total']}")
        print(f"With email: {fixed_stats['with_email']} ({fixed_stats['with_email']/fixed_stats['total']*100:.1f}%)")
        print(f"With phone: {fixed_stats['with_phone']} ({fixed_stats['with_phone']/fixed_stats['total']*100:.1f}%)")
        print(f"\nPNG emails found: {len(fixed_stats['png_emails'])}")
        
        print(f"\nStatus breakdown:")
        for status, count in fixed_stats['status_counts'].items():
            print(f"  {status}: {count}")
        
        # Calculate improvements
        if 'original_stats' in locals():
            print("\n\nImprovements:")
            print("-" * 60)
            email_improvement = fixed_stats['with_email'] - original_stats['with_email']
            phone_improvement = fixed_stats['with_phone'] - original_stats['with_phone']
            print(f"Additional emails found: +{email_improvement}")
            print(f"Additional phones found: +{phone_improvement}")
            print(f"PNG emails removed: {len(original_stats['png_emails']) - len(fixed_stats['png_emails'])}")
            
    except FileNotFoundError:
        print("Fixed file not found - run venue_contact_enricher_brightdata.py to create it")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()