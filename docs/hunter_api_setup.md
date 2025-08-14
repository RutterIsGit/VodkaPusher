# Hunter API Setup Guide

## Overview
Hunter.io is a service for finding and verifying professional email addresses. This guide covers setup and integration for the PubScraper project.

## Getting Started

### 1. Create Hunter Account
1. Visit [hunter.io](https://hunter.io)
2. Sign up for an account
3. Choose a plan based on your needs:
   - **Free**: 25 searches/month (good for testing)
   - **Starter**: $49/month for 1,000 searches
   - **Growth**: $99/month for 5,000 searches
   - **Pro**: $199/month for 20,000 searches

### 2. Obtain API Key
1. Log into Hunter dashboard
2. Navigate to API section
3. Copy your API key
4. Keep it secure - don't commit to version control

### 3. Configure Environment
Add to your `.env` file:
```bash
# Hunter API Configuration
HUNTER_API_KEY=your_api_key_here

# Optional: Set limits to control costs
HUNTER_MAX_VERIFICATIONS=1000
HUNTER_MAX_SEARCHES=500
HUNTER_CONFIDENCE_THRESHOLD=70
```

## API Endpoints

### Domain Search
Find email addresses associated with a domain:
```
GET https://api.hunter.io/v2/domain-search?domain=example.com&api_key=xxx
```

Returns:
- List of email addresses
- Confidence scores
- Sources where found
- Pattern detection

### Email Verifier
Verify if an email address is deliverable:
```
GET https://api.hunter.io/v2/email-verifier?email=test@example.com&api_key=xxx
```

Returns:
- Status: valid, invalid, accept_all, unknown
- Score: 0-100 deliverability confidence
- Additional checks results

## Integration Best Practices

### 1. Rate Limiting
- Free plan: 50 requests/month
- Paid plans: 60 requests/minute
- Implement delays between requests
- Use exponential backoff for retries

### 2. Cost Optimization
- Verify only high-confidence domains
- Skip generic domains (gmail.com, etc.)
- Cache results to avoid duplicate calls
- Use bulk operations where available

### 3. Data Quality
- Prefer role-based emails (info@, contact@)
- Higher confidence scores = better quality
- Verify before using in production
- Remove bounced emails from lists

## Usage in PubScraper

### Running Email Enrichment
```bash
python hunter_email_enricher.py
```

### Options
- `--dry-run`: Estimate costs without making API calls
- `--limit N`: Process only N venues
- `--verify-only`: Only verify existing emails
- `--search-only`: Only search for new emails

### Output
The script updates your CSV with:
- New email addresses found
- Verification status for existing emails
- Confidence scores
- Source information

## Monitoring Usage

### Check API Credits
```python
# In your code
response = requests.get(
    'https://api.hunter.io/v2/account',
    params={'api_key': api_key}
)
credits_left = response.json()['data']['requests']['searches']['available']
```

### Cost Tracking
The enricher logs:
- API calls made
- Credits consumed
- Estimated cost
- Success/failure rates

## Troubleshooting

### Common Issues

1. **"API key invalid"**
   - Check API key in .env file
   - Ensure no extra spaces
   - Verify key in Hunter dashboard

2. **"Rate limit exceeded"**
   - Add delays between requests
   - Check your plan limits
   - Upgrade plan if needed

3. **"No emails found"**
   - Domain might be too small
   - Try without www prefix
   - Check if domain is active

4. **"Verification failed"**
   - Email might not exist
   - Server might block verification
   - Try again later

### Debug Mode
Enable verbose logging:
```bash
export HUNTER_DEBUG=true
python hunter_email_enricher.py
```

## Security Considerations

1. **Never commit API keys**
   - Use .env files
   - Add .env to .gitignore
   - Use environment variables in production

2. **Respect Privacy**
   - Only collect business emails
   - Don't harvest personal emails
   - Comply with GDPR/privacy laws

3. **Secure Storage**
   - Encrypt sensitive data
   - Limit access to email lists
   - Regular security audits

## Support
- Hunter Documentation: https://hunter.io/api-documentation
- Support: support@hunter.io
- Status Page: https://status.hunter.io/