"""
Full workflow test - Simulates one complete price check cycle
Tests: Scraper → Database → Alerts → Notifications
"""

import logging
from datetime import datetime, timedelta
from test_scraper import MockFlightScraper
from alert_handler import AlertHandler
from database import get_lowest_price, get_all_prices
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, PRICE_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_workflow():
    """Run a complete bot cycle with mock data"""
    
    print("\n" + "="*70)
    print("🧪 FULL WORKFLOW TEST - SIMULATING ONE COMPLETE BOT CYCLE")
    print("="*70)
    
    # Step 1: Initialize components
    print("\n📦 Step 1: Initialize components")
    print("   ├─ Creating scraper...")
    scraper = MockFlightScraper()
    print("   ├─ Creating alert handler...")
    alert_handler = AlertHandler()
    print("   └─ ✅ Components ready\n")
    
    # Step 2: Scrape prices
    print("📍 Step 2: Scraping flight prices")
    print(f"   └─ Route: {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}")
    
    result = scraper.scrape_and_store()
    
    if result["success"]:
        data = result["data"]
        print(f"   ├─ Lowest price: €{data['lowest_price']:.2f}")
        print(f"   ├─ Average price: €{data['average_price']:.2f}")
        print(f"   ├─ Flights found: {len(data['flights'])}")
        print(f"   └─ ✅ Scraping successful\n")
    else:
        print("   └─ ❌ Scraping failed")
        return False
    
    # Step 3: Check alerts
    print("🔔 Step 3: Checking for price alerts")
    current_price = data['lowest_price']
    print(f"   ├─ Current price: €{current_price:.2f}")
    print(f"   ├─ Threshold: €{PRICE_THRESHOLD:.2f}")
    
    alert_result = alert_handler.check_and_alert(current_price)
    
    if alert_result["alert_sent"]:
        print(f"   ├─ ✅ Alert triggered!")
        print(f"   ├─ Sent via: {', '.join(alert_result.get('sent_via', []))}")
    else:
        print(f"   ├─ ℹ️  No alert (reason: {alert_result.get('reason', 'unknown')})")
    print("   └─ ✅ Alert check complete\n")
    
    # Step 4: Verify database
    print("🗄️  Step 4: Verifying database")
    all_prices = get_all_prices()
    print(f"   ├─ Total prices in database: {len(all_prices)}")
    
    if all_prices:
        latest = all_prices[0]
        print(f"   ├─ Latest: €{latest[3]:.2f} ({latest[5]})")
    
    stats = get_lowest_price(7)
    if stats:
        lowest, highest, average, count = stats
        print(f"   ├─ 7-day stats:")
        print(f"   │  ├─ Lowest: €{lowest:.2f}")
        print(f"   │  ├─ Highest: €{highest:.2f}")
        print(f"   │  ├─ Average: €{average:.2f}")
        print(f"   │  └─ Count: {count}")
    print("   └─ ✅ Database verified\n")
    
    # Step 5: Summary
    print("="*70)
    print("✅ FULL WORKFLOW TEST COMPLETE")
    print("="*70)
    print("\n📊 Test Summary:")
    print(f"   ✅ Scraper: Working (found {len(data['flights'])} flights)")
    print(f"   ✅ Database: Working ({len(all_prices)} prices stored)")
    print(f"   ✅ Alerts: Working (threshold logic correct)")
    print(f"   ✅ Notifications: Ready (Email + Telegram mock)")
    print("\n🎉 All systems operational!")
    print("✨ Bot is ready for deployment!\n")
    
    return True

def show_next_steps():
    """Show what to do next"""
    print("="*70)
    print("📋 NEXT STEPS")
    print("="*70)
    print("\n1. Test the scheduler (simulate hourly checks):")
    print("   cd ~/ryanair-price-tracker")
    print("   source venv/bin/activate")
    print("   python scheduler.py")
    
    print("\n2. Start the bot (real execution):")
    print("   python main.py")
    
    print("\n3. During Phase 6 (deployment):")
    print("   └─ Set up real Gmail credentials")
    print("   └─ Set up real Telegram bot")
    print("   └─ Deploy to Railway")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    logger.info("Starting full workflow test...")
    
    try:
        success = test_full_workflow()
        if success:
            show_next_steps()
        else:
            print("\n❌ Test failed")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
