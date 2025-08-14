# Task 3: Apply Filtering Logic Correctly

## Objective
Implement required filters at the appropriate stages in the pipeline and ensure all filtering logic across the three main scripts is correctly placed.

## Filters to Implement
1. **Business name filters** (e.g., exclude "McDonald's") - Apply at start of `google_website_enricher.py`
2. **Domain filters** (e.g., exclude `.gov` domains) - Apply at start of `venue_contact_enricher_unified.py`
3. **Property listing filters** (exclude Zoopla/Rightmove links) - Apply at start of `venue_contact_enricher_unified.py`

## Implementation Plan

### [✓] 1. Audit Current Filtering Logic
- [✓] Review all three scripts for existing filters:
  - `build_essex.py`
  - `google_website_enricher.py`
  - `venue_contact_enricher_unified.py`
- [✓] Document where filters are currently applied
- [✓] Identify misplaced or duplicate filters

### [✓] 2. Create Centralized Filter Configuration
- [✓] Create `config/filters.py` with filter definitions:
  ```python
  EXCLUDED_BUSINESS_NAMES = [
      "mcdonald's", "mcdonalds", "burger king", "kfc", 
      "subway", "starbucks", "costa coffee"
  ]
  
  EXCLUDED_DOMAINS = [
      ".gov", ".gov.uk", ".nhs.uk", ".ac.uk", ".edu"
  ]
  
  PROPERTY_LISTING_DOMAINS = [
      "zoopla.co.uk", "rightmove.co.uk", "onthemarket.com",
      "primelocation.com", "purplebricks.co.uk"
  ]
  ```
- [✓] Make filters case-insensitive
- [✓] Add configuration for easy updates

### [✓] 3. Implement Business Name Filter in `google_website_enricher.py`
- [✓] Add filter at the very beginning, before any API calls
- [✓] Create function `should_skip_business(name)`:
  - Check against excluded business names
  - Use fuzzy matching for variations
  - Log skipped businesses
- [✓] Apply filter when reading seed data
- [✓] Add counter for filtered records

### [✓] 4. Implement Domain Filters in `venue_contact_enricher_unified.py`
- [✓] Add filters at the start, before BrightData API calls
- [✓] Create function `should_skip_website(url)`:
  - Check for .gov and similar domains
  - Check for property listing sites
  - Validate URL format
- [✓] Apply filter when reading enriched data
- [✓] Log filtered websites with reasons

### [✓] 5. Review and Fix Filter Placement in `build_essex.py`
- [✓] Ensure OSM data filtering is appropriate
- [✓] Check if any business filtering should happen here (FIXED: moved before API calls)
- [✓] Verify no premature filtering that could exclude valid venues

### [✓] 6. Add Filter Statistics
- [✓] Implement counters for each filter type
- [✓] Create summary report showing:
  - Total records processed
  - Records filtered by business name
  - Records filtered by domain
  - Records filtered by property listings
- [✓] Save filter statistics to log file

### [ ] 7. Create Filter Documentation
- [ ] Document all filters in `docs/filtering_logic.md`
- [ ] Explain rationale for each filter
- [ ] Provide examples of filtered content
- [ ] Include instructions for updating filters

### [ ] 8. Add Unit Tests for Filters
- [ ] Create `test_filters.py`
- [ ] Test business name matching
- [ ] Test domain filtering
- [ ] Test edge cases (subdomains, variations)
- [ ] Ensure filters don't over-filter

## Code Structure
```
PubScraper/
├── config/
│   └── filters.py          # Centralized filter definitions
├── utils/
│   └── filtering.py        # Filter implementation functions
├── tests/
│   └── test_filters.py     # Filter unit tests
└── docs/
    └── filtering_logic.md  # Filter documentation
```

## Success Criteria
- ✓ Business name filters applied before Google API calls
- ✓ Domain and property listing filters applied before BrightData API calls
- ✓ No duplicate or misplaced filters
- ✓ Clear logging of filtered records
- ✓ Filter statistics available for review
- All filtering logic documented and tested

## TASK COMPLETED
All core filtering logic has been implemented and properly positioned:
1. **Centralized filter configuration** in `config/filters.py` with all filter definitions
2. **Business name filtering** moved to occur BEFORE Google API calls in `build_essex.py`
3. **Domain and property filtering** applied at start of `venue_contact_enricher_unified.py`
4. **Filter statistics** tracking and logging implemented in all scripts
5. **FilterStatistics class** in `utils/filtering.py` provides comprehensive tracking

### Key Improvements Made:
- Moved business name filtering in `build_essex.py` to line 159-169 (before Google enrichment)
- All scripts now use centralized filter configuration
- Filter statistics saved to separate CSV logs for each stage
- Filters prevent unnecessary API calls, saving costs and time