#!/usr/bin/env python3
"""
Web-based GUI for EasyJet Holiday Deal Scraper
Flask web interface for configuring and running the scraper
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import threading
import os
import pandas as pd
from datetime import datetime
import json
import time

from enhanced_easyjet_scraper import EnhancedEasyJetScraper as EasyJetScraper
from config import DEFAULT_CONFIG, AIRPORT_CODES

app = Flask(__name__)
app.secret_key = 'easyjet_scraper_secret_key'

# Global variables for scraper state
scraper_status = {
    'running': False,
    'progress': 'Ready',
    'logs': [],
    'last_result': None
}

class WebScraperLogger:
    """Custom logger that captures messages for web display"""
    def __init__(self):
        self.messages = []
    
    def info(self, message):
        self.add_message('INFO', message)
        print(f"INFO: {message}")
    
    def error(self, message):
        self.add_message('ERROR', message)
        print(f"ERROR: {message}")
    
    def warning(self, message):
        self.add_message('WARNING', message)
        print(f"WARNING: {message}")
    
    def debug(self, message):
        self.add_message('DEBUG', message)
        print(f"DEBUG: {message}")
    
    def add_message(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.messages.append(log_entry)
        scraper_status['logs'].append(log_entry)
        
        # Keep only last 100 messages
        if len(scraper_status['logs']) > 100:
            scraper_status['logs'] = scraper_status['logs'][-100:]

@app.route('/')
def index():
    """Main page with scraper interface"""
    return render_template('index.html', 
                         airports=AIRPORT_CODES,
                         default_config=DEFAULT_CONFIG)

@app.route('/start_scraper', methods=['POST'])
def start_scraper():
    """Start the scraping process"""
    if scraper_status['running']:
        return jsonify({'error': 'Scraper is already running'}), 400
    
    try:
        # Get configuration from form
        config = DEFAULT_CONFIG.copy()
        
        # Get selected airports
        selected_airports = request.form.getlist('airports')
        if not selected_airports:
            return jsonify({'error': 'Please select at least one airport'}), 400
        
        config.update({
            'departure_airports': selected_airports,
            'min_duration': int(request.form.get('min_duration', 7)),
            'max_duration': int(request.form.get('max_duration', 14)),
            'min_price': int(request.form.get('min_price', 100)),
            'price_threshold': int(request.form.get('max_price', 2000)),
            'max_deals_per_search': int(request.form.get('max_deals', 50)),
            'search_months_ahead': int(request.form.get('months_ahead', 6)),
            'sort_by_price': request.form.get('sort_by_price') == 'on',
            'output_file': request.form.get('output_file', 'easyjet_deals.csv')
        })
        
        # Validate inputs
        if config['min_duration'] >= config['max_duration']:
            return jsonify({'error': 'Max duration must be greater than min duration'}), 400
        
        if config['min_price'] >= config['price_threshold']:
            return jsonify({'error': 'Max price must be greater than min price'}), 400
        
        # Clear previous logs
        scraper_status['logs'] = []
        scraper_status['running'] = True
        scraper_status['progress'] = 'Starting...'
        
        # Start scraper in background thread
        thread = threading.Thread(target=run_scraper_background, args=(config,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Scraper started successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to start scraper: {str(e)}'}), 500

def run_scraper_background(config):
    """Run scraper in background thread"""
    try:
        scraper_status['progress'] = 'Initializing scraper...'
        
        # Create scraper with custom logger
        scraper = EasyJetScraper(config)
        
        # Replace logger with web logger
        web_logger = WebScraperLogger()
        scraper.logger = web_logger
        
        # Log configuration
        web_logger.info("=== Starting EasyJet Deal Scraper ===")
        web_logger.info(f"Airports: {', '.join(config['departure_airports'])}")
        web_logger.info(f"Duration: {config['min_duration']}-{config['max_duration']} days")
        web_logger.info(f"Price range: £{config['min_price']}-£{config['price_threshold']}")
        web_logger.info(f"Max deals: {config['max_deals_per_search']}")
        web_logger.info(f"Sort by price: {config['sort_by_price']}")
        web_logger.info(f"Output: {config['output_file']}")
        
        scraper_status['progress'] = 'Running scraper...'
        
        # Run scraper
        scraper.run_enhanced_scraping()
        
        scraper_status['progress'] = 'Completed successfully!'
        scraper_status['last_result'] = config['output_file']
        web_logger.info(f"✅ Scraping completed! Results saved to: {config['output_file']}")
        
    except Exception as e:
        scraper_status['progress'] = f'Error: {str(e)}'
        web_logger = WebScraperLogger()
        web_logger.error(f"Scraping failed: {str(e)}")
    
    finally:
        scraper_status['running'] = False

@app.route('/status')
def get_status():
    """Get current scraper status"""
    return jsonify(scraper_status)

@app.route('/stop_scraper', methods=['POST'])
def stop_scraper():
    """Stop the scraping process"""
    scraper_status['running'] = False
    scraper_status['progress'] = 'Stopped by user'
    return jsonify({'success': True, 'message': 'Scraper stopped'})

@app.route('/download_results')
def download_results():
    """Download the results CSV file"""
    if scraper_status['last_result'] and os.path.exists(scraper_status['last_result']):
        return send_file(scraper_status['last_result'], as_attachment=True)
    else:
        return jsonify({'error': 'No results file available'}), 404

@app.route('/view_results')
def view_results():
    """View results in a table"""
    if not scraper_status['last_result'] or not os.path.exists(scraper_status['last_result']):
        return render_template('no_results.html')
    
    try:
        df = pd.read_csv(scraper_status['last_result'])
        
        # Convert to HTML table
        results_html = df.to_html(classes='table table-striped table-hover', 
                                 table_id='results-table', 
                                 escape=False, 
                                 index=False)
        
        # Calculate summary stats
        total_deals = len(df)
        
        # Extract numeric prices for stats
        prices = df['total_price'].str.replace('£', '').str.replace(',', '').astype(float)
        min_price = prices.min()
        max_price = prices.max()
        avg_price = prices.mean()
        
        destinations = df['destination'].nunique()
        
        summary = {
            'total_deals': total_deals,
            'min_price': f"£{min_price:.0f}",
            'max_price': f"£{max_price:.0f}",
            'avg_price': f"£{avg_price:.0f}",
            'destinations': destinations,
            'filename': scraper_status['last_result']
        }
        
        return render_template('results.html', 
                             results_table=results_html,
                             summary=summary)
        
    except Exception as e:
        return render_template('error.html', error=f"Error loading results: {str(e)}")

# Create templates directory and files
def create_templates():
    """Create HTML templates for the web interface"""
    os.makedirs('templates', exist_ok=True)
    
    # Main index template
    index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EasyJet Holiday Deal Scraper</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .log-container { height: 300px; overflow-y: auto; background: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; }
        .log-entry { margin-bottom: 5px; font-family: monospace; font-size: 0.9em; }
        .log-info { color: #0066cc; }
        .log-error { color: #dc3545; }
        .log-warning { color: #fd7e14; }
        .log-success { color: #198754; }
        .airport-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">🛫 EasyJet Holiday Deal Scraper</h1>
                
                <form id="scraperForm">
                    <!-- Airport Selection -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>Departure Airports</h5>
                        </div>
                        <div class="card-body">
                            <div class="airport-grid">
                                {% for airport, code in airports.items() %}
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="airports" value="{{ airport }}" 
                                           id="airport_{{ loop.index }}" {% if airport == 'Bristol' %}checked{% endif %}>
                                    <label class="form-check-label" for="airport_{{ loop.index }}">
                                        {{ airport }} ({{ code }})
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Configuration -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>Search Configuration</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="form-label">Min Duration (days)</label>
                                    <input type="number" class="form-control" name="min_duration" value="7" min="1" max="30">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Max Duration (days)</label>
                                    <input type="number" class="form-control" name="max_duration" value="14" min="1" max="30">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Min Price (£)</label>
                                    <input type="number" class="form-control" name="min_price" value="100" min="50" max="5000">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Max Price (£)</label>
                                    <input type="number" class="form-control" name="max_price" value="2000" min="100" max="10000">
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-md-4">
                                    <label class="form-label">Max Deals per Search</label>
                                    <input type="number" class="form-control" name="max_deals" value="50" min="10" max="200">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Months Ahead</label>
                                    <input type="number" class="form-control" name="months_ahead" value="6" min="1" max="12">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Output File</label>
                                    <input type="text" class="form-control" name="output_file" value="easyjet_deals.csv">
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="sort_by_price" checked>
                                        <label class="form-check-label">Sort by lowest price first</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Control Buttons -->
                    <div class="text-center mb-4">
                        <button type="submit" class="btn btn-primary btn-lg me-3" id="startBtn">
                            🚀 Start Scraping
                        </button>
                        <button type="button" class="btn btn-danger me-3" id="stopBtn" disabled>
                            ⏹️ Stop
                        </button>
                        <a href="/view_results" class="btn btn-success me-3">
                            📊 View Results
                        </a>
                        <button type="button" class="btn btn-secondary" id="clearLogBtn">
                            🗑️ Clear Log
                        </button>
                    </div>
                </form>
                
                <!-- Status -->
                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>Status</h5>
                        <span id="statusBadge" class="badge bg-secondary">Ready</span>
                    </div>
                    <div class="card-body">
                        <div class="progress mb-3">
                            <div class="progress-bar" id="progressBar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <p id="statusText">Ready to start scraping</p>
                    </div>
                </div>
                
                <!-- Log Output -->
                <div class="card">
                    <div class="card-header">
                        <h5>Log Output</h5>
                    </div>
                    <div class="card-body">
                        <div id="logContainer" class="log-container"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let statusInterval;
        
        document.getElementById('scraperForm').addEventListener('submit', function(e) {
            e.preventDefault();
            startScraper();
        });
        
        document.getElementById('stopBtn').addEventListener('click', stopScraper);
        document.getElementById('clearLogBtn').addEventListener('click', clearLog);
        
        function startScraper() {
            const formData = new FormData(document.getElementById('scraperForm'));
            
            fetch('/start_scraper', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    startStatusUpdates();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error starting scraper: ' + error);
            });
        }
        
        function stopScraper() {
            fetch('/stop_scraper', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                stopStatusUpdates();
            });
        }
        
        function startStatusUpdates() {
            statusInterval = setInterval(updateStatus, 1000);
        }
        
        function stopStatusUpdates() {
            if (statusInterval) {
                clearInterval(statusInterval);
            }
        }
        
        function updateStatus() {
            fetch('/status')
            .then(response => response.json())
            .then(data => {
                // Update status text
                document.getElementById('statusText').textContent = data.progress;
                
                // Update status badge
                const badge = document.getElementById('statusBadge');
                if (data.running) {
                    badge.className = 'badge bg-primary';
                    badge.textContent = 'Running';
                    document.getElementById('progressBar').style.width = '100%';
                    document.getElementById('progressBar').className = 'progress-bar progress-bar-striped progress-bar-animated';
                } else {
                    badge.className = 'badge bg-secondary';
                    badge.textContent = 'Ready';
                    document.getElementById('progressBar').style.width = '0%';
                    document.getElementById('progressBar').className = 'progress-bar';
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    stopStatusUpdates();
                }
                
                // Update logs
                const logContainer = document.getElementById('logContainer');
                logContainer.innerHTML = '';
                data.logs.forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.className = `log-entry log-${log.level.toLowerCase()}`;
                    logEntry.textContent = `[${log.timestamp}] ${log.level}: ${log.message}`;
                    logContainer.appendChild(logEntry);
                });
                
                // Auto-scroll to bottom
                logContainer.scrollTop = logContainer.scrollHeight;
            });
        }
        
        function clearLog() {
            document.getElementById('logContainer').innerHTML = '';
        }
        
        // Start status updates on page load
        updateStatus();
    </script>
</body>
</html>
    '''
    
    # Results template
    results_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scraper Results - EasyJet Deal Scraper</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">📊 Scraping Results</h1>
                
                <!-- Summary Cards -->
                <div class="row mb-4">
                    <div class="col-md-2">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5 class="card-title">{{ summary.total_deals }}</h5>
                                <p class="card-text">Total Deals</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5 class="card-title">{{ summary.min_price }}</h5>
                                <p class="card-text">Lowest Price</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5 class="card-title">{{ summary.max_price }}</h5>
                                <p class="card-text">Highest Price</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5 class="card-title">{{ summary.avg_price }}</h5>
                                <p class="card-text">Average Price</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5 class="card-title">{{ summary.destinations }}</h5>
                                <p class="card-text">Destinations</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="card text-center">
                            <div class="card-body">
                                <a href="/download_results" class="btn btn-success btn-sm">📥 Download CSV</a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Navigation -->
                <div class="mb-3">
                    <a href="/" class="btn btn-primary">← Back to Scraper</a>
                    <a href="/download_results" class="btn btn-success">📥 Download CSV</a>
                </div>
                
                <!-- Results Table -->
                <div class="card">
                    <div class="card-header">
                        <h5>Holiday Deals ({{ summary.filename }})</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            {{ results_table|safe }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#results-table').DataTable({
                "pageLength": 25,
                "order": [[ 8, "asc" ]], // Sort by total_price column
                "columnDefs": [
                    { "width": "15%", "targets": 1 }, // destination
                    { "width": "10%", "targets": 8 }, // total_price
                    { "width": "10%", "targets": 9 }  // price_per_person
                ]
            });
        });
    </script>
</body>
</html>
    '''
    
    # No results template
    no_results_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>No Results - EasyJet Deal Scraper</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-6 text-center">
                <h1>📭 No Results Available</h1>
                <p class="lead">No scraping results found. Please run the scraper first.</p>
                <a href="/" class="btn btn-primary">← Back to Scraper</a>
            </div>
        </div>
    </div>
</body>
</html>
    '''
    
    # Error template
    error_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - EasyJet Deal Scraper</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-6 text-center">
                <h1>❌ Error</h1>
                <div class="alert alert-danger">{{ error }}</div>
                <a href="/" class="btn btn-primary">← Back to Scraper</a>
            </div>
        </div>
    </div>
</body>
</html>
    '''
    
    # Write templates to files
    with open('templates/index.html', 'w') as f:
        f.write(index_html)
    
    with open('templates/results.html', 'w') as f:
        f.write(results_html)
    
    with open('templates/no_results.html', 'w') as f:
        f.write(no_results_html)
    
    with open('templates/error.html', 'w') as f:
        f.write(error_html)

if __name__ == '__main__':
    # Create templates
    create_templates()
    
    print("🚀 Starting EasyJet Deal Scraper Web GUI...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8000, debug=False)
