"""
Web scraper for Ryanair flight prices
Uses Selenium to automate browser and extract flight prices
"""

import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RyanairScraper:
    """Scrapes flight prices from Ryanair website"""
    
    def __init__(self):
        self.base_url = "https://www.ryanair.com"
        self.driver = None
        
    def setup_driver(self):
        """Initialize Selenium WebDriver with Chrome"""
        logger.info("Setting up browser...")
        
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run without showing browser window
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            # Use webdriver-manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Browser started successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            return False
    
    def close_driver(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
    
    def get_prices(self, departure_date=None):
        """
        Scrape flight prices from Ryanair
        
        Args:
            departure_date: datetime object for flight date (default: tomorrow)
        
        Returns:
            dict with price info or None if error
        """
        
        if not departure_date:
            departure_date = datetime.now() + timedelta(days=1)
        
        # Format date as YYYY-MM-DD
        date_str = departure_date.strftime("%Y-%m-%d")
        
        # Build Ryanair search URL
        search_url = f"{self.base_url}/en/booking/home"
        
        logger.info(f"🔍 Scraping prices for {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT} on {date_str}")
        
        try:
            # Open the Ryanair website
            self.driver.get(search_url)
            logger.info("Page loaded, waiting for elements...")
            
            # Wait for the page to fully load (max 10 seconds)
            wait = WebDriverWait(self.driver, 10)
            
            # Try to find and fill the departure airport field
            try:
                departure_field = wait.until(
                    EC.presence_of_element_located((By.ID, "input-button-origin"))
                )
                departure_field.click()
                time.sleep(1)
                
                # Type the departure airport
                departure_input = self.driver.find_element(By.ID, "input-button-origin")
                departure_input.send_keys(DEPARTURE_AIRPORT)
                time.sleep(2)
                
                logger.info(f"✅ Entered departure: {DEPARTURE_AIRPORT}")
            except Exception as e:
                logger.warning(f"Could not find departure field: {e}")
            
            # Find and fill the arrival airport field
            try:
                arrival_field = wait.until(
                    EC.presence_of_element_located((By.ID, "input-button-destination"))
                )
                arrival_field.click()
                time.sleep(1)
                
                arrival_input = self.driver.find_element(By.ID, "input-button-destination")
                arrival_input.send_keys(ARRIVAL_AIRPORT)
                time.sleep(2)
                
                logger.info(f"✅ Entered arrival: {ARRIVAL_AIRPORT}")
            except Exception as e:
                logger.warning(f"Could not find arrival field: {e}")
            
            # Find and fill the date field
            try:
                date_field = wait.until(
                    EC.presence_of_element_located((By.NAME, "departure"))
                )
                date_field.click()
                time.sleep(1)
                
                date_input = self.driver.find_element(By.NAME, "departure")
                date_input.clear()
                date_input.send_keys(date_str)
                time.sleep(1)
                
                logger.info(f"✅ Entered date: {date_str}")
            except Exception as e:
                logger.warning(f"Could not find date field: {e}")
            
            # Find and click the search button
            try:
                search_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid*='search']"))
                )
                search_button.click()
                logger.info("🔎 Clicked search button, waiting for results...")
                
                time.sleep(5)  # Wait for results to load
                
            except Exception as e:
                logger.warning(f"Could not click search button: {e}")
            
            # Extract flight prices
            prices = self._extract_flight_prices()
            
            if prices:
                logger.info(f"✅ Found {len(prices)} flights")
                return {
                    "departure": DEPARTURE_AIRPORT,
                    "arrival": ARRIVAL_AIRPORT,
                    "date": date_str,
                    "flights": prices,
                    "lowest_price": min([p["price"] for p in prices]) if prices else None,
                    "scraped_at": datetime.now().isoformat()
                }
            else:
                logger.warning("⚠️ No flights found on page")
                return None
                
        except TimeoutException:
            logger.error("❌ Timeout waiting for page elements")
            return None
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            return None
    
    def _extract_flight_prices(self):
        """Extract flight prices from loaded page"""
        try:
            flights = []
            
            # Look for flight cards (this selector may need adjustment based on Ryanair's current HTML)
            flight_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid*='flight-card']")
            
            logger.info(f"Found {len(flight_cards)} flight cards")
            
            for card in flight_cards:
                try:
                    # Try to extract price - may be in different formats
                    price_text = card.find_element(By.CSS_SELECTOR, "span[data-testid*='price']").text
                    
                    # Clean price (remove € symbol, extra spaces)
                    price = float(price_text.replace("€", "").replace(",", ".").strip())
                    
                    # Try to get departure time
                    try:
                        time_element = card.find_element(By.CSS_SELECTOR, "div[data-testid*='departure']")
                        departure_time = time_element.text
                    except:
                        departure_time = "N/A"
                    
                    flights.append({
                        "price": price,
                        "currency": "EUR",
                        "departure_time": departure_time,
                        "scraped_at": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.debug(f"Could not extract price from card: {e}")
                    continue
            
            return flights
            
        except Exception as e:
            logger.error(f"Error extracting prices: {e}")
            return []
    
    def scrape_price(self, departure_date=None):
        """
        Main function: Setup browser, scrape prices, return results
        
        Returns:
            dict with flight price data or None on error
        """
        try:
            if not self.setup_driver():
                return None
            
            result = self.get_prices(departure_date)
            return result
            
        finally:
            self.close_driver()


# Test the scraper
if __name__ == "__main__":
    logger.info("Starting Ryanair scraper test...")
    
    scraper = RyanairScraper()
    result = scraper.scrape_price()
    
    if result:
        print("\n✅ Scraping successful!")
        print(f"Route: {result['departure']} → {result['arrival']}")
        print(f"Date: {result['date']}")
        print(f"Lowest price: €{result['lowest_price']}")
        print(f"Flights found: {len(result['flights'])}")
        
        # Show first 3 flights
        for i, flight in enumerate(result['flights'][:3]):
            print(f"  Flight {i+1}: €{flight['price']} - Departs at {flight['departure_time']}")
    else:
        print("\n❌ Scraping failed")
