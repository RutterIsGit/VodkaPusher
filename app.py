from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import subprocess
import threading
import uuid
import os
import json
from datetime import datetime
import csv

app = Flask(__name__)
CORS(app)

tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/seed-data', methods=['POST'])
def seed_data():
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'running', 'progress': 0, 'message': 'Starting seed data generation...'}
    
    def run_task():
        try:
            tasks[task_id]['message'] = 'Running build_essex.py...'
            result = subprocess.run(['python', 'build_essex.py'], 
                                    capture_output=True, text=True)
            if result.returncode == 0:
                tasks[task_id]['status'] = 'completed'
                tasks[task_id]['progress'] = 100
                tasks[task_id]['message'] = 'Seed data generation completed'
                
                if os.path.exists('essex_licensed_venues.csv'):
                    with open('essex_licensed_venues.csv', 'r') as f:
                        reader = csv.reader(f)
                        row_count = sum(1 for row in reader) - 1
                        tasks[task_id]['records'] = row_count
            else:
                tasks[task_id]['status'] = 'failed'
                tasks[task_id]['message'] = f'Error: {result.stderr}'
        except Exception as e:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['message'] = str(e)
    
    thread = threading.Thread(target=run_task)
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/google-enrich', methods=['POST'])
def google_enrich():
    mode = request.json.get('mode', 'missing')
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'running', 'progress': 0, 'message': 'Starting Google enrichment...'}
    
    def run_task():
        try:
            tasks[task_id]['message'] = 'Running google_website_enricher.py...'
            cmd = ['python', 'google_website_enricher.py']
            if mode == 'all':
                cmd.append('--refresh-all')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                tasks[task_id]['status'] = 'completed'
                tasks[task_id]['progress'] = 100
                tasks[task_id]['message'] = 'Google enrichment completed'
            else:
                tasks[task_id]['status'] = 'failed'
                tasks[task_id]['message'] = f'Error: {result.stderr}'
        except Exception as e:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['message'] = str(e)
    
    thread = threading.Thread(target=run_task)
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/scrape-contacts', methods=['POST'])
def scrape_contacts():
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'running', 'progress': 0, 'message': 'Starting contact scraping...'}
    
    def run_task():
        try:
            tasks[task_id]['message'] = 'Running venue_contact_enricher_unified.py...'
            result = subprocess.run(['python', 'venue_contact_enricher_unified.py'], 
                                    capture_output=True, text=True)
            
            if result.returncode == 0:
                tasks[task_id]['status'] = 'completed'
                tasks[task_id]['progress'] = 100
                tasks[task_id]['message'] = 'Contact scraping completed'
            else:
                tasks[task_id]['status'] = 'failed'
                tasks[task_id]['message'] = f'Error: {result.stderr}'
        except Exception as e:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['message'] = str(e)
    
    thread = threading.Thread(target=run_task)
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/verify-emails', methods=['POST'])
def verify_emails():
    dry_run = request.json.get('dry_run', False)
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'running', 'progress': 0, 'message': 'Starting email verification...'}
    
    def run_task():
        try:
            tasks[task_id]['message'] = 'Running hunter_email_enricher.py...'
            
            env = os.environ.copy()
            if dry_run:
                env['HUNTER_DRY_RUN'] = 'true'
                tasks[task_id]['message'] = 'Running in dry-run mode (sample only)...'
            
            result = subprocess.run(['python', 'hunter_email_enricher.py'], 
                                    capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                tasks[task_id]['status'] = 'completed'
                tasks[task_id]['progress'] = 100
                tasks[task_id]['message'] = 'Email verification completed'
                
                if os.path.exists('hunter_enrichment_report.json'):
                    with open('hunter_enrichment_report.json', 'r') as f:
                        report = json.load(f)
                        tasks[task_id]['report'] = report
            else:
                tasks[task_id]['status'] = 'failed'
                tasks[task_id]['message'] = f'Error: {result.stderr}'
        except Exception as e:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['message'] = str(e)
    
    thread = threading.Thread(target=run_task)
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/status/<task_id>')
def get_status(task_id):
    if task_id in tasks:
        return jsonify(tasks[task_id])
    return jsonify({'status': 'not_found'}), 404

@app.route('/api/files')
def list_files():
    files = []
    csv_files = [
        'essex_licensed_venues.csv',
        'essex_venues_google.csv',
        'essex_venues_enriched.csv',
        'essex_venues_hunter_enriched.csv'
    ]
    
    for filename in csv_files:
        if os.path.exists(filename):
            stat = os.stat(filename)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    return jsonify(files)

@app.route('/api/download/<filename>')
def download_file(filename):
    allowed_files = ['essex_licensed_venues.csv', 'essex_venues_google.csv', 'essex_venues_enriched.csv', 'essex_venues_hunter_enriched.csv']
    if filename in allowed_files and os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    app.run(debug=True, port=5001)