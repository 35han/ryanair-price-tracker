# Phase 5: Dashboard & Export - Complete! ✅

## What We Built

### Files Created (3 new files):

1. **exporter.py** - Export functionality
   - CSV export (for Excel, spreadsheets)
   - JSON export (for APIs, data analysis)
   - Statistics calculation
   - File management

2. **dashboard.py** - Flask web dashboard
   - Beautiful web interface
   - Real-time statistics
   - Download CSV/JSON
   - API endpoints
   - Responsive design

3. **test_phase5.py** - Comprehensive testing
   - ✅ TESTED AND WORKING
   - Tests all export features
   - Tests API simulation
   - Usage guide included

---

## System Capabilities

```
Database (prices.db)
        ↓
    Exporter
    ├─ CSV Export → Excel/Spreadsheets
    ├─ JSON Export → APIs/Tools
    ├─ Statistics → Analysis
    └─ File Management
        ↓
    Dashboard (Flask)
    ├─ Web UI (http://localhost:5000)
    ├─ API Endpoints
    ├─ Download CSV/JSON
    └─ Real-time stats
```

---

## Test Results ✅

```
📊 Test 1: Statistics
   ✅ Lowest price: €31.03
   ✅ Highest price: €48.00
   ✅ Average price: €37.41
   ✅ Price range: €16.97
   ✅ Total checks: 9

📄 Test 2: CSV Export
   ✅ File: exports/test_export.csv
   ✅ Size: 0.6KB
   ✅ Records: 9

📄 Test 3: JSON Export
   ✅ File: exports/test_export.json
   ✅ Size: 2.6KB
   ✅ Records: 9

🌐 Test 4: Dashboard API
   ✅ 9 price records available
   ✅ Statistics: 9 checks, avg €37.41

📁 Test 5: Export Listing
   ✅ 4 exported files found

✅ ALL TESTS PASSED!
```

---

## Features

### Export Module

**CSV Export:**
```
ID,Departure,Arrival,Price (€),Currency,Flight Date,Checked At,URL
1,TLL,NUE,45.50,EUR,2026-05-10,2026-04-27 11:21:18,N/A
2,TLL,NUE,48.00,EUR,2026-05-10,2026-04-27 11:21:18,N/A
...
```

**JSON Export:**
```json
{
  "export_info": {
    "exported_at": "2026-04-27T14:33:25",
    "route": "TLL → NUE",
    "records": 9
  },
  "statistics": {
    "lowest_price": 31.03,
    "highest_price": 48.00,
    "average_price": 37.41,
    "total_checks": 9
  },
  "prices": [...]
}
```

**Statistics:**
```python
{
  "lowest_price": 31.03,
  "highest_price": 48.00,
  "average_price": 37.41,
  "price_range": 16.97,
  "total_checks": 9
}
```

---

## Dashboard Features

### Web Interface
- 🎨 Beautiful, responsive design
- 📊 Real-time statistics
- 📈 4-card stat display
- 📋 Status alerts
- 📥 CSV/JSON download buttons

### API Endpoints

```
GET  /                 - Main dashboard
GET  /api/stats        - JSON statistics
GET  /api/prices       - Price history (JSON)
GET  /api/export/csv   - Download CSV file
GET  /api/export/json  - Download JSON file
```

---

## How to Use

### 1. Generate Statistics
```python
from exporter import PriceExporter

exporter = PriceExporter()
stats = exporter.get_statistics(30)

print(f"Lowest: €{stats['lowest_price']}")
print(f"Average: €{stats['average_price']}")
```

### 2. Export to CSV
```python
csv_file = exporter.export_to_csv(days=30)
# File saved to: exports/prices_YYYYMMDD_HHMMSS.csv
```

### 3. Export to JSON
```python
json_file = exporter.export_to_json(days=30)
# File saved to: exports/prices_YYYYMMDD_HHMMSS.json
```

### 4. Start Dashboard
```bash
cd ~/ryanair-price-tracker
source venv/bin/activate
python dashboard.py
```

Then open: **http://localhost:5000**

### 5. Use Dashboard API
```bash
# Get statistics
curl http://localhost:5000/api/stats

# Get prices
curl http://localhost:5000/api/prices

# Download CSV
curl http://localhost:5000/api/export/csv -o prices.csv

# Download JSON
curl http://localhost:5000/api/export/json -o prices.json
```

---

## Integration with Bot

### Add to Scheduler
Edit `scheduler.py` to add auto-export after each job:

```python
from exporter import PriceExporter

def price_check_job(self):
    # ... existing code ...
    
    # Auto-export
    exporter = PriceExporter()
    exporter.export_to_csv()
    exporter.export_to_json()
```

### Add Dashboard to Main
Edit `main.py` to offer dashboard option:

```python
if __name__ == "__main__":
    print("1. Run scheduler (automatic price checks)")
    print("2. Start dashboard (view statistics)")
    
    choice = input("Select: ")
    if choice == "1":
        main()
    else:
        from dashboard import start_dashboard
        start_dashboard()
```

---

## Dashboard Screenshots (Text-based)

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       ✈️  Ryanair Price Tracker Dashboard                ║
║       Real-time flight price monitoring                  ║
║                                                           ║
║  Route: TLL → NUE                                         ║
║  Alert Threshold: €50                                    ║
║  Tracking Since: 2026-04-27                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
│ 💰 Lowest Price      │ €31.03                           │
│ 30-day minimum       │                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 💸 Highest Price     │ €48.00                           │
│ 30-day maximum       │                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📈 Average Price     │ €37.41                           │
│ 9 checks             │                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📊 Price Range       │ €16.97                           │
│ High - Low           │                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Status:                                                  │
│ ✅ Bot running and monitoring prices every hour         │
│ 📊 Database contains 9 price records                    │
│ 🔔 Alert threshold: €50.00                              │
│ Last updated: 2026-04-27 14:33:25                      │
└─────────────────────────────────────────────────────────┘

[📥 Download CSV] [📥 Download JSON] [🔄 Refresh]
```

---

## File Structure

```
ryanair-price-tracker/
├── exporter.py          ← CSV/JSON export
├── dashboard.py         ← Flask web interface
├── test_phase5.py       ← Phase 5 tests
├── exports/             ← Exported files
│   ├── prices_*.csv
│   └── prices_*.json
└── requirements.txt     ← Updated with Flask
```

---

## Key Features Summary

✅ **CSV Export**
- Compatible with Excel, spreadsheets
- Easy to share
- Human-readable format

✅ **JSON Export**
- API-friendly
- Structured data
- Includes statistics

✅ **Dashboard**
- Beautiful web UI
- Real-time statistics
- Download capabilities
- API endpoints

✅ **Statistics**
- Min/Max/Average prices
- Price trends
- Historical analysis

✅ **Automated**
- Can integrate with scheduler
- Auto-export after each job
- Background processing

---

## Next Steps (Phase 6)

Phase 6 will handle:
1. Create GitHub repository
2. Deploy to Railway (cloud)
3. Set up automated CI/CD
4. Configure environment variables
5. Monitor bot on Railway dashboard

---

## You're Almost Done!

✅ Phase 1: Project setup
✅ Phase 2: Web scraper
✅ Phase 3: Notifications
✅ Phase 4: Scheduler & integration
✅ Phase 5: Dashboard & export (THIS ONE!)
⏳ Phase 6: Cloud deployment

🎉 Only 1 phase left before your bot goes live!

---

## Quick Reference

### Start Dashboard
```bash
python dashboard.py
```

### Export Data
```bash
python exporter.py
```

### Run Full Tests
```bash
python test_phase5.py
```

### Integrate with Bot
- Add to scheduler for auto-export
- Run dashboard alongside bot
- Use API for integrations

---

## Configuration

All exports go to `exports/` directory with naming convention:
```
prices_YYYYMMDD_HHMMSS.csv
prices_YYYYMMDD_HHMMSS.json
```

Dashboard listens on:
```
http://localhost:5000
```

API base:
```
http://localhost:5000/api/
```

---

## Support

If dashboard won't start:
```bash
# Check Flask is installed
pip install flask

# Run with debug enabled
python dashboard.py --debug

# Change port
python -c "from dashboard import start_dashboard; start_dashboard(port=8000)"
```

If exports fail:
```bash
# Check exports directory exists
mkdir -p exports

# Check permissions
ls -la exports/

# Run exporter manually
python exporter.py
```

