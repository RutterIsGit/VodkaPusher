# Task 4: Build a Simple Frontend

## Objective
Create a basic user interface with buttons for each step in the workflow, providing an easy way to run the data enrichment pipeline.

## Frontend Requirements
1. **"Seed Data" button** - Runs seed data generation/update
2. **"Google Enrichment" button** - With options for partial or full enrichment
3. **"Scrape Contacts" button** - Initiates BrightData contact enrichment
4. **"Email Verification" button** - Runs Hunter API enrichment (from Task 6)

## Implementation Plan

### [x] 1. Choose Frontend Technology
- [x] Use Flask for simplicity and Python integration
- [x] Create single-page application with AJAX for async operations
- [x] Use Bootstrap for basic styling
- [x] Implement progress indicators for long-running tasks

### [x] 2. Create Project Structure
```
PubScraper/
├── app.py                  # Flask application
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── app.js         # Frontend JavaScript
├── templates/
│   └── index.html         # Main UI template
└── api/
    └── routes.py          # API endpoints
```

### [x] 3. Implement Flask Backend
- [x] Create Flask app with necessary routes:
  - `/` - Main interface
  - `/api/seed-data` - Run build_essex.py
  - `/api/google-enrich` - Run google_website_enricher.py
  - `/api/scrape-contacts` - Run venue_contact_enricher_unified.py
  - `/api/verify-emails` - Run Hunter API enrichment (placeholder)
  - `/api/status/<task_id>` - Check task status
  - `/api/download/<filename>` - Download result files
  - `/api/files` - List available CSV files

### [x] 4. Implement Task Queue
- [x] Use threading for async task execution
- [x] Create task wrappers for each script
- [x] Implement progress tracking
- [x] Store task results and status

### [x] 5. Create UI Components
- [x] Main dashboard with workflow steps
- [x] Seed Data section:
  - Run button
  - Status indicator
  - Record count display
- [x] Google Enrichment section:
  - Radio buttons for enrichment mode
  - Run button
  - Progress bar
  - Statistics display
- [x] Contact Scraping section:
  - Run button
  - Progress indicator
  - Success/failure counts
- [x] Email Verification section:
  - Run button
  - Verification statistics (placeholder)

### [x] 6. Implement Progress Tracking
- [x] Add basic progress tracking with polling
- [x] Display:
  - Current task status
  - Progress percentage
  - Status messages
  - Task completion state

### [x] 7. Add File Management
- [x] Display current data files
- [x] Show last modified times
- [x] Provide download links for CSVs
- [ ] Add file backup functionality (optional)

### [ ] 8. Implement Error Handling
- [ ] Graceful error display in UI
- [ ] Log viewer for debugging
- [ ] Retry failed operations
- [ ] Export error reports

### [ ] 9. Add Configuration Panel
- [ ] API key management (secure storage)
- [ ] Filter configuration UI
- [ ] Rate limit settings
- [ ] Output preferences

### [ ] 10. Create Docker Setup (Optional)
- [ ] Dockerfile for easy deployment
- [ ] docker-compose.yml with dependencies
- [ ] Environment variable configuration
- [ ] Volume mapping for data persistence

## UI Mockup
```
┌─────────────────────────────────────────────┐
│           Essex Pub Data Enricher            │
├─────────────────────────────────────────────┤
│                                             │
│  1. Seed Data Generation                    │
│  ┌─────────────┐  Status: ✓ Complete       │
│  │ Run Update  │  Records: 1,247           │
│  └─────────────┘  Last run: 2 hours ago    │
│                                             │
│  2. Google Website Enrichment               │
│  ○ Enrich missing only                     │
│  ● Refresh all records                     │
│  ┌─────────────┐  Progress: ████░░ 78%    │
│  │     Run     │  Found: 934/1,200        │
│  └─────────────┘                           │
│                                             │
│  3. Contact Information Scraping            │
│  ┌─────────────┐  Status: Ready           │
│  │     Run     │  Emails: 0               │
│  └─────────────┘  Phones: 0               │
│                                             │
│  4. Email Verification (Hunter)             │
│  ┌─────────────┐  Status: Not configured  │
│  │     Run     │  [Configure API Key]     │
│  └─────────────┘                           │
│                                             │
│  Downloads: [seed.csv] [enriched.csv]      │
└─────────────────────────────────────────────┘
```

## Success Criteria
- All pipeline steps accessible via UI
- Real-time progress tracking
- Error handling and recovery
- File download capability
- Clean, intuitive interface
- Responsive design
- Proper security for API keys