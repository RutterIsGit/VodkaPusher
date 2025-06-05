# VodkaPusher
Repository for the PubScraper project.

## Google Programmable Search Enrichment

The script `google_website_enricher.py` can fill missing `website` fields in
`essex_licensed_venues.csv` using the Google Programmable Search JSON API. Set
the environment variables `GOOGLE_API_KEY` and `GOOGLE_CX` with your API key and
search engine ID before running the module directly:

```bash
export GOOGLE_API_KEY=your-api-key
export GOOGLE_CX=your-search-engine-id
python google_website_enricher.py
```

Both variables can also be set when running `build_essex.py` to enable Google
enrichment as part of the build process.
