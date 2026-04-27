"""
Playwright-based scraper for Ryanair
Playwright is lightweight, cloud-friendly, and comes with built-in browsers
"""

import logging
from datetime import datetime, timedelta
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT

logging.basicConfig(level=logging.INFO)
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
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Go to Ryanair search page
                url = f"https://www.ryanair.com/en/booking/home/{DEPARTURE_AIRPORT}/{ARRIVAL_AIRPORT}/{date_str}"
                logger.info(f"📄 Loading: {url}")
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait for prices to load
                logger.info("⏳ Waiting for prices to load...")
                page.wait_for_selector("div[data-testid*='price']", timeout=15000)
                
                # Extract price data
                flights = []
                try:
                    # Get all flight cards
                    flight_cards = page.query_selector_all("div[data-testid*='flight']")
                    
                    for card in flight_cards:
                        try:
                            # Try to get price
                            price_elem = card.query_selector("div[data-testid*='price'], span[data-testid*='price']")
                            if price_elem:
                                price_text = price_elem.text_content()
                                # Extract number from text like "€39.99"
                                price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
                                
                                departure = card.query_selector("[data-testid*='departure']")
                                arrival = card.query_selector("[data-testid*='arrival']")
                                
                                flights.append({
                                    "price": price,
                                    "currency": "EUR",
                                    "departure_time": departure.text_content() if departure else "N/A",
                                    "arrival_time": arrival.text_content() if arrival else "N/A",
                                    "duration": "N/A"
                                })
                        except Exception as e:
                            logger.debug(f"Could not parse flight card: {e}")
                            continue
                
                except Exception as e:
                    logger.warning(f"Could not find flight cards: {e}")
                
                browser.close()
                
                if flights:
                    flights = sorted(flights, key=lambda x: x['price'])
                    logger.info(f"✅ Playwright: Found {len(flights)} flights")
                    
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
                    logger.warning("❌ Playwright: No flights found")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Playwright scraping failed: {e}")
            return None
