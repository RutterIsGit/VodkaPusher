let activeTaskIds = {};

async function runSeedData() {
    const btn = document.getElementById('btn-seed');
    btn.disabled = true;
    
    const response = await fetch('/api/seed-data', { method: 'POST' });
    const data = await response.json();
    
    activeTaskIds['seed'] = data.task_id;
    monitorTask('seed', data.task_id);
}

async function runGoogleEnrich() {
    const btn = document.getElementById('btn-google');
    btn.disabled = true;
    
    const mode = document.querySelector('input[name="enrichMode"]:checked').value;
    
    const response = await fetch('/api/google-enrich', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode })
    });
    const data = await response.json();
    
    activeTaskIds['google'] = data.task_id;
    monitorTask('google', data.task_id);
}

async function runScrapeContacts() {
    const btn = document.getElementById('btn-scrape');
    btn.disabled = true;
    
    const response = await fetch('/api/scrape-contacts', { method: 'POST' });
    const data = await response.json();
    
    activeTaskIds['scrape'] = data.task_id;
    monitorTask('scrape', data.task_id);
}

async function runVerifyEmails() {
    const btn = document.getElementById('btn-verify');
    btn.disabled = true;
    
    const dryRun = document.getElementById('dryRun').checked;
    
    const response = await fetch('/api/verify-emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dry_run: dryRun })
    });
    const data = await response.json();
    
    activeTaskIds['verify'] = data.task_id;
    monitorTask('verify', data.task_id);
}

function showHunterConfig() {
    alert('Please add HUNTER_API_KEY to your .env file.\n\nSign up at hunter.io to get your API key.\n\nConfiguration options:\n- HUNTER_MAX_VERIFICATIONS (default: 1000)\n- HUNTER_MAX_SEARCHES (default: 500)\n- HUNTER_CONFIDENCE_THRESHOLD (default: 70)');
}

async function monitorTask(taskType, taskId) {
    const statusEl = document.getElementById(`${taskType}-status`);
    const messageEl = document.getElementById(`${taskType}-message`);
    const progressBar = document.getElementById(`${taskType}-progress-bar`);
    const progressBarInner = progressBar?.querySelector('.progress-bar');
    const btn = document.getElementById(`btn-${taskType}`);
    
    if (progressBar) {
        progressBar.style.display = 'block';
    }
    
    const interval = setInterval(async () => {
        const response = await fetch(`/api/status/${taskId}`);
        const data = await response.json();
        
        if (data.status === 'running') {
            statusEl.className = 'badge bg-info';
            statusEl.textContent = 'Running';
            messageEl.textContent = data.message || 'Processing...';
            if (progressBarInner) {
                progressBarInner.style.width = `${data.progress || 0}%`;
            }
        } else if (data.status === 'completed') {
            statusEl.className = 'badge bg-success';
            statusEl.textContent = 'Completed';
            messageEl.textContent = data.message || 'Task completed successfully';
            if (progressBarInner) {
                progressBarInner.style.width = '100%';
            }
            if (taskType === 'seed' && data.records) {
                document.getElementById('seed-records').textContent = data.records;
            }
            if (taskType === 'verify' && data.report) {
                const report = data.report;
                document.getElementById('verify-report').style.display = 'block';
                document.getElementById('emails-found').textContent = report.summary.emails_found || 0;
                document.getElementById('emails-verified').textContent = report.summary.emails_verified || 0;
                document.getElementById('invalid-emails').textContent = report.summary.invalid_emails || 0;
                document.getElementById('credits-used').textContent = report.summary.credits_used || 0;
            }
            clearInterval(interval);
            btn.disabled = false;
            setTimeout(() => {
                if (progressBar) {
                    progressBar.style.display = 'none';
                    progressBarInner.style.width = '0%';
                }
            }, 2000);
            loadFiles();
        } else if (data.status === 'failed') {
            statusEl.className = 'badge bg-danger';
            statusEl.textContent = 'Failed';
            messageEl.textContent = data.message || 'Task failed';
            clearInterval(interval);
            btn.disabled = false;
            if (progressBar) {
                progressBar.style.display = 'none';
            }
        }
    }, 1000);
}

async function loadFiles() {
    const response = await fetch('/api/files');
    const files = await response.json();
    
    const fileList = document.getElementById('file-list');
    
    if (files.length === 0) {
        fileList.innerHTML = '<p class="text-muted">No data files found</p>';
        return;
    }
    
    fileList.innerHTML = files.map(file => {
        const sizeKB = (file.size / 1024).toFixed(2);
        const date = new Date(file.modified).toLocaleString();
        return `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <strong>${file.name}</strong>
                    <small class="text-muted d-block">
                        ${sizeKB} KB - Modified: ${date}
                    </small>
                </div>
                <a href="/api/download/${file.name}" class="btn btn-sm btn-outline-primary">
                    Download
                </a>
            </div>
        `;
    }).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
    setInterval(loadFiles, 30000);
});