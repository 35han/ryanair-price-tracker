"""
Simple combined scraper that tries multiple methods
Uses Selenium for reliable scraping with browser automation
"""

import logging
from datetime import datetime, timedelta
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT
from database import insert_price, insert_price_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing scrapers
try:
    from scraper_api import RyanairAPIScraperV2
    api_scraper_available = True
except:
    api_scraper_available = False
    logger.warning("API scraper not available")

try:
    from scraper_alternative import RyanairAlternativeScraper
    alt_scraper_available = True
except:
    alt_scraper_available = False
    logger.warning("Alternative scraper not available")

try:
    from scraper_playwright import PlaywrightRyanairScraper
    playwright_scraper_available = True
except:
    playwright_scraper_available = False
    logger.warning("Playwright scraper not available")

try:
    from scraper import RyanairScraper
    selenium_scraper_available = True
except:
    selenium_scraper_available = False
    logger.warning("Selenium scraper not available")

try:
    from scraper_mock import MockRyanairScraper
    mock_scraper_available = True
except:
    mock_scraper_available = False
    logger.warning("Mock scraper not available")


class FlightPriceScraper:
    """Main scraper that uses the most reliable method available"""
    
    def __init__(self):
        self.last_price = None
        self.api_scraper = None
        self.alt_scraper = None
        self.playwright_scraper = None
        self.selenium_scraper = None
        self.mock_scraper = None
        
        if api_scraper_available:
            self.api_scraper = RyanairAPIScraperV2()
        if alt_scraper_available:
            self.alt_scraper = RyanairAlternativeScraper()
        if playwright_scraper_available:
            self.playwright_scraper = PlaywrightRyanairScraper()
        if selenium_scraper_available:
            self.selenium_scraper = RyanairScraper()
        if mock_scraper_available:
            self.mock_scraper = MockRyanairScraper()
    
    def scrape(self, departure_date=None):
        """
        Try to scrape flight prices using available methods
        
        Returns:
            dict with flight data or None on failure
        """
        
        if not departure_date:
            departure_date = datetime.now() + timedelta(days=1)
        
        # Convert string date to datetime if needed
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        
        date_str = departure_date.strftime('%Y-%m-%d') if hasattr(departure_date, 'strftime') else str(departure_date)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Starting price check for {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}")
        logger.info(f"Date: {date_str}")
        logger.info(f"{'='*60}")
        
        result = None
        
        # Try API method first (faster, no browser needed)
        if self.api_scraper:
            logger.info("\n📡 Attempting API method...")
            try:
                result = self.api_scraper.scrape_price(departure_date)
                if result:
                    logger.info("✅ API method succeeded!")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ API method failed: {e}")
        
        # Try alternative scraper (different endpoints)
        if self.alt_scraper:
            logger.info("\n📡 Attempting alternative API method...")
            try:
                result = self.alt_scraper.scrape_price(departure_date)
                if result:
                    logger.info("✅ Alternative method succeeded!")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Alternative method failed: {e}")
        
        # Try Playwright (lightweight browser, works in cloud)
        if self.playwright_scraper:
            logger.info("\n🎬 Attempting Playwright browser method...")
            try:
                result = self.playwright_scraper.scrape_price(departure_date)
                if result:
                    logger.info("✅ Playwright method succeeded! REAL PRICES")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Playwright method failed: {e}")
        
        # Fallback to Selenium (more reliable but slower)
        if self.selenium_scraper:
            logger.info("\n🌐 Attempting Selenium browser method...")
            try:
                result = self.selenium_scraper.scrape_price(departure_date)
                if result:
                    logger.info("✅ Selenium method succeeded!")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Selenium method failed: {e}")
        
        # FINAL FALLBACK: Use mock data (for testing/development)
        if self.mock_scraper:
            logger.info("\n🎯 Using mock data for testing...")
            try:
                result = self.mock_scraper.scrape_price(departure_date)
                if result:
                    logger.info("✅ Mock data loaded (THIS IS TEST DATA)")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Mock scraper failed: {e}")
        
        logger.error("❌ All scraping methods failed!")
        return None
    
    def scrape_and_store(self, departure_date=None):
        """
        Scrape prices and automatically store in database
        
        Returns:
            dict with results
        """
        result = self.scrape(departure_date)
        
        if result and "flights" in result:
            try:
                # Store lowest price in database
                lowest_price = result.get("lowest_price")
                url = f"https://www.ryanair.com/en/{result['departure']}/{result['arrival']}"
                
                insert_price(
                    departure=result["departure"],
                    arrival=result["arrival"],
                    price=lowest_price,
                    departure_date=result["date"],
                    url=url
                )
                
                insert_price_check(
                    lowest_price=lowest_price,
                    status="success"
                )
                
                logger.info(f"✅ Stored price: €{lowest_price:.2f}")
                
                return {
                    "success": True,
                    "data": result,
                    "stored": True
                }
            except Exception as e:
                logger.error(f"Error storing in database: {e}")
                return {
                    "success": True,
                    "data": result,
                    "stored": False
                }
        else:
            # Store failed attempt
            try:
                insert_price_check(
                    lowest_price=None,
                    status="error",
                    error_message="Scraping failed - no flights found"
                )
            except:
                pass
            
            return {
                "success": False,
                "data": None,
                "stored": False
            }


# Test scraper
if __name__ == "__main__":
    logger.info("Testing combined flight price scraper...")
    
    scraper = FlightPriceScraper()
    
    # Scrape for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    result = scraper.scrape_and_store(tomorrow)
    
    if result["success"]:
        data = result["data"]
        print(f"\n✅ Success! Found flights:")
        print(f"   Route: {data['departure']} → {data['arrival']}")
        print(f"   Date: {data['date']}")
        print(f"   Lowest price: €{data['lowest_price']:.2f}")
        print(f"   Highest price: €{data.get('highest_price', 'N/A')}")
        print(f"   Average price: €{data.get('average_price', 'N/A')}")
        print(f"   Flights found: {len(data['flights'])}")
        print(f"   Stored in database: {result['stored']}")
        
        if data['flights']:
            print(f"\n   First 3 flights:")
            for i, flight in enumerate(data['flights'][:3]):
                print(f"     {i+1}. €{flight['price']:.2f} - {flight.get('departure_time', 'N/A')}")
    else:
        print(f"\n❌ Failed to scrape prices")
