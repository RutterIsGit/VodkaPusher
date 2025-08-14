# Task 6: Add Final Email Enrichment Using Hunter API

## Objective
Add a final enrichment step using the Hunter Domain Search and Email Verifier APIs to find missing emails and verify existing ones. Create corresponding frontend button and documentation.

## Implementation Plan

### [ ] 1. Research Hunter API
- [ ] Review Hunter.io API documentation
- [ ] Understand available endpoints:
  - Domain Search - Find emails by domain
  - Email Finder - Find specific person's email
  - Email Verifier - Verify email validity
- [ ] Check rate limits and pricing tiers
- [ ] Identify best practices for bulk operations

### [ ] 2. Create Hunter Integration Script
- [ ] Create `hunter_email_enricher.py`
- [ ] Implement Hunter API client class
- [ ] Add configuration for API key management
- [ ] Create functions for:
  - Domain-based email search
  - Email verification
  - Bulk processing with rate limiting

### [ ] 3. Implement Email Discovery Logic
- [ ] For venues with websites but no email:
  - Extract domain from website URL
  - Use Domain Search to find emails
  - Prioritize generic emails (info@, contact@, etc.)
  - Score and rank results by confidence
- [ ] Handle various domain formats
- [ ] Filter out personal emails if needed

### [ ] 4. Implement Email Verification
- [ ] For venues with existing emails:
  - Verify email validity
  - Check deliverability score
  - Mark invalid emails for removal
  - Log verification results
- [ ] Handle verification statuses:
  - Valid
  - Invalid
  - Accept-all
  - Unknown

### [ ] 5. Create Smart Email Selection
- [ ] Implement logic to choose best email:
  - Prefer verified emails
  - Prioritize role-based emails
  - Consider confidence scores
  - Avoid personal emails for businesses
- [ ] Handle multiple email scenarios

### [ ] 6. Add Data Enrichment Pipeline
- [ ] Read existing enriched data
- [ ] Process records in batches
- [ ] Track API usage and costs
- [ ] Update CSV with new/verified emails
- [ ] Create audit trail of changes

### [ ] 7. Implement Cost Controls
- [ ] Add configurable limits:
  - Maximum verifications per run
  - Maximum searches per run
  - Cost threshold alerts
- [ ] Implement priority processing:
  - Verify high-value venues first
  - Skip low-confidence websites
- [ ] Add dry-run mode for cost estimation

### [ ] 8. Frontend Integration
- [ ] Add "Email Verification" button to UI
- [ ] Display:
  - Current email coverage
  - Verification statistics
  - API credits remaining
  - Estimated cost
- [ ] Add configuration modal:
  - API key input
  - Processing limits
  - Verification options

### [ ] 9. Create README Documentation
- [ ] Create `docs/hunter_api_setup.md`:
  ```markdown
  # Hunter API Setup Guide
  
  ## Getting Started
  1. Sign up at hunter.io
  2. Obtain API key from dashboard
  3. Choose appropriate plan
  
  ## Configuration
  - Add API key to .env file
  - Set processing limits
  - Configure verification options
  
  ## Usage
  - Cost estimates
  - Best practices
  - Troubleshooting
  ```

### [ ] 10. Add Monitoring and Reporting
- [ ] Create enrichment report:
  - Emails found
  - Emails verified
  - Invalid emails removed
  - API credits used
  - Cost breakdown
- [ ] Export detailed logs
- [ ] Generate summary statistics

## Script Structure
```python
# hunter_email_enricher.py
class HunterClient:
    def __init__(self, api_key)
    def search_domain(self, domain)
    def verify_email(self, email)
    def bulk_verify(self, emails)

class EmailEnricher:
    def __init__(self, hunter_client)
    def enrich_venue(self, venue)
    def process_batch(self, venues)
    def generate_report(self)
```

## Configuration Example
```env
# .env file
HUNTER_API_KEY=your_api_key_here
HUNTER_MAX_VERIFICATIONS=1000
HUNTER_MAX_SEARCHES=500
HUNTER_CONFIDENCE_THRESHOLD=70
```

## Success Criteria
- Working Hunter API integration
- Improved email coverage for venues
- Verified email addresses
- Cost-effective processing
- Clear documentation
- Frontend integration complete
- Comprehensive reporting