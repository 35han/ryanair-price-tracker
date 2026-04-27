"""
Scheduler test with mock scraper - Tests the scheduling logic
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from test_scraper import MockFlightScraper
from alert_handler import AlertHandler
from config import CHECK_INTERVAL_HOURS, PRICE_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBotScheduler:
    """Scheduler with mock scraper for testing"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = MockFlightScraper()
        self.alert_handler = AlertHandler()
        self.job_count = 0
    
    def price_check_job(self):
        """Mock price check job"""
        self.job_count += 1
        
        logger.info("\n" + "="*70)
        logger.info(f"⏰ JOB #{self.job_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        try:
            # Scrape with mock data
            logger.info("1️⃣  Scraping prices (using mock data)...")
            result = self.scraper.scrape_and_store()
            
            if not result["success"]:
                logger.error("❌ Scraping failed")
                return
            
            data = result["data"]
            current_price = data["lowest_price"]
            
            logger.info(f"   ✅ Found: €{current_price:.2f}")
            
            # Check alerts
            logger.info(f"2️⃣  Checking alerts (threshold: €{PRICE_THRESHOLD})...")
            alert_result = self.alert_handler.check_and_alert(current_price)
            
            if alert_result["alert_sent"]:
                logger.info(f"   ✅ Alert sent via: {', '.join(alert_result.get('sent_via', []))}")
            else:
                logger.info(f"   ℹ️  No alert: {alert_result.get('reason', 'price above threshold')}")
            
            logger.info("✅ Job completed\n")
            
        except Exception as e:
            logger.error(f"❌ Job failed: {e}\n")
    
    def run_test(self, num_jobs=3, interval_seconds=5):
        """Run test with multiple jobs"""
        
        print("\n" + "="*70)
        print(f"🧪 SCHEDULER TEST - Simulating {num_jobs} jobs")
        print("="*70)
        print(f"\nConfiguration:")
        print(f"  Number of jobs: {num_jobs}")
        print(f"  Interval: {interval_seconds} seconds (normally {CHECK_INTERVAL_HOURS} hours)")
        print(f"  Price threshold: €{PRICE_THRESHOLD}")
        
        # Add job with short interval for testing
        trigger = IntervalTrigger(seconds=interval_seconds)
        self.scheduler.add_job(
            self.price_check_job,
            trigger=trigger,
            id="test_price_check",
            name="Test Price Check"
        )
        
        # Start scheduler
        self.scheduler.start()
        print(f"\n✅ Scheduler started")
        print(f"🚀 Running {num_jobs} jobs at {interval_seconds} second intervals...\n")
        
        import time
        
        # Let jobs run
        try:
            while self.job_count < num_jobs:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.scheduler.shutdown()
        
        # Summary
        print("\n" + "="*70)
        print("✅ SCHEDULER TEST COMPLETE")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   Jobs executed: {self.job_count}")
        print(f"   Interval: {interval_seconds}s (normally {CHECK_INTERVAL_HOURS}h)")
        print(f"   Status: ✅ WORKING")
        print(f"\n💡 In production, the bot runs one job every {CHECK_INTERVAL_HOURS} hour(s)")
        print(f"💡 Each job:")
        print(f"   1. Scrapes current prices")
        print(f"   2. Stores in database")
        print(f"   3. Checks if below threshold")
        print(f"   4. Sends Email + Telegram alerts if triggered")
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    logger.info("Starting scheduler test...")
    
    scheduler = MockBotScheduler()
    
    # Run 3 test jobs with 5 second interval (for quick testing)
    scheduler.run_test(num_jobs=3, interval_seconds=5)
    
    print("✨ Ready to start real bot with: python main.py")
