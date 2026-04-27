# Phase 4: Scheduler & Integration - Complete! ✅

## What We Built

### Files Created (4 new files):

1. **scheduler.py** - APScheduler configuration
   - Runs price checks on a schedule (every hour)
   - Integrates scraper + alerts
   - Logs detailed job information
   - Can start/stop easily
   - Can check status

2. **main.py** - Bot entry point
   - Starts the scheduler
   - Displays nice banner
   - Handles graceful shutdown (Ctrl+C)
   - Logs to file (bot.log) and console
   - Shows bot status

3. **test_full_workflow.py** - Complete workflow test
   - ✅ TESTED AND WORKING
   - Tests: Scraper → Database → Alerts
   - Shows 7-day price statistics
   - Verifies all components work together

4. **test_scheduler_mock.py** - Scheduler test
   - ✅ TESTED AND WORKING
   - Simulates multiple scheduled jobs
   - Shows job execution every N seconds
   - Demonstrates scheduling logic

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│          MAIN.PY (Entry Point)                      │
├─────────────────────────────────────────────────────┤
│  - Shows banner                                     │
│  - Starts scheduler                                 │
│  - Handles graceful shutdown                        │
│  - Logs to bot.log + console                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│       SCHEDULER.PY (Background Jobs)                │
├─────────────────────────────────────────────────────┤
│  Every 1 hour (configurable):                       │
│                                                     │
│  1. Call FLIGHT_SCRAPER.py                         │
│     └─ Fetches latest prices                       │
│     └─ Stores in DATABASE                          │
│                                                     │
│  2. Call ALERT_HANDLER.py                          │
│     └─ Compares price vs threshold                 │
│     └─ Triggers EMAIL_NOTIFIER (if needed)         │
│     └─ Triggers TELEGRAM_NOTIFIER (if needed)      │
│                                                     │
│  3. Logs to DATABASE + bot.log                      │
└─────────────────────────────────────────────────────┘
```

---

## Test Results ✅

### Full Workflow Test:
```
📦 Step 1: Initialize components ✅
📍 Step 2: Scraping flight prices ✅
   └─ Lowest price: €38.15
   └─ Average price: €51.88
   └─ Flights found: 5

🔔 Step 3: Checking for price alerts ✅
   └─ Current price: €38.15
   └─ Threshold: €50.00
   └─ Alert logic working correctly

🗄️  Step 4: Verifying database ✅
   └─ 7 prices stored
   └─ 7-day stats available
   └─ All data accessible

✅ All systems operational!
```

### Scheduler Test:
```
🧪 Simulating 2 jobs at 3 second intervals

⏰ JOB #1 - 14:31:13 ✅
1️⃣  Scraping prices (using mock data)...
   ✅ Found: €33.38
2️⃣  Checking alerts (threshold: €50.0)...
   ✅ Job completed

⏰ JOB #2 - 14:31:16 ✅
1️⃣  Scraping prices (using mock data)...
   ✅ Found: €32.62
2️⃣  Checking alerts (threshold: €50.0)...
   ✅ Job completed

Status: ✅ WORKING
```

---

## How to Use

### Start the Bot:
```bash
cd ~/ryanair-price-tracker
source venv/bin/activate
python main.py
```

Output:
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       ✈️  RYANAIR PRICE TRACKER BOT - STARTING  ✈️        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

📍 Route: TLL → NUE
💰 Price Alert Threshold: €50
⏰ Check Interval: Every 1 hour(s)
📧 Notifications: Email + Telegram

The bot is now running in the background
It will check prices automatically every 1 hour(s)
Press Ctrl+C to stop the bot
```

### Stop the Bot:
Press `Ctrl+C` - gracefully shuts down scheduler and logs everything

### View Logs:
```bash
# View live logs
tail -f bot.log

# Count how many price checks run today
grep "PRICE CHECK JOB STARTED" bot.log | wc -l
```

---

## Configuration

### In config.py:

```python
# Check prices every N hours
CHECK_INTERVAL_HOURS = 1

# Price threshold for alerts
PRICE_THRESHOLD = 50.0

# Route to track
DEPARTURE_AIRPORT = "TLL"
ARRIVAL_AIRPORT = "NUE"
```

### Customization:

```bash
# Track different route
# Edit DEPARTURE_AIRPORT and ARRIVAL_AIRPORT in config.py

# Change alert frequency
# Edit CHECK_INTERVAL_HOURS in config.py
# Options: 0.5 (30 min), 1 (1 hour), 6 (6 hours), 24 (daily)

# Change price threshold
# Edit PRICE_THRESHOLD in config.py or .env file
```

---

## What Happens Every Hour

When the bot runs, it:

1. **Scrapes Prices** (30-60 seconds)
   - Tries API method first (fast)
   - Falls back to Selenium (reliable)
   - Extracts lowest price

2. **Stores Data** (1 second)
   - Saves price to SQLite database
   - Records timestamp
   - Logs job in price_checks table

3. **Checks Threshold** (1 second)
   - Compares current price vs threshold
   - Calculates savings
   - Checks if alert already sent

4. **Sends Alerts** (2 seconds)
   - If price below threshold:
     - Sends Email via Gmail SMTP
     - Sends Telegram message
     - Logs alert in database

5. **Completes Job** (1 second)
   - Writes summary to bot.log
   - Waits for next scheduled run

**Total time per job: ~1-2 minutes**

---

## Key Features

✅ **Automated Scheduling**
- Runs every 1 hour automatically
- No manual intervention needed
- Continues running in background

✅ **Robust Error Handling**
- Catches scraping errors
- Falls back to alternative methods
- Continues running even if one check fails

✅ **Comprehensive Logging**
- Logs to file (bot.log) + console
- Tracks every job execution
- Easy to troubleshoot

✅ **Graceful Shutdown**
- Press Ctrl+C to stop
- Cleanly closes scheduler
- No data loss or corruption

✅ **Database Integration**
- Stores all prices automatically
- Tracks alert history
- Enables price trend analysis

---

## Testing

### Test Full Workflow:
```bash
python test_full_workflow.py
```
Tests: Scraper → Database → Alerts

### Test Scheduler:
```bash
python test_scheduler_mock.py
```
Simulates multiple scheduled jobs

### Test Individual Components:
```bash
# Test scraper
python test_scraper.py

# Test notifications
python test_notifications_mock.py

# Test scheduler jobs
python scheduler.py
```

---

## Next Steps (Phase 5)

Phase 5 will add:
1. Dashboard to view price history
2. CSV/JSON export functionality
3. Price trend analysis
4. Better visualization

Then Phase 6: Deploy to Railway! 🚀

---

## File Summary

| File | Purpose |
|------|---------|
| scheduler.py | APScheduler configuration |
| main.py | Bot entry point |
| test_full_workflow.py | Complete workflow test |
| test_scheduler_mock.py | Scheduler test |
| PHASE4_SUMMARY.md | This file |

---

## Architecture Summary

```
User → main.py (starts bot)
         ↓
      scheduler.py (every 1 hour)
         ↓
      scraper (fetch prices)
         ↓
      database.py (store)
         ↓
      alert_handler.py (check threshold)
         ↓
      email_notifier.py + telegram_notifier.py (notify)
         ↓
      User receives alerts 📧💬
```

---

## You're Almost Done!

✅ Phase 1: Project setup
✅ Phase 2: Web scraper
✅ Phase 3: Notifications
✅ Phase 4: Scheduler & integration (THIS ONE!)
⏳ Phase 5: Dashboard & export
⏳ Phase 6: Cloud deployment

🎉 You've built the core bot! Just 2 more phases to go!
