"""
Main entry point for Ryanair Price Tracker Bot
Run this file to start the bot: python main.py
"""

import logging
import signal
import sys
import os
from datetime import datetime

# Force unbuffered output for Railway from the very start
os.environ['PYTHONUNBUFFERED'] = '1'

# CRITICAL: Configure ROOT logger FIRST before any imports
# This ensures all child loggers use the same configuration
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Remove any existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add single unbuffered console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Now import the rest
from scheduler import start_bot, stop_bot, get_scheduler
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, EMAIL_PRICE_THRESHOLDS, CHECK_INTERVAL_HOURS
from database import create_database

logger = logging.getLogger(__name__)

def main():
    """Main function - entry point"""
    
    try:
        # Initialize database first
        logger.info("🚀 Initializing database...")
        create_database()
        logger.info("✅ Database initialized")
        
        # Show banner
        logger.info("\n" + "="*70)
        logger.info("✈️  RYANAIR PRICE TRACKER BOT - STARTING")
        logger.info("="*70)
        logger.info(f"📍 Route: {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}")
        logger.info(f"⏰ Check Interval: Every {CHECK_INTERVAL_HOURS} hour(s)")
        logger.info(f"📱 Notifications: Telegram (hourly updates)")
        logger.info(f"🗄️  Database: prices.db")
        logger.info("="*70 + "\n")
        
        # Start the bot
        logger.info("🚀 Starting bot scheduler...")
        scheduler = start_bot()
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("\n\n🛑 Shutting down bot...")
            stop_bot()
            logger.info("✅ Bot stopped")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("✨ Bot is running! Waiting for scheduled jobs...\n")
        
        # Keep running indefinitely
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
        stop_bot()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        stop_bot()
        sys.exit(1)


if __name__ == "__main__":
    main()
