"""
Configuration file for Ryanair Price Tracker Bot
All settings in one place for easy customization
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== FLIGHT DETAILS ==========
DEPARTURE_AIRPORT = "TLL"  # Tallinn, Estonia
ARRIVAL_AIRPORT = "BER"    # Berlin, Germany
SEARCH_DATES = ["2026-06-09", "2026-06-10", "2026-06-12"]  # Specific dates to track

# ========== PRICE ALERT SETTINGS ==========
PRICE_THRESHOLD = float(os.getenv("PRICE_THRESHOLD", 24.99))  # Alert when price < €24.99
CHECK_INTERVAL_HOURS = 1  # Check every 1 hour

# ========== EMAIL SETTINGS ==========
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")  # Your Gmail address (from environment)
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # Gmail app password (from environment)
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", GMAIL_EMAIL)  # Where to send alerts

# ========== TELEGRAM SETTINGS ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # From BotFather
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Your chat ID

# ========== DATABASE SETTINGS ==========
DATABASE_NAME = "prices.db"

# ========== LOGGING ==========
LOG_FILE = "bot.log"
