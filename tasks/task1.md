# Task 1: Fix BrightData Enrichment Issues

## Objective
Investigate and resolve all issues with BrightData enrichment in `venue_contact_enricher_final.py` to ensure reliable contact information extraction from all website types.

## Issues to Address
1. **Tripadvisor and Facebook URLs fail to return data**
2. **Dynamic content websites sometimes return no data**
3. **Incorrect enrichment results (e.g., .png filenames instead of contact info)**

## Important Notes
- **Input Data**: Use `essex_venues_enriched.csv` for testing and validation
- **BrightData Integration**: Current implementation uses direct HTTP requests, not MCP tools
- **API Integration**: If BrightData API is needed, use their REST API with proper authentication
- **Documentation**: Refer to `docs/brightdata_mcp_tools.md` for BrightData capabilities reference

## Implementation Plan

### [ ] 1. Analyze Current Implementation
- [ ] Review `venue_contact_enricher_final.py` to understand current approach
- [ ] Identify that it currently uses basic HTTP requests, not BrightData
- [ ] Analyze failure patterns in `essex_venues_enriched.csv`
- [ ] Document which URLs are failing and why

### [ ] 2. Research BrightData API Integration
- [ ] Review BrightData Web Scraper API documentation
- [ ] Check `test_brightdata_api.py` for API usage examples
- [ ] Understand authentication using Bearer token from .env
- [ ] Research BrightData's specialized endpoints:
  - Web Scraper API for general sites
  - Web Data API for platform-specific data (Facebook, Tripadvisor)
  - Browser API for JavaScript-heavy sites

### [ ] 3. Implement BrightData API Client
- [ ] Create `brightdata_client.py` with proper API integration
- [ ] Add configuration for API key from .env file
- [ ] Implement methods:
  - `scrape_website(url)` - General web scraping
  - `scrape_facebook_business(url)` - Facebook-specific endpoint
  - `scrape_with_browser(url)` - For dynamic content
- [ ] Add proper error handling and response parsing
- [ ] Implement rate limiting (respect API limits)

### [ ] 4. Implement Smart URL Router
- [ ] Create function to classify URLs by type:
  ```python
  def classify_url(url):
      if 'facebook.com' in url:
          return 'facebook'
      elif 'tripadvisor' in url:
          return 'tripadvisor'
      elif requires_javascript(url):
          return 'dynamic'
      else:
          return 'static'
  ```
- [ ] Route to appropriate BrightData endpoint based on classification
- [ ] Add fallback chain if primary method fails

### [ ] 5. Fix Facebook Handler
- [ ] Use BrightData's Facebook-specific API if available
- [ ] Extract business information from structured response
- [ ] Parse contact details from "About" section
- [ ] Handle various Facebook page formats
- [ ] Add retry with browser API if needed

### [ ] 6. Fix Tripadvisor Handler
- [ ] Implement browser-based scraping for Tripadvisor
- [ ] Wait for dynamic content to load
- [ ] Look for contact information in business details
- [ ] Extract phone numbers and websites
- [ ] Handle rate limiting and CAPTCHAs

### [ ] 7. Add Robust Content Validation
- [ ] Strengthen email validation:
  ```python
  # Reject patterns like image.png, style.css, etc.
  def is_valid_email(email):
      if email.endswith(('.png', '.jpg', '.css', '.js')):
          return False
      # Proper email regex
      return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))
  ```
- [ ] Validate phone numbers against UK formats
- [ ] Log all rejected values for debugging
- [ ] Create whitelist of known good patterns

### [ ] 8. Implement Limited Retry Logic
- [ ] Set maximum retry attempts to 2 (to avoid long runs)
- [ ] Use exponential backoff: 1s, 2s
- [ ] Try methods in order:
  1. Direct HTTP request (current method)
  2. BrightData Web Scraper API
  3. BrightData Browser API (only for known dynamic sites)
- [ ] Stop on first success
- [ ] Log total time spent per venue

### [ ] 9. Testing and Validation
- [ ] Create `test_enrichment_fixes.py`
- [ ] Test with problematic URLs from `essex_venues_enriched.csv`
- [ ] Focus on venues with `extraction_status` = 'failed' or 'no_contact'
- [ ] Verify improvements:
  - Facebook pages now return data
  - Tripadvisor pages extract contacts
  - No .png files in email results
- [ ] Generate before/after comparison report

### [ ] 10. Performance Optimization
- [ ] Limit total API calls per run
- [ ] Add timeout limits (30s max per venue)
- [ ] Skip venues already successfully enriched
- [ ] Implement progress saving every 25 venues
- [ ] Add estimated completion time display

## Key Code Changes
1. Replace basic HTTP requests with BrightData API calls
2. Add URL classification and routing logic
3. Implement strict validation for extracted data
4. Add limited retry mechanism
5. Improve logging and error reporting

## Success Criteria
- At least 50% improvement in contact extraction for Facebook/Tripadvisor
- Zero .png or invalid file extensions in email results
- Average processing time under 10 seconds per venue
- Clear logs showing which method succeeded
- No infinite retry loops or excessive API usage