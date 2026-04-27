# Phase 3: Email & Telegram Setup Guide

## Overview
This guide shows you how to set up Email and Telegram notifications for your bot. It takes about 10 minutes total.

---

## Part 1: Gmail Email Setup (5 minutes)

### Step 1: Create a Gmail App Password

Ryanair Price Bot needs to log in to your Gmail account to send emails. For security, Gmail requires an "app password" instead of your main password.

**Follow these steps:**

1. Go to: **https://myaccount.google.com**
2. Click **"Security"** in the left menu
3. Find **"2-Step Verification"** and make sure it's **ON**
   - If it's off, click it and follow prompts to enable it
4. After 2-Step is enabled, scroll down and find **"App passwords"**
5. Click **"App passwords"**
6. Select:
   - **App**: "Mail"
   - **Device**: "Windows Computer" (or your device type)
7. Google will generate a **16-character password**
8. **Copy this password** (it looks like: `abcd efgh ijkl mnop`)

### Step 2: Add to .env file

1. In your project folder (`~/ryanair-price-tracker`), find the file `.env.example`
2. Copy it: `cp .env.example .env`
3. Open `.env` in a text editor
4. Fill in:

```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=abcd efgh ijkl mnop
EMAIL_RECIPIENT=your-email@gmail.com
```

### Step 3: Test Email

Run this command to test if email works:

```bash
cd ~/ryanair-price-tracker
source venv/bin/activate
python email_notifier.py
```

You should see:
```
✅ Email credentials validated
✅ Test email sent successfully!
```

And you should receive a test email! 📧

---

## Part 2: Telegram Bot Setup (5 minutes)

### Step 1: Create a Telegram Bot

1. Open **Telegram app** (download from https://telegram.org if you don't have it)
2. Search for: **@BotFather** (official bot creator)
3. Click on BotFather and say **"Hello"** or **"/start"**
4. Type: **/newbot**
5. BotFather asks: "What should your bot be called?"
   - Answer: `RyanairPriceBot` (or any name you like)
6. BotFather asks: "What should your bot's username be?"
   - Answer: `ryanair_price_bot_YOURNAME` (username must be unique, all lowercase)
7. **BotFather gives you a TOKEN** like: `123456789:ABCDefGHIjklMnoPQrsTuVwXyZaBcDeFgH`
   - **COPY THIS TOKEN** and save it somewhere safe

### Step 2: Get Your Chat ID

1. In Telegram, search for your bot username (e.g., `ryanair_price_bot_YOURNAME`)
2. Click on your bot and send it any message (e.g., "hello")
3. Open this URL in your browser (replace YOUR_TOKEN with your actual token):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
   For example:
   ```
   https://api.telegram.org/bot123456789:ABCDefGHIjklMnoPQrsTuVwXyZaBcDeFgH/getUpdates
   ```
4. You'll see JSON data. Look for **"chat":{"id":123456789}**
5. The number (123456789) is your **CHAT_ID** - copy it

### Step 3: Add to .env file

Open `.env` and fill in:

```
TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIjklMnoPQrsTuVwXyZaBcDeFgH
TELEGRAM_CHAT_ID=123456789
```

### Step 4: Test Telegram

Run this command:

```bash
cd ~/ryanair-price-tracker
source venv/bin/activate
python telegram_notifier.py
```

You should see:
```
✅ Telegram bot validated: RyanairPriceBot
✅ Telegram message sent
```

And you should receive a test message in Telegram! 💬

---

## Part 3: Test Both Notifications Together

Once both Email and Telegram are set up, test the alert handler:

```bash
cd ~/ryanair-price-tracker
source venv/bin/activate
python alert_handler.py
```

You should receive:
- 📧 Email alert (when price is below threshold)
- 💬 Telegram message (when price is below threshold)

---

## Troubleshooting

### Email not working?

**Problem**: "Email credentials invalid" error

**Solution**:
1. Make sure you used an **app password**, not your regular Gmail password
2. Make sure **2-Step Verification is ON**
3. Try creating a new app password

**Problem**: Email sends but never arrives

**Solution**:
1. Check your spam/junk folder
2. Make sure `EMAIL_RECIPIENT` is correct in `.env`

### Telegram not working?

**Problem**: "Telegram bot token invalid" error

**Solution**:
1. Make sure you copied the **full token** from BotFather
2. Make sure there are no extra spaces

**Problem**: Bot receives messages but doesn't send them

**Solution**:
1. Make sure you sent at least one message to your bot first
2. Try this URL in browser to test:
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
   - You should see your message in the JSON response

**Problem**: Can't find Chat ID

**Solution**:
1. Make sure you:
   - Created the bot with BotFather
   - Added it to a chat
   - Sent it a message
   - Checked the `/getUpdates` URL

---

## Next Steps (Phase 4)

Once notifications are working, we'll:
1. Create the scheduler (runs bot every hour)
2. Combine everything (scraper → alerts → notifications)
3. Test the complete workflow

Ready to move on? Let me know! 🚀
