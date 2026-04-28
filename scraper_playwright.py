"""
Playwright-based scraper for Ryanair
Playwright is lightweight, cloud-friendly, and comes with built-in browsers
"""

import logging
import re
from datetime import datetime, timedelta
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright
    playwright_available = True
except ImportError:
    playwright_available = False
    logger.warning("Playwright not available - will install on first use")


class PlaywrightRyanairScraper:
    """Scrapes Ryanair using Playwright - lightweight browser automation"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    def scrape_price(self, departure_date=None):
        """Scrape real prices from Ryanair website"""
        
        if not departure_date:
            departure_date = datetime.now() + timedelta(days=1)
        
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        
        date_str = departure_date.strftime("%Y-%m-%d")
        
        logger.info(f"🎬 Playwright: Scraping {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT} on {date_str}")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                # Launch browser (Playwright handles browser installation)
                logger.info("📱 Starting browser...")
                browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
                
                page = browser.new_page()
                
                # Mimic real browser
                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                })
                
                # Go to Ryanair search page
                url = f"https://www.ryanair.com/en/booking/home/{DEPARTURE_AIRPORT}/{ARRIVAL_AIRPORT}/{date_str}"
                logger.info(f"📄 Loading: {url}")
                
                try:
                    # Don't wait for networkidle - Ryanair is a SPA that never truly idles
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    logger.warning(f"⚠️ Page load warning: {e}")
                
                # Give page a moment to render
                import time
                time.sleep(2)
                
                # Extract all flight cards and prices
                flights = []
                logger.info("⏳ Extracting flight data...")
                
                # Method 1: Try to get prices from visible elements
                try:
                    page.evaluate("""
                        // Wait for all images to load
                        Promise.all(Array.from(document.images).map(img => 
                            new Promise(resolve => {
                                img.onload = img.onerror = resolve;
                            })
                        ));
                    """)
                except:
                    pass
                
                # Get page content and extract prices
                content = page.content()
                
                # Look for price patterns in HTML (€XX.XX)
                price_pattern = r'€\s*(\d+[.,]\d{2})'
                prices = re.findall(price_pattern, content)
                
                if prices:
                    logger.info(f"Found price patterns: {prices[:5]}...")
                    # Convert strings to floats
                    for price_str in prices[:20]:  # Get top 20 prices
                        try:
                            price = float(price_str.replace(',', '.'))
                            flights.append({
                                "price": round(price, 2),
                                "currency": "EUR",
                                "departure_time": "N/A",
                                "arrival_time": "N/A",
                                "duration": "N/A"
                            })
                        except:
                            pass
                
                browser.close()
                
                if flights:
                    flights = sorted(flights, key=lambda x: x['price'])
                    # Remove duplicates
                    seen = set()
                    unique_flights = []
                    for f in flights:
                        if f['price'] not in seen:
                            unique_flights.append(f)
                            seen.add(f['price'])
                    
                    flights = unique_flights[:15]  # Keep top 15 unique prices
                    logger.info(f"✅ Playwright: Found {len(flights)} unique prices")
                    
                    return {
                        "departure": DEPARTURE_AIRPORT,
                        "arrival": ARRIVAL_AIRPORT,
                        "date": date_str,
                        "flights": flights,
                        "lowest_price": round(flights[0]["price"], 2),
                        "highest_price": round(flights[-1]["price"], 2),
                        "average_price": round(sum([f["price"] for f in flights]) / len(flights), 2),
                        "scraped_at": datetime.now().isoformat(),
                        "source": "playwright"
                    }
                else:
                    logger.warning("❌ Playwright: No prices found in content")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Playwright scraping failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
