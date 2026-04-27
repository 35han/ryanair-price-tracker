"""
Telegram notifications
Sends price alerts via Telegram bot
"""

import requests
import logging
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Sends price alerts via Telegram bot"""
    
    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def validate_credentials(self):
        """Test if Telegram bot token and chat ID are valid"""
        if not self.bot_token or not self.chat_id:
            logger.error("❌ Telegram credentials not configured")
            return False
        
        try:
            # Try to get bot info
            response = requests.get(f"{self.api_url}/getMe", timeout=5)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    logger.info(f"✅ Telegram bot validated: {bot_info['result']['first_name']}")
                    return True
            
            logger.error("❌ Telegram bot token invalid")
            return False
            
        except Exception as e:
            logger.error(f"❌ Telegram connection error: {e}")
            return False
    
    def send_message(self, text, parse_mode="HTML"):
        """
        Send a message via Telegram
        
        Args:
            text: Message text (supports HTML formatting)
            parse_mode: "HTML" or "Markdown"
        
        Returns:
            bool: True if sent successfully
        """
        
        if not self.bot_token or not self.chat_id:
            logger.error("❌ Telegram credentials not configured")
            return False
        
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Telegram message sent")
                return True
            else:
                logger.error(f"❌ Telegram error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            return False
    
    def send_price_alert(self, departure, arrival, price, average_price, date):
        """
        Send a price alert via Telegram
        
        Args:
            departure: Departure airport code
            arrival: Arrival airport code
            price: Current price found
            average_price: Average price from history
            date: Flight date
        """
        
        # Calculate savings
        savings = ((average_price - price) / average_price * 100) if average_price else 0
        savings_amount = average_price - price if average_price else 0
        
        # Format message
        message = f"""<b>✈️ PRICE ALERT!</b>

<b>Great Deal Found!</b>

<b>Route:</b> {departure} → {arrival}
<b>Date:</b> {date}
<b>Price:</b> <code>€{price:.2f}</code>
<b>Average:</b> €{average_price:.2f}

<b>You save:</b> €{savings_amount:.2f} ({savings:.1f}%)

<i>🏃 Hurry! Prices may change.</i>
<i>Visit Ryanair.com to book</i>

<i>Time: {datetime.now().strftime('%H:%M:%S')}</i>
"""
        
        return self.send_message(message, parse_mode="HTML")
    
    def send_daily_summary(self, lowest_price, highest_price, average_price, flights_checked, date):
        """
        Send a daily summary of prices checked
        
        Args:
            lowest_price: Lowest price found today
            highest_price: Highest price found today
            average_price: Average price today
            flights_checked: Number of flights checked
            date: Flight date being tracked
        """
        
        message = f"""<b>📊 Daily Price Summary</b>

<b>Date:</b> {date}

<b>Stats:</b>
💰 Lowest: €{lowest_price:.2f}
💸 Highest: €{highest_price:.2f}
📈 Average: €{average_price:.2f}

✈️ Flights checked: {flights_checked}

<i>Keep watching for better deals!</i>
"""
        
        return self.send_message(message, parse_mode="HTML")
    
    def send_hourly_update(self, departure, arrival, price, average_price, date):
        """
        Send hourly price update via Telegram (regardless of price changes)
        
        Args:
            departure: Departure airport code
            arrival: Arrival airport code
            price: Current lowest price found
            average_price: Average price from history
            date: Flight date
        """
        
        # Calculate change from average
        change = price - average_price
        change_percent = (change / average_price * 100) if average_price else 0
        
        trend = "📉" if change < 0 else "📈" if change > 0 else "→"
        
        message = f"""<b>⏰ Hourly Price Update</b>

<b>Route:</b> {departure} → {arrival}
<b>Date:</b> {date}

<b>Current Price:</b> <code>€{price:.2f}</code>
<b>Average:</b> €{average_price:.2f}

<b>Trend:</b> {trend} {change:+.2f}€ ({change_percent:+.1f}%)

<i>Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message, parse_mode="HTML")


# Test function
if __name__ == "__main__":
    notifier = TelegramNotifier()
    
    logger.info("Testing Telegram notifier...")
    logger.info(f"Bot token: {notifier.bot_token[:20]}..." if notifier.bot_token else "Not set")
    logger.info(f"Chat ID: {notifier.chat_id}")
    
    # Validate credentials
    if notifier.validate_credentials():
        logger.info("✅ Telegram credentials are valid!")
        
        # Send test alert
        test_result = notifier.send_price_alert(
            departure="TLL",
            arrival="NUE",
            price=42.50,
            average_price=55.00,
            date="2026-05-10"
        )
        
        if test_result:
            logger.info("✅ Test Telegram message sent successfully!")
        else:
            logger.error("❌ Failed to send test Telegram message")
    else:
        logger.error("❌ Telegram credentials are invalid or not configured")
        logger.info("\n📝 Please configure:")
        logger.info("   1. Create a Telegram bot with @BotFather")
        logger.info("   2. Set TELEGRAM_BOT_TOKEN in .env")
        logger.info("   3. Set TELEGRAM_CHAT_ID in .env")
        logger.info("   See setup instructions for details")
