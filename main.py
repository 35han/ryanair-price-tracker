#!/usr/bin/env python3
"""
Main entry point for Ryanair Price Tracker Bot
"""

import sys
import os

# MUST be first - force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

# Print immediately to both stdout and stderr
print("\n" + "="*70, flush=True)
print("🚀 BOT STARTUP BEGINNING", flush=True)
print("="*70, flush=True)

print("📋 Environment:", flush=True)
print(f"   Python: {sys.version}", flush=True)
print(f"   CWD: {os.getcwd()}", flush=True)
print(f"   PID: {os.getpid()}", flush=True)

try:
    print("\n🔧 Configuring logging...", flush=True)
    import logging
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add unbuffered handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(handler)
    
    logger = logging.getLogger(__name__)
    logger.info("✅ Logging configured")
    
    # Now try imports
    logger.info("\n📦 Importing modules...")
    
    from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, SEARCH_DATES
    logger.info(f"✅ Config: {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}, Dates: {SEARCH_DATES}")
    
    from database import create_database
    logger.info("✅ Database module loaded")
    
    from scheduler import start_bot, stop_bot
    logger.info("✅ Scheduler module loaded")
    
    # Start bot
    logger.info("\n✈️ STARTING BOT")
    logger.info("="*70)
    
    create_database()
    logger.info("✅ Database initialized")
    
    start_bot()
    
except Exception as e:
    print(f"\n❌ STARTUP ERROR: {e}", flush=True)
    print(f"   Type: {type(e).__name__}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

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
