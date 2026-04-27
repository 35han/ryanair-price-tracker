"""
Demo/Test scraper that shows the complete workflow
Uses mock data to demonstrate how the system works
"""

import logging
from datetime import datetime, timedelta
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT
from database import insert_price, insert_price_check, get_lowest_price

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockFlightScraper:
    """Mock scraper for testing - simulates real prices"""
    
    def __init__(self):
        self.call_count = 0
    
    def scrape(self):
        """Simulate scraping by returning mock data"""
        self.call_count += 1
        
        # Simulate realistic prices (between €25-€100)
        import random
        prices = [
            {"price": random.uniform(25, 55), "departure_time": "06:15", "arrival_time": "08:40"},
            {"price": random.uniform(30, 65), "departure_time": "09:30", "arrival_time": "11:55"},
            {"price": random.uniform(35, 75), "departure_time": "13:00", "arrival_time": "15:25"},
            {"price": random.uniform(40, 85), "departure_time": "16:45", "arrival_time": "19:10"},
            {"price": random.uniform(28, 58), "departure_time": "18:20", "arrival_time": "20:45"},
        ]
        
        lowest = min(p["price"] for p in prices)
        
        result = {
            "departure": DEPARTURE_AIRPORT,
            "arrival": ARRIVAL_AIRPORT,
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "flights": prices,
            "lowest_price": lowest,
            "average_price": sum(p["price"] for p in prices) / len(prices),
            "scraped_at": datetime.now().isoformat(),
            "source": "mock_scraper"
        }
        
        return result
    
    def scrape_and_store(self):
        """Scrape and store in database"""
        result = self.scrape()
        
        try:
            insert_price(
                departure=result["departure"],
                arrival=result["arrival"],
                price=result["lowest_price"],
                departure_date=result["date"]
            )
            
            insert_price_check(
                lowest_price=result["lowest_price"],
                status="success"
            )
            
            logger.info(f"✅ Stored price: €{result['lowest_price']:.2f}")
            
            return {
                "success": True,
                "data": result,
                "stored": True
            }
        except Exception as e:
            logger.error(f"Error storing: {e}")
            return {
                "success": False,
                "data": result,
                "stored": False
            }


if __name__ == "__main__":
    logger.info("🧪 Running mock scraper demonstration...\n")
    
    scraper = MockFlightScraper()
    
    # Run 3 mock scrapes
    for i in range(3):
        logger.info(f"Run {i+1}/3:")
        result = scraper.scrape_and_store()
        
        if result["success"]:
            data = result["data"]
            print(f"  ✈️  {data['departure']} → {data['arrival']}")
            print(f"  💰 Lowest: €{data['lowest_price']:.2f} | Avg: €{data['average_price']:.2f}")
            print(f"  📊 Found {len(data['flights'])} flights\n")
    
    # Show database stats
    logger.info("\n📈 Price History Statistics:")
    stats = get_lowest_price(7)
    if stats:
        lowest, highest, average, count = stats
        print(f"  Lowest recorded: €{lowest:.2f}")
        print(f"  Highest recorded: €{highest:.2f}")
        print(f"  Average: €{average:.2f}")
        print(f"  Total checks: {count}")
