"""
Mock scraper using realistic price data
While we solve the API/Selenium issues, this returns realistic prices
so the bot can actually send notifications
"""

import logging
import random
from datetime import datetime, timedelta
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockRyanairScraper:
    """Mock scraper - returns realistic prices for testing"""
    
    def __init__(self):
        # Price ranges based on the screenshot you provided
        # June prices: €38-€105 (lowest around €38-40)
        self.price_ranges = {
            "2026-06-09": (38, 85),   # Generally cheaper
            "2026-06-10": (40, 95),   # Mid-range
            "2026-06-12": (42, 100),  # Slightly expensive
        }
    
    def scrape_price(self, departure_date=None):
        """Return realistic mock prices"""
        
        if not departure_date:
            departure_date = datetime.now() + timedelta(days=1)
        
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        
        date_str = departure_date.strftime("%Y-%m-%d")
        
        logger.info(f"🎯 Using mock data for {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT} on {date_str}")
        
        # Get price range for this date
        if date_str in self.price_ranges:
            min_price, max_price = self.price_ranges[date_str]
        else:
            min_price, max_price = 35, 120
        
        # Generate realistic flight prices
        lowest_price = min_price + random.uniform(0, 3)
        flights = []
        
        # Create 10 fake flights with varied prices
        for i in range(10):
            price = lowest_price + (i * random.uniform(2, 8))
            flights.append({
                "price": round(price, 2),
                "currency": "EUR",
                "departure_time": f"{7 + i//2:02d}:{i*6 % 60:02d}",
                "arrival_time": f"{9 + i//2:02d}:{i*6 % 60:02d}",
                "duration": f"1h {i*5 % 60:02d}m"
            })
        
        result = {
            "departure": DEPARTURE_AIRPORT,
            "arrival": ARRIVAL_AIRPORT,
            "date": date_str,
            "flights": flights,
            "lowest_price": round(lowest_price, 2),
            "highest_price": round(flights[-1]["price"], 2),
            "average_price": round(sum([f["price"] for f in flights]) / len(flights), 2),
            "scraped_at": datetime.now().isoformat(),
            "source": "mock_data"
        }
        
        logger.info(f"✅ Mock scraper: Found prices €{result['lowest_price']:.2f} - €{result['highest_price']:.2f}")
        return result
