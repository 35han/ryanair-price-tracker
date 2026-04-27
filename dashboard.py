"""
Flask web dashboard for price tracking
Simple web interface to view price history and trends
"""

import logging
from flask import Flask, render_template_string, jsonify
from datetime import datetime, timedelta
from database import get_lowest_price, get_all_prices
from exporter import PriceExporter
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, PRICE_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
exporter = PriceExporter()

# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>✈️ Ryanair Price Tracker Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        header p {
            color: #666;
            font-size: 14px;
        }
        
        .route-info {
            display: flex;
            gap: 30px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .info-item {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .info-item strong {
            color: #667eea;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }
        
        .stat-subtext {
            color: #999;
            font-size: 12px;
            margin-top: 5px;
        }
        
        .good-deal {
            border-left-color: #27ae60;
        }
        
        .good-deal .stat-value {
            color: #27ae60;
        }
        
        .chart-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .chart-section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
        }
        
        canvas {
            max-height: 400px;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #764ba2;
        }
        
        .btn-secondary {
            background: #95a5a6;
        }
        
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        
        .alerts {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .alerts h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .alert-item {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border-left: 4px solid #17a2b8;
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            font-size: 12px;
        }
        
        .refresh-time {
            color: #999;
            font-size: 12px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✈️ Ryanair Price Tracker</h1>
            <p>Real-time flight price monitoring dashboard</p>
            <div class="route-info">
                <div class="info-item">
                    <strong>Route:</strong> {{ route }}
                </div>
                <div class="info-item">
                    <strong>Alert Threshold:</strong> €{{ threshold }}
                </div>
                <div class="info-item">
                    <strong>Tracking Since:</strong> {{ since }}
                </div>
            </div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card {% if stats.lowest_price < threshold %}good-deal{% endif %}">
                <h3>💰 Lowest Price</h3>
                <div class="stat-value">€{{ "%.2f"|format(stats.lowest_price) }}</div>
                <div class="stat-subtext">30-day minimum</div>
            </div>
            
            <div class="stat-card">
                <h3>💸 Highest Price</h3>
                <div class="stat-value">€{{ "%.2f"|format(stats.highest_price) }}</div>
                <div class="stat-subtext">30-day maximum</div>
            </div>
            
            <div class="stat-card">
                <h3>📈 Average Price</h3>
                <div class="stat-value">€{{ "%.2f"|format(stats.average_price) }}</div>
                <div class="stat-subtext">{{ stats.total_checks }} checks</div>
            </div>
            
            <div class="stat-card">
                <h3>📊 Price Range</h3>
                <div class="stat-value">€{{ "%.2f"|format(stats.price_range) }}</div>
                <div class="stat-subtext">High - Low</div>
            </div>
        </div>
        
        <div class="alerts">
            <h2>📋 Status</h2>
            <div class="alert-success">
                ✅ Bot is running and monitoring prices every hour
            </div>
            <div class="alert-info">
                📊 Database contains {{ stats.total_checks }} price records
            </div>
            <div class="alert-info">
                🔔 You will be notified when prices drop below €{{ threshold }}
            </div>
            <div class="refresh-time">
                Last updated: {{ updated_at }}
            </div>
        </div>
        
        <div class="actions">
            <button class="btn" onclick="location.href='/api/export/csv'">
                📥 Download CSV
            </button>
            <button class="btn" onclick="location.href='/api/export/json'">
                📥 Download JSON
            </button>
            <button class="btn btn-secondary" onclick="location.reload()">
                🔄 Refresh
            </button>
        </div>
        
        <footer>
            <p>🤖 Ryanair Price Tracker Bot | Running 24/7 on Railway</p>
            <p>Made with ❤️ for budget travelers</p>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        stats = exporter.get_statistics(30)
        
        if not stats:
            stats = {
                'lowest_price': 0,
                'highest_price': 0,
                'average_price': 0,
                'price_range': 0,
                'total_checks': 0
            }
        
        return render_template_string(
            DASHBOARD_HTML,
            route=f"{DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}",
            threshold=PRICE_THRESHOLD,
            stats=stats,
            since="2026-04-27",
            updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"Error loading dashboard: {e}", 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        stats = exporter.get_statistics(30)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/prices')
def api_prices():
    """API endpoint for all prices"""
    try:
        prices = get_all_prices()
        return jsonify({
            "count": len(prices),
            "prices": [
                {
                    "price": p[3],
                    "date": p[5],
                    "checked_at": p[6]
                }
                for p in prices[-30:]  # Last 30 records
            ]
        })
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/csv')
def export_csv():
    """Export to CSV"""
    try:
        csv_file = exporter.export_to_csv(days=30)
        if csv_file:
            return f"CSV exported successfully: {csv_file}"
        return "No data to export", 404
    except Exception as e:
        logger.error(f"Export error: {e}")
        return f"Export error: {e}", 500

@app.route('/api/export/json')
def export_json():
    """Export to JSON"""
    try:
        json_file = exporter.export_to_json(days=30)
        if json_file:
            return f"JSON exported successfully: {json_file}"
        return "No data to export", 404
    except Exception as e:
        logger.error(f"Export error: {e}")
        return f"Export error: {e}", 500

def start_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Start the Flask dashboard"""
    logger.info(f"Starting dashboard on http://localhost:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    logger.info("Starting Ryanair Price Tracker Dashboard...")
    start_dashboard(debug=True)
