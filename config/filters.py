"""
Centralized filter configuration for the venue enrichment pipeline.
"""

# Business names to exclude (case-insensitive)
EXCLUDED_BUSINESS_NAMES = [
    "mcdonald's", "mcdonalds", "burger king", "kfc", 
    "subway", "starbucks", "costa coffee", "costa",
    "pret a manger", "pret", "five guys", "taco bell",
    "nandos", "nando's", "popeyes", "wendy's", "wendys",
    "greggs", "pizza hut", "dominos", "domino's", 
    "papa johns", "papa john's", "john lewis"
]

# Keywords that indicate non-alcohol venues
EXCLUDED_KEYWORDS = [
    "coffee", "cafe", "tea", "bakery", "sandwich"
]

# Domains to exclude (government, educational, etc.)
EXCLUDED_DOMAINS = [
    ".gov", ".gov.uk", ".nhs.uk", ".ac.uk", ".edu",
    ".police.uk", ".mod.uk", ".parliament.uk"
]

# Property listing and aggregator domains
PROPERTY_LISTING_DOMAINS = [
    "zoopla.co.uk", "rightmove.co.uk", "onthemarket.com",
    "primelocation.com", "purplebricks.co.uk", "foxtons.co.uk",
    "knight-frank.co.uk", "savills.co.uk", "hamptons.co.uk",
    "spareroom.co.uk", "openrent.com"
]

# Business directory and aggregator sites
BUSINESS_DIRECTORIES = [
    "yell.com", "yelp.com", "yelp.co.uk", "tripadvisor.com",
    "tripadvisor.co.uk", "scoot.co.uk", "192.com",
    "thomsonlocal.com", "opentable.com", "opentable.co.uk",
    "bookatable.com", "bookatable.co.uk", "timeout.com",
    "designmynight.com", "hardens.com", "allinlondon.co.uk",
    "squaremeal.co.uk", "londontown.com", "visitlondon.com"
]

# Social media domains (for filtering when needed)
SOCIAL_MEDIA_DOMAINS = [
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "tiktok.com", "youtube.com", "pinterest.com"
]


def should_exclude_business_name(name: str) -> bool:
    """Check if a business name should be excluded."""
    if not name:
        return True
        
    name_lower = name.lower().strip()
    
    # Check exact matches for excluded chains
    for excluded in EXCLUDED_BUSINESS_NAMES:
        if excluded in name_lower:
            return True
    
    # Check for excluded keywords
    for keyword in EXCLUDED_KEYWORDS:
        if keyword in name_lower:
            return True
    
    return False


def should_exclude_domain(url: str) -> bool:
    """Check if a URL/domain should be excluded."""
    if not url:
        return True
        
    url_lower = url.lower().strip()
    
    # Check government/educational domains
    for domain in EXCLUDED_DOMAINS:
        if domain in url_lower:
            return True
    
    # Check property listing sites
    for domain in PROPERTY_LISTING_DOMAINS:
        if domain in url_lower:
            return True
    
    # Check business directories
    for domain in BUSINESS_DIRECTORIES:
        if domain in url_lower:
            return True
    
    return False


def get_filter_reason(name: str = None, url: str = None) -> str:
    """Get a human-readable reason for why something was filtered."""
    reasons = []
    
    if name and should_exclude_business_name(name):
        name_lower = name.lower()
        if any(chain in name_lower for chain in EXCLUDED_BUSINESS_NAMES):
            reasons.append("Excluded chain/franchise")
        elif any(kw in name_lower for kw in EXCLUDED_KEYWORDS):
            reasons.append("Non-alcohol venue (coffee/cafe/tea)")
    
    if url and should_exclude_domain(url):
        url_lower = url.lower()
        if any(d in url_lower for d in EXCLUDED_DOMAINS):
            reasons.append("Government/educational domain")
        elif any(d in url_lower for d in PROPERTY_LISTING_DOMAINS):
            reasons.append("Property listing site")
        elif any(d in url_lower for d in BUSINESS_DIRECTORIES):
            reasons.append("Business directory/aggregator")
    
    return " | ".join(reasons) if reasons else "Unknown reason"