# Phase 3: Email & Telegram Notifications - Complete! ✅

## What We Built

### Files Created:

1. **email_notifier.py** - Sends price alerts via Gmail
   - SMTP connection to Gmail
   - Beautiful HTML email formatting
   - Includes price history and savings
   - Easy credential validation

2. **telegram_notifier.py** - Sends alerts via Telegram bot
   - Connect to Telegram Bot API
   - Formatted messages with emojis
   - Daily summary support
   - Credential validation

3. **alert_handler.py** - Brain of the system
   - Checks if price is below threshold
   - Sends email AND Telegram alerts
   - Tracks last alert to avoid duplicates
   - Records alerts in database
   - Optional daily summaries

4. **test_notifications_mock.py** - Testing without real credentials
   - ✅ TESTED AND WORKING
   - Demonstrates all notification flows
   - Perfect for testing the system structure
   - Shows what emails/messages would look like

5. **.env.example** - Configuration template
   - Shows all required environment variables
   - Step-by-step setup instructions
   - Security best practices

6. **PHASE3_SETUP_GUIDE.md** - Complete beginner guide
   - How to set up Gmail app password
   - How to create Telegram bot
   - How to find your Telegram chat ID
   - Troubleshooting tips

---

## System Flow

```
┌──────────────────────────────────────────────────┐
│  Scraper finds price (€40.00)                    │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
         ┌────────────────────┐
         │  Alert Handler     │
         │  Checks threshold  │
         │  (€50.00)          │
         └────────────┬───────┘
                      │
              Is €40 < €50?
                    YES ✓
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
    📧 Email Sent           💬 Telegram Sent
    (Beautiful HTML)        (Formatted message)
         │                         │
         ▼                         ▼
    Gmail Inbox            Telegram Chat
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
            Database Alert Logged
```

---

## Test Results ✅

Successfully tested mock notification system:
- ✅ Email alert would send when price < €50
- ✅ Telegram message would send when price < €50
- ✅ No alert when price > €50
- ✅ Beautiful formatting with savings calculated
- ✅ Both channels work simultaneously

Output example:
```
📧 EMAIL WOULD BE SENT 📧
Route: TLL → NUE
Price: €42.50
Average: €55.00
Savings: €12.50

💬 TELEGRAM MESSAGE WOULD SEND 💬
✈️ PRICE ALERT!
Route: TLL → NUE
Price: €42.50
Savings: €12.50 (22.7%)
```

---

## How to Set Up Real Notifications

### Quick Setup (10 minutes total):

#### Gmail Setup:
1. Go to myaccount.google.com → Security
2. Enable "2-Step Verification"
3. Generate "App password" (Mail, Windows Computer)
4. Copy the 16-character password

#### Telegram Setup:
1. Open Telegram, search for @BotFather
2. Type /newbot
3. Name your bot (e.g., RyanairPriceBot)
4. Copy the TOKEN from BotFather
5. Send a message to your bot
6. Get your CHAT_ID from: https://api.telegram.org/botTOKEN/getUpdates

#### Configure:
```bash
cd ~/ryanair-price-tracker
cp .env.example .env
# Edit .env and fill in the 4 variables:
# GMAIL_EMAIL, GMAIL_PASSWORD, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

### Test Real Notifications:
```bash
# Test email
python email_notifier.py

# Test Telegram
python telegram_notifier.py

# Test complete alert system
python alert_handler.py
```

---

## How to Use in Your Bot

```python
from alert_handler import AlertHandler
from datetime import datetime, timedelta

# Initialize alert handler
alert_handler = AlertHandler()

# After scraping a price
current_price = 42.50
departure_date = datetime.now() + timedelta(days=1)

# Check and send alerts automatically
result = alert_handler.check_and_alert(current_price, departure_date)

if result["alert_sent"]:
    print(f"✅ Alerts sent via: {', '.join(result['sent_via'])}")
else:
    print(f"ℹ️ No alert: {result['reason']}")
```

---

## Configuration

### Required Environment Variables:

```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=app-password-16-chars
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
PRICE_THRESHOLD=50.0
```

### Optional Customization:

In `config.py`:
- Change `PRICE_THRESHOLD` for different alert price
- Change `DEPARTURE_AIRPORT` / `ARRIVAL_AIRPORT` for different routes
- Change `EMAIL_RECIPIENT` to send to different email

---

## Key Features

✅ **Email Alerts**
- Beautiful HTML formatting
- Shows savings and percentage discount
- Sent via Gmail SMTP
- Includes timestamp

✅ **Telegram Alerts**
- Instant notifications
- Emoji formatting for quick scanning
- Includes flight details
- Alternative to email

✅ **Smart Alerts**
- Only sends when price below threshold
- Avoids duplicate alerts for same price
- Tracks alerts in database
- Optional daily summaries

✅ **Error Handling**
- Validates credentials before sending
- Graceful fallback if one channel fails
- Detailed logging for debugging

---

## Troubleshooting

### Email issues?
- ❌ "Invalid credentials" → Check you used app password, not main password
- ❌ Email doesn't arrive → Check spam folder, verify EMAIL_RECIPIENT

### Telegram issues?
- ❌ "Invalid token" → Copy full token from BotFather, no extra spaces
- ❌ "Not getting messages" → Make sure you sent a message to bot first

### Both channels fail?
- Email and Telegram are independent
- If one fails, the other still tries
- Check .env file for typos
- Validate credentials separately

---

## Next Steps (Phase 4)

Once notifications are set up, we'll:
1. Create APScheduler configuration (run bot hourly)
2. Combine scraper + notifications
3. Create main.py (entry point)
4. Test full end-to-end workflow
5. Deploy to Railway

Ready for Phase 4? 🚀

---

## File Summary

| File | Purpose |
|------|---------|
| email_notifier.py | Gmail SMTP email sending |
| telegram_notifier.py | Telegram bot API integration |
| alert_handler.py | Coordination & alert logic |
| test_notifications_mock.py | Testing without credentials |
| .env.example | Configuration template |
| PHASE3_SETUP_GUIDE.md | Step-by-step setup instructions |
| PHASE3_SUMMARY.md | This file |
