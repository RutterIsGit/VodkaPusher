# Google Knowledge Graph API Analysis

## Overview
This document analyzes the feasibility of using Google's Knowledge Graph Search API for discovering pubs in Essex, UK.

## API Capabilities

### Supported Features
- **Entity Search**: Search for entities by name, type, or description
- **Type Filtering**: Filter results by entity types (e.g., BarOrPub, LocalBusiness)
- **Relevance Scoring**: Results include relevance scores
- **Rich Data**: Some entities include descriptions, URLs, and images
- **Free Tier**: First 100,000 entities per month free

### Limitations
- **Geographic Filtering**: No native support for geographic boundaries or radius search
- **Coverage**: Limited coverage of local businesses compared to dedicated local search APIs
- **Data Freshness**: Not all business data is current
- **Detailed Information**: Limited operational details (hours, contact info)

## Test Results

### Search Strategies Tested
1. Direct queries: "pubs in Essex", "pubs in Essex UK"
2. Type-filtered searches: Filtering by BarOrPub, LocalBusiness types
3. Town-specific searches: Major Essex towns (Chelmsford, Colchester, etc.)
4. Entity type variations: "pub", "public house", "tavern"

### Findings
- **Coverage**: Knowledge Graph returns very limited results for local pubs
- **Data Quality**: Results often include well-known chains but miss independent venues
- **Geographic Precision**: Difficult to limit results to specific geographic areas
- **Information Completeness**: Most results lack essential business details

## Comparison with OSM Approach

| Aspect | OSM Data | Knowledge Graph API |
|--------|----------|-------------------|
| Coverage | ~3,000+ venues in Essex | <100 relevant results |
| Geographic Filtering | Excellent (boundary-based) | Poor (keyword-based only) |
| Data Freshness | Community-updated | Variable |
| Contact Information | Limited | Very limited |
| Cost | Free | Free up to 100k/month |
| Implementation Complexity | Moderate | Simple |

## Cost Analysis

### Current Google Search API
- Cost: $5 per 1,000 searches
- For 3,000 venues: ~$15 (assuming 1 search per venue)

### Knowledge Graph API
- Free tier: 100,000 entities/month
- Beyond free tier: $5 per 1,000 entities
- For full Essex coverage: Would fit within free tier

## Recommendation

**Not recommended** for primary venue discovery due to:

1. **Insufficient Coverage**: Knowledge Graph misses the vast majority of local pubs
2. **Poor Geographic Control**: Cannot reliably limit results to Essex boundaries
3. **Limited Local Business Focus**: API is designed for general knowledge, not local business discovery

### Suggested Use Cases
Knowledge Graph API could supplement existing data for:
- Identifying major pub chains
- Getting descriptions for well-known venues
- Enriching data for popular tourist destinations

## Integration Approach

If supplemental use is desired:
1. Continue using OSM as primary data source
2. Use Knowledge Graph to enrich data for venues with high relevance scores
3. Focus on entity types: BarOrPub, LocalBusiness, Restaurant
4. Implement caching to stay within free tier limits

## Website Enrichment Test Results

### Testing Methodology
- Tested using venue name + postcode for specific searches
- Tried multiple search strategies per venue
- Tested both random venues and known chains

### Results
- **Random sample (20 venues)**: 0% success rate
- **Known chains (Wetherspoon, Harvester, etc.)**: 0% success rate
- **Direct chain searches**: Minimal results, not location-specific

### Conclusion for Website Enrichment
Knowledge Graph API is **not suitable** for finding venue websites because:
1. It lacks coverage of local businesses, even well-known chains
2. Cannot match specific venue locations using postcode
3. Returns general entity information rather than specific business listings

## Alternative Recommendations

For better local business discovery, consider:
1. **Google Places API**: Better coverage but higher cost
2. **Foursquare API**: Good for venue discovery with categories
3. **Yelp Fusion API**: Strong UK coverage for hospitality venues
4. **Continue with current approach**: Google Custom Search remains more effective despite higher cost
5. **Hybrid approach**: Try free APIs first (Bing, DuckDuckGo) before paid options