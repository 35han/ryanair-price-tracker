"""
Alert handler - checks prices and triggers notifications
This is the brain of the notification system
"""

import logging
from datetime import datetime, timedelta
from config import PRICE_THRESHOLD, DEPARTURE_AIRPORT, ARRIVAL_AIRPORT
from database import get_lowest_price, insert_alert
from email_notifier import EmailNotifier
from telegram_notifier import TelegramNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertHandler:
    """Checks prices and sends alerts if price drops below threshold"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.telegram_notifier = TelegramNotifier()
        self.price_threshold = PRICE_THRESHOLD
        self.last_alert_price = None  # Avoid sending duplicate alerts
    
    def check_and_alert(self, current_price, departure_date=None):
        """
        Check if price is below threshold and send alerts
        
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
        logger.info(f"   Threshold: €{self.price_threshold:.2f}")
        
        # Get historical price data
        price_stats = get_lowest_price(7)  # Last 7 days
        
        if not price_stats:
            logger.warning("⚠️ No historical data yet")
            lowest, highest, average = current_price, current_price, current_price
        else:
            lowest, highest, average, count = price_stats
        
        result = {
            "current_price": current_price,
            "threshold": self.price_threshold,
            "alert_sent": False,
            "average_price": average,
            "reason": None
        }
        
        # Check if price is below threshold
        if current_price < self.price_threshold:
            # Avoid duplicate alerts for same price
            if self.last_alert_price and abs(self.last_alert_price - current_price) < 1.0:
                logger.info(f"⚠️ Alert already sent for this price")
                result["reason"] = "duplicate_price"
                return result
            
            logger.info(f"✅ PRICE BELOW THRESHOLD! Sending alerts...")
            
            # Try to send alerts
            alert_sent = False
            sent_via = []
            
            # Send email
            if self.email_notifier.validate_credentials():
                email_sent = self.email_notifier.send_price_alert(
                    departure=DEPARTURE_AIRPORT,
                    arrival=ARRIVAL_AIRPORT,
                    price=current_price,
                    average_price=average,
                    date=departure_date
                )
                if email_sent:
                    sent_via.append("email")
                    alert_sent = True
            else:
                logger.warning("⚠️ Email not configured, skipping email alert")
            
            # Send Telegram
            if self.telegram_notifier.validate_credentials():
                telegram_sent = self.telegram_notifier.send_price_alert(
                    departure=DEPARTURE_AIRPORT,
                    arrival=ARRIVAL_AIRPORT,
                    price=current_price,
                    average_price=average,
                    date=departure_date
                )
                if telegram_sent:
                    sent_via.append("telegram")
                    alert_sent = True
            else:
                logger.warning("⚠️ Telegram not configured, skipping Telegram alert")
            
            if alert_sent:
                # Record the alert in database
                try:
                    insert_alert(current_price, " + ".join(sent_via))
                    self.last_alert_price = current_price
                    result["alert_sent"] = True
                    result["sent_via"] = sent_via
                    result["reason"] = "price_below_threshold"
                    logger.info(f"✅ Alerts sent via: {', '.join(sent_via)}")
                except Exception as e:
                    logger.error(f"Error recording alert: {e}")
            else:
                logger.error("❌ No notification methods configured")
                result["reason"] = "no_notifiers_configured"
        else:
            logger.info(f"ℹ️ Price is above threshold (€{self.price_threshold:.2f})")
            result["reason"] = "price_above_threshold"
        
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
