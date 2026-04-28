"""
Synchronous scheduler - more reliable than APScheduler BackgroundScheduler
Runs jobs in the main thread to ensure they execute in Railway environment
"""

import logging
import time
from datetime import datetime, timedelta
from config import CHECK_INTERVAL_HOURS, DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, EMAIL_PRICE_THRESHOLDS, SEARCH_DATES
from flight_scraper import FlightPriceScraper
from alert_handler import AlertHandler
from database import insert_price_check

logger = logging.getLogger(__name__)

class SyncBotScheduler:
    """Synchronous scheduler that runs jobs directly in main thread"""
    
    def __init__(self):
        self.scraper = FlightPriceScraper()
        self.alert_handler = AlertHandler()
        self.running = False
        self.check_interval_seconds = int(CHECK_INTERVAL_HOURS * 3600)  # Convert hours to seconds
        self.next_check_time = None
    
    def price_check_job(self):
        """
        Main job: Scrape prices for all search dates and check for alerts
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
            logger.error(f"\n❌ Job failed with error: {e}", exc_info=True)
            try:
                insert_price_check(None, "error", str(e))
            except Exception as db_error:
                logger.error(f"Failed to log error to database: {db_error}")
            logger.info("="*70 + "\n")
    
    def start(self):
        """Start the synchronous scheduler loop"""
        if self.running:
            logger.warning("⚠️ Scheduler already running")
            return
        
        self.running = True
        self.next_check_time = datetime.now()
        
        logger.info("\n" + "🚀 "*20)
        logger.info("STARTING PRICE TRACKER BOT (SYNC MODE)")
        logger.info("🚀 "*20)
        logger.info(f"\n✅ Scheduler configured for every {CHECK_INTERVAL_HOURS} hour(s) ({self.check_interval_seconds} seconds)")
        logger.info(f"📋 First check will run immediately, then every {self.check_interval_seconds} seconds\n")
        
        # Main scheduler loop
        while self.running:
            now = datetime.now()
            
            # Check if it's time to run the job
            if now >= self.next_check_time:
                logger.info(f"[SCHEDULER] Running job at {now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                try:
                    self.price_check_job()
                except Exception as e:
                    logger.error(f"Uncaught error in job: {e}", exc_info=True)
                
                # Schedule next check
                self.next_check_time = now + timedelta(seconds=self.check_interval_seconds)
                logger.info(f"[SCHEDULER] Next check scheduled for {self.next_check_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Sleep briefly to avoid busy-waiting
            time.sleep(5)  # Check every 5 seconds if it's time to run
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("✅ Scheduler stopped")
    
    def get_status(self):
        """Get scheduler status"""
        return {
            "running": self.running,
            "jobs_count": 1,
            "jobs": [{
                "id": "price_check_job",
                "name": "Hourly Price Check",
                "trigger": f"every {CHECK_INTERVAL_HOURS} hour(s)"
            }]
        }


# Global scheduler instance
_scheduler = None

def get_scheduler():
    """Get or create the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = SyncBotScheduler()
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
