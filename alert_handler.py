"""
Alert handler - checks prices and triggers notifications
This is the brain of the notification system
"""

import logging
from datetime import datetime, timedelta
from config import EMAIL_PRICE_THRESHOLDS, TELEGRAM_HOURLY_UPDATE, DEPARTURE_AIRPORT, ARRIVAL_AIRPORT
from database import get_lowest_price, insert_alert
from email_notifier import EmailNotifier
from telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)

class AlertHandler:
    """Checks prices and sends alerts based on configured thresholds"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.telegram_notifier = TelegramNotifier()
        self.email_thresholds = EMAIL_PRICE_THRESHOLDS  # [40.0, 35.0, 30.0]
        self.last_email_alerts = {}  # Track which thresholds we've already alerted for
        self.telegram_hourly = TELEGRAM_HOURLY_UPDATE  # True
    
    def check_and_alert(self, current_price, departure_date=None):
        """
        Check prices and send alerts:
        - EMAIL: ALWAYS send price report + threshold alerts
        - TELEGRAM: Every check with current price
        
        Args:
            current_price: The current lowest price found
            departure_date: Flight date (default: tomorrow)
        
        Returns:
            dict with alert status
        """
        
        if not departure_date:
            departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif hasattr(departure_date, 'strftime'):
            departure_date = departure_date.strftime("%Y-%m-%d")
        
        logger.info(f"\n🔔 Checking for alerts...")
        logger.info(f"   Current price: €{current_price:.2f}")
        logger.info(f"   Email thresholds: €{', €'.join(map(str, self.email_thresholds))}")
        
        # Get historical price data
        price_stats = get_lowest_price(7)  # Last 7 days
        
        if not price_stats:
            logger.warning("⚠️ No historical data yet")
            lowest, highest, average = current_price, current_price, current_price
        else:
            lowest, highest, average, count = price_stats
        
        result = {
            "current_price": current_price,
            "email_thresholds": self.email_thresholds,
            "telegram_update": False,
            "email_alerts_sent": [],
            "price_report_sent": False,
            "average_price": average
        }
        
        # ============ SKIP EMAIL - FOCUS ON TELEGRAM ONLY ============
        logger.info(f"📱 Skipping email - Telegram only mode")
        
        # ============ TELEGRAM UPDATES (Hourly regardless of price) ============
        if self.telegram_hourly:
            logger.info(f"📱 Sending hourly Telegram update...")
            
            if self.telegram_notifier.validate_credentials():
                telegram_sent = self.telegram_notifier.send_hourly_update(
                    departure=DEPARTURE_AIRPORT,
                    arrival=ARRIVAL_AIRPORT,
                    price=current_price,
                    average_price=average,
                    date=departure_date
                )
                if telegram_sent:
                    result["telegram_update"] = True
                    logger.info(f"✅ Telegram hourly update sent")
                else:
                    logger.warning("⚠️ Failed to send Telegram update")
            else:
                logger.warning("⚠️ Telegram not configured")
        
        return result
    
    def send_daily_summary(self):
        """Send a daily summary of prices (optional)"""
        
        logger.info("📊 Sending daily price summary...")
        
        price_stats = get_lowest_price(1)  # Today's data
        
        if not price_stats:
            logger.warning("No data for today")
            return False
        
        lowest, highest, average, count = price_stats
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Send via Telegram
        if self.telegram_notifier.validate_credentials():
            self.telegram_notifier.send_daily_summary(
                lowest_price=lowest,
                highest_price=highest,
                average_price=average,
                flights_checked=count,
                date=tomorrow
            )
            logger.info("✅ Daily summary sent")
            return True
        
        return False


# Test function
if __name__ == "__main__":
    logger.info("Testing alert handler...")
    
    handler = AlertHandler()
    
    # Test 1: Price below threshold
    logger.info("\n--- Test 1: Price below threshold (€40.00) ---")
    result = handler.check_and_alert(40.00, "2026-05-10")
    print(f"Alert sent: {result['alert_sent']}")
    print(f"Reason: {result['reason']}")
    if 'sent_via' in result:
        print(f"Sent via: {result['sent_via']}")
    
    # Test 2: Price above threshold
    logger.info("\n--- Test 2: Price above threshold (€60.00) ---")
    result = handler.check_and_alert(60.00, "2026-05-10")
    print(f"Alert sent: {result['alert_sent']}")
    print(f"Reason: {result['reason']}")
