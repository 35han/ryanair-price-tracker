"""
APScheduler configuration - runs bot tasks on a schedule
Handles hourly price checks and other background jobs
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from config import CHECK_INTERVAL_HOURS, DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, EMAIL_PRICE_THRESHOLDS
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
    
    def price_check_job(self):
        """
        Main job: Scrape prices and check for alerts
        This runs on the schedule (hourly by default)
        """
        
        logger.info("\n" + "="*70)
        logger.info(f"⏰ PRICE CHECK JOB STARTED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        try:
            # Calculate flight date (tomorrow by default, customizable)
            departure_date = datetime.now() + timedelta(days=1)
            
            logger.info(f"\n📍 Checking: {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}")
            logger.info(f"📅 Date: {departure_date.strftime('%Y-%m-%d')}")
            logger.info(f"💰 Email thresholds: €{', €'.join(map(str, EMAIL_PRICE_THRESHOLDS))}")
            
            # Step 1: Scrape prices
            logger.info("\n1️⃣  Scraping prices...")
            result = self.scraper.scrape_and_store(departure_date)
            
            if not result["success"]:
                logger.error("❌ Scraping failed, skipping alerts")
                insert_price_check(None, "error", "Scraping failed")
                return
            
            # Step 2: Get price data
            data = result["data"]
            current_price = data["lowest_price"]
            average_price = data.get("average_price", current_price)
            flights_found = len(data["flights"])
            
            logger.info(f"\n2️⃣  Results:")
            logger.info(f"   ✅ Lowest price: €{current_price:.2f}")
            logger.info(f"   📊 Average: €{average_price:.2f}")
            logger.info(f"   ✈️  Flights found: {flights_found}")
            
            # Step 3: Check for alerts
            logger.info(f"\n3️⃣  Checking for alerts...")
            alert_result = self.alert_handler.check_and_alert(
                current_price, 
                departure_date
            )
            
            if alert_result.get("telegram_update") or alert_result.get("email_alerts_sent"):
                sent_methods = []
                if alert_result.get("telegram_update"):
                    sent_methods.append("Telegram")
                if alert_result.get("email_alerts_sent"):
                    sent_methods.append(f"Email (€{alert_result['email_alerts_sent']})")
                logger.info(f"   ✅ Notifications sent via: {', '.join(sent_methods)}")
            else:
                logger.info(f"   ℹ️  No alerts sent")
            
            # Step 4: Log success
            logger.info("\n✅ Job completed successfully")
            logger.info("="*70 + "\n")
            
        except Exception as e:
            logger.error(f"\n❌ Job failed with error: {e}")
            insert_price_check(None, "error", str(e))
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
        logger.info("\n💡 Tip: Bot will continue running in the background")
        logger.info("💡 Tip: Use Ctrl+C to stop the bot\n")
    
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
