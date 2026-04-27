"""
APScheduler configuration - runs bot tasks on a schedule
Handles hourly price checks and other background jobs
"""

import logging
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from config import CHECK_INTERVAL_HOURS, DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, EMAIL_PRICE_THRESHOLDS, SEARCH_DATES
from flight_scraper import FlightPriceScraper
from alert_handler import AlertHandler
from database import get_lowest_price, insert_price_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotScheduler:
    """Manages scheduled tasks for the price tracker bot"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = FlightPriceScraper()
        self.alert_handler = AlertHandler()
        self.job_id = None
        self.telegram_handler_thread = None
    
    def price_check_job(self):
        """
        Main job: Scrape prices for all search dates and check for alerts
        This runs on the schedule (every 15 minutes by default)
        """
        
        logger.info("\n" + "="*70)
        logger.info(f"⏰ PRICE CHECK JOB STARTED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        try:
            logger.info(f"\n📍 Checking: {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}")
            logger.info(f"📅 Dates to check: {', '.join(SEARCH_DATES)}")
            logger.info(f"💰 Email thresholds: €{', €'.join(map(str, EMAIL_PRICE_THRESHOLDS))}")
            
            all_lowest_prices = []
            
            # Step 1: Scrape prices for ALL search dates
            for search_date in SEARCH_DATES:
                logger.info(f"\n1️⃣  Scraping prices for {search_date}...")
                
                result = self.scraper.scrape_and_store(search_date)
                
                if not result["success"]:
                    logger.warning(f"⚠️  Scraping failed for {search_date}")
                    continue
                
                # Step 2: Get price data
                data = result["data"]
                current_price = data["lowest_price"]
                average_price = data.get("average_price", current_price)
                flights_found = len(data["flights"])
                
                all_lowest_prices.append(current_price)
                
                logger.info(f"   ✅ {search_date}: €{current_price:.2f} (avg: €{average_price:.2f}, flights: {flights_found})")
                
                # Step 3: Check for alerts for this date
                alert_result = self.alert_handler.check_and_alert(
                    current_price, 
                    search_date
                )
                
                if alert_result.get("telegram_update") or alert_result.get("email_alerts_sent"):
                    sent_methods = []
                    if alert_result.get("telegram_update"):
                        sent_methods.append("Telegram")
                    if alert_result.get("email_alerts_sent"):
                        sent_methods.append(f"Email (€{alert_result['email_alerts_sent']})")
                    logger.info(f"   ✅ Notifications sent via: {', '.join(sent_methods)}")
            
            if not all_lowest_prices:
                logger.error("❌ No prices were scraped successfully")
                return
            
            # Step 4: Log summary
            lowest_overall = min(all_lowest_prices)
            logger.info(f"\n📊 Summary:")
            logger.info(f"   Overall lowest: €{lowest_overall:.2f}")
            logger.info(f"   Dates checked: {len(all_lowest_prices)}/{len(SEARCH_DATES)}")
            
            # Step 5: Log success
            logger.info("\n✅ Job completed successfully")
            logger.info("="*70 + "\n")
            
        except Exception as e:
            logger.error(f"\n❌ Job failed with error: {e}")
            try:
                insert_price_check(None, "error", str(e))
            except Exception as db_error:
                logger.error(f"Failed to log error to database: {db_error}")
            logger.info("="*70 + "\n")
    
    def start(self):
        """Start the scheduler"""
        if self.scheduler.running:
            logger.warning("⚠️ Scheduler already running")
            return
        
        logger.info("\n" + "🚀 "*20)
        logger.info("STARTING PRICE TRACKER BOT")
        logger.info("🚀 "*20)
        
        # Add the price check job
        trigger = IntervalTrigger(hours=CHECK_INTERVAL_HOURS)
        self.job_id = self.scheduler.add_job(
            self.price_check_job,
            trigger=trigger,
            id="price_check_job",
            name="Hourly Price Check",
            replace_existing=True
        )
        
        logger.info(f"✅ Job scheduled: Every {CHECK_INTERVAL_HOURS} hour(s)")
        logger.info(f"📋 Job ID: {self.job_id.id}")
        logger.info(f"⏰ Scheduler will run the job every {CHECK_INTERVAL_HOURS} hour(s)")
        
        # Start the scheduler
        self.scheduler.start()
        logger.info("✅ Scheduler started successfully")
        
        # Start Telegram bot handler in separate thread
        logger.info("\n🤖 Starting Telegram bot handler...")
        self.start_telegram_handler()
        
        logger.info("\n💡 Tip: Bot will continue running in the background")
        logger.info("💡 Tip: Use Ctrl+C to stop the bot\n")
    
    def start_telegram_handler(self):
        """Start Telegram bot handler in a separate thread"""
        try:
            from telegram_bot_handler import start_telegram_bot_handler
            
            self.telegram_handler_thread = threading.Thread(
                target=start_telegram_bot_handler,
                daemon=False
            )
            self.telegram_handler_thread.start()
            logger.info("✅ Telegram bot handler started")
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram handler: {e}")

    
    def stop(self):
        """Stop the scheduler"""
        if not self.scheduler.running:
            logger.warning("⚠️ Scheduler not running")
            return
        
        self.scheduler.shutdown()
        logger.info("✅ Scheduler stopped")
    
    def get_status(self):
        """Get scheduler status"""
        if not self.scheduler.running:
            return {
                "running": False,
                "message": "Scheduler not running"
            }
        
        jobs = self.scheduler.get_jobs()
        
        status = {
            "running": True,
            "jobs_count": len(jobs),
            "jobs": []
        }
        
        for job in jobs:
            status["jobs"].append({
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger)
            })
        
        return status


# Global scheduler instance
_scheduler = None

def get_scheduler():
    """Get or create the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = BotScheduler()
    return _scheduler

def start_bot():
    """Start the bot (entry point for main.py)"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler

def stop_bot():
    """Stop the bot"""
    scheduler = get_scheduler()
    scheduler.stop()


# Test function
if __name__ == "__main__":
    logger.info("Testing scheduler...")
    
    scheduler = get_scheduler()
    
    # Show current config
    logger.info(f"\nConfiguration:")
    logger.info(f"  Route: {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}")
    logger.info(f"  Check interval: {CHECK_INTERVAL_HOURS} hour(s)")
    logger.info(f"  Email thresholds: €{', €'.join(map(str, EMAIL_PRICE_THRESHOLDS))}")
    
    # Run one test job immediately
    logger.info("\n🧪 Running one-time test job...\n")
    scheduler.price_check_job()
    
    logger.info("\n✅ Test complete!")
    logger.info("\nTo start the bot with scheduler:")
    logger.info("  python main.py")
