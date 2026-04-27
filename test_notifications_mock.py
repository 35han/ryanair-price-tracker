"""
Mock notification tester - Demonstrates the alert system without real email/Telegram
Useful for testing the system structure before credentials are configured
"""

import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockEmailNotifier:
    """Mock email notifier for testing"""
    
    def __init__(self):
        pass
    
    def validate_credentials(self):
        logger.info("📧 [MOCK] Email credentials validated (mock)")
        return True
    
    def send_price_alert(self, departure, arrival, price, average_price, date, url=None):
        logger.info(f"""
        ╔═══════════════════════════════════╗
        ║      📧 EMAIL WOULD BE SENT 📧   ║
        ╠═══════════════════════════════════╣
        ║ Route: {departure} → {arrival}            ║
        ║ Price: €{price:.2f}                    ║
        ║ Average: €{average_price:.2f}           ║
        ║ Date: {date}                  ║
        ║ Savings: €{average_price - price:.2f}                  ║
        ╚═══════════════════════════════════╝
        """)
        return True

class MockTelegramNotifier:
    """Mock Telegram notifier for testing"""
    
    def __init__(self):
        pass
    
    def validate_credentials(self):
        logger.info("💬 [MOCK] Telegram credentials validated (mock)")
        return True
    
    def send_price_alert(self, departure, arrival, price, average_price, date):
        logger.info(f"""
        ╔═══════════════════════════════════╗
        ║   💬 TELEGRAM MESSAGE WOULD SEND 💬 ║
        ╠═══════════════════════════════════╣
        ║ ✈️ PRICE ALERT!                   ║
        ║                                   ║
        ║ Route: {departure} → {arrival}     ║
        ║ Price: €{price:.2f}                ║
        ║ Date: {date}                  ║
        ║ Savings: €{average_price - price:.2f}                ║
        ╚═══════════════════════════════════╝
        """)
        return True

class MockAlertHandler:
    """Mock alert handler for demonstration"""
    
    def __init__(self):
        self.email_notifier = MockEmailNotifier()
        self.telegram_notifier = MockTelegramNotifier()
        self.price_threshold = 50.0
    
    def check_and_alert(self, current_price, departure_date=None):
        """Check and send mock alerts"""
        
        if not departure_date:
            departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif hasattr(departure_date, 'strftime'):
            departure_date = departure_date.strftime("%Y-%m-%d")
        
        logger.info(f"\n🔔 Checking alerts (MOCK MODE)...")
        logger.info(f"   Current price: €{current_price:.2f}")
        logger.info(f"   Threshold: €{self.price_threshold:.2f}")
        
        result = {
            "current_price": current_price,
            "threshold": self.price_threshold,
            "alert_sent": False,
            "sent_via": []
        }
        
        if current_price < self.price_threshold:
            logger.info(f"✅ PRICE BELOW THRESHOLD! Would send alerts...")
            
            # Mock email
            if self.email_notifier.validate_credentials():
                self.email_notifier.send_price_alert(
                    departure="TLL",
                    arrival="NUE",
                    price=current_price,
                    average_price=55.0,
                    date=departure_date
                )
                result["sent_via"].append("email")
                result["alert_sent"] = True
            
            # Mock Telegram
            if self.telegram_notifier.validate_credentials():
                self.telegram_notifier.send_price_alert(
                    departure="TLL",
                    arrival="NUE",
                    price=current_price,
                    average_price=55.0,
                    date=departure_date
                )
                result["sent_via"].append("telegram")
                result["alert_sent"] = True
        else:
            logger.info(f"ℹ️ Price above threshold - no alert")
        
        return result

if __name__ == "__main__":
    logger.info("🧪 Testing notification system (MOCK MODE)...\n")
    
    handler = MockAlertHandler()
    
    # Test scenarios
    test_cases = [
        (42.50, "Price below threshold"),
        (35.00, "Great deal"),
        (60.00, "Price above threshold"),
    ]
    
    for price, description in test_cases:
        logger.info(f"\n{'='*50}")
        logger.info(f"Test: {description} (€{price:.2f})")
        logger.info('='*50)
        
        result = handler.check_and_alert(price, "2026-05-10")
        
        logger.info(f"\nResult:")
        logger.info(f"  Alert sent: {result['alert_sent']}")
        logger.info(f"  Sent via: {', '.join(result['sent_via']) if result['sent_via'] else 'None'}")
    
    logger.info("\n" + "="*50)
    logger.info("✅ Mock notification test complete!")
    logger.info("="*50)
    logger.info("\nNext steps:")
    logger.info("1. Set up Gmail (see PHASE3_SETUP_GUIDE.md)")
    logger.info("2. Set up Telegram (see PHASE3_SETUP_GUIDE.md)")
    logger.info("3. Run: python email_notifier.py (to test real email)")
    logger.info("4. Run: python telegram_notifier.py (to test real Telegram)")
    logger.info("5. Run: python alert_handler.py (to test real alerts)")
