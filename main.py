"""
Main entry point for Ryanair Price Tracker Bot
Run this file to start the bot: python main.py
"""

import logging
import signal
import sys
from datetime import datetime
from scheduler import start_bot, stop_bot, get_scheduler
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, EMAIL_PRICE_THRESHOLDS, CHECK_INTERVAL_HOURS
from database import create_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  # Also save to file
        logging.StreamHandler()  # Print to console
    ]
)
logger = logging.getLogger(__name__)

def show_banner():
    """Display bot banner"""
    banner = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       ✈️  RYANAIR PRICE TRACKER BOT - STARTING  ✈️        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    📍 Route: {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}
    💰 Email thresholds: €{', €'.join(map(str, EMAIL_PRICE_THRESHOLDS))}
    📱 Telegram: Hourly updates
    ⏰ Check Interval: Every {CHECK_INTERVAL_HOURS} hour(s)
    📧 Notifications: Email (threshold) + Telegram (hourly)
    🗄️  Database: SQLite (prices.db)
    
    ⏱️  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ────────────────────────────────────────────────────────────
    
    💡 The bot is now running in the background
    💡 It will check prices automatically every {CHECK_INTERVAL_HOURS} hour(s)
    💡 Logs are saved to: bot.log
    💡 Press Ctrl+C to stop the bot
    
    ────────────────────────────────────────────────────────────
    """
    print(banner)
    logger.info("Bot banner displayed")

def show_status():
    """Display current bot status"""
    scheduler = get_scheduler()
    status = scheduler.get_status()
    
    if status["running"]:
        print("\n✅ Bot Status: RUNNING")
        print(f"   Jobs scheduled: {status['jobs_count']}")
        for job in status["jobs"]:
            print(f"   └─ {job['name']}")
    else:
        print("\n❌ Bot Status: NOT RUNNING")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n" + "="*60)
    print("🛑 Shutting down bot...")
    print("="*60)
    logger.info("Received shutdown signal")
    
    stop_bot()
    
    print("✅ Bot stopped successfully")
    print("📊 Final logs saved to: bot.log")
    sys.exit(0)

def main():
    """Main function - entry point"""
    
    # Initialize database first
    logger.info("Initializing database...")
    create_database()
    logger.info("✅ Database initialized")
    
    # Show banner
    show_banner()
    
    try:
        # Start the bot
        logger.info("Starting bot...")
        scheduler = start_bot()
        
        # Show status
        show_status()
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        
        # Keep the bot running
        print("\n✨ Bot is ready! Waiting for scheduled jobs...\n")
        
        # This will run indefinitely until Ctrl+C
        # The scheduler handles background jobs automatically
        import time
        try:
            while True:
                time.sleep(1)  # Keep the main thread alive for the scheduler
        except KeyboardInterrupt:
            pass
            
    except KeyboardInterrupt:
        # Caught by signal handler above
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        stop_bot()
        sys.exit(1)


if __name__ == "__main__":
    main()
