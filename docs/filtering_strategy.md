# Filtering Strategy Documentation

## Overview
This document outlines the filtering strategy for the PubScraper pipeline, ensuring efficient API usage and relevant results.

## Filter Placement Strategy

### 1. Build Essex (`build_essex.py`)
**No filtering at this stage** - Collect all potential venues from OSM to build comprehensive seed data.

### 2. Google Website Enricher (`google_website_enricher.py`)
**Filter before API calls** to save on API costs and processing time.

#### Business Name Filters
Applied at the start to exclude chain establishments:
- Fast food chains: McDonald's, Burger King, KFC, Subway
- Coffee chains: Starbucks, Costa Coffee, Caffè Nero
- Other chains that are clearly not pubs

**Rationale**: These businesses will never be pubs, so no point in enriching them.

### 3. Venue Contact Enricher (`venue_contact_enricher_final.py`)
**Filter before BrightData API calls** to avoid scraping inappropriate sites.

#### Domain Filters
Exclude government and institutional domains:
- `.gov`, `.gov.uk` - Government websites
- `.nhs.uk` - NHS websites
- `.ac.uk`, `.edu` - Educational institutions
- `.police.uk` - Police websites

**Rationale**: These domains won't contain pub contact information.

#### Property Listing Filters
Exclude real estate websites:
- `zoopla.co.uk`
- `rightmove.co.uk`
- `onthemarket.com`
- `primelocation.com`
- `purplebricks.co.uk`

**Rationale**: These are listing sites, not actual pub websites.

## Implementation Guidelines

### 1. Filter Functions
Create reusable filter functions that:
- Are case-insensitive
- Handle URL variations (www, https, etc.)
- Log filtered items for auditing
- Return clear reasons for filtering

### 2. Configuration
Store filter lists in configuration files:
- Easy to update without code changes
- Version controlled
- Well-documented

### 3. Logging
For each filtered item, log:
- Item filtered (business name or URL)
- Filter type applied
- Reason for filtering
- Timestamp

### 4. Statistics
Track filtering metrics:
- Total items processed
- Items filtered by each filter type
- Percentage filtered
- API calls saved

## Filter Examples

### Business Name Filter
```python
# Input: "McDonald's - Chelmsford High Street"
# Action: Skip (matches excluded business)
# Reason: "Chain restaurant - McDonald's"
```

### Domain Filter
```python
# Input: "https://www.essex.gov.uk/leisure/pubs"
# Action: Skip (matches .gov.uk)
# Reason: "Government domain"
```

### Property Listing Filter
```python
# Input: "https://www.zoopla.co.uk/for-sale/details/12345"
# Action: Skip (property listing site)
# Reason: "Property listing website"
```

## Maintenance

### Regular Review
- Monthly review of filter effectiveness
- Check for new chains to exclude
- Verify no legitimate pubs are filtered
- Update based on results analysis

### Adding New Filters
1. Document the reason for the new filter
2. Add to appropriate configuration file
3. Test with sample data
4. Monitor impact on results

### Removing Filters
1. Document why filter is no longer needed
2. Check historical impact
3. Remove from configuration
4. Monitor for any negative effects