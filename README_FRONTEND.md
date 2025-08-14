# Essex Pub Data Enricher - Frontend

## Quick Start

1. Install dependencies:
```bash
pip install flask flask-cors
```

2. Run the Flask application:
```bash
python3 app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Features

- **Seed Data Generation**: Click "Run Update" to generate/update the base venue data
- **Google Enrichment**: Choose between enriching missing data only or refreshing all records
- **Contact Scraping**: Extract contact information from venue websites using BrightData
- **Email Verification**: Placeholder for Hunter API integration (Task 6)
- **File Management**: Download generated CSV files directly from the interface

## API Endpoints

- `POST /api/seed-data` - Run seed data generation
- `POST /api/google-enrich` - Run Google enrichment
- `POST /api/scrape-contacts` - Run contact scraping
- `POST /api/verify-emails` - Run email verification (placeholder)
- `GET /api/status/<task_id>` - Check task status
- `GET /api/files` - List available CSV files
- `GET /api/download/<filename>` - Download a CSV file

## Project Structure

```
app.py                  # Flask application
templates/
  └── index.html       # Main UI template  
static/
  ├── css/
  │   └── style.css   # Custom styles
  └── js/
      └── app.js      # Frontend JavaScript
```

## Notes

- Tasks run asynchronously in background threads
- Progress is tracked via polling (1-second intervals)
- All generated CSV files are available for download
- The interface automatically refreshes the file list every 30 seconds