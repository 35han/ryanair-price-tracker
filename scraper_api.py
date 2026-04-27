"""
Alternative scraper using Ryanair's internal API
This is more reliable than Selenium as it directly queries Ryanair's servers
"""

import requests
import logging
from datetime import datetime, timedelta
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RyanairAPIScraperV2:
    """Scrapes flight prices using Ryanair's API endpoint"""
    
    def __init__(self):
        # Ryanair's current API endpoint
        self.api_url = "https://www.ryanair.com/api/booking/v4/en/availability"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.ryanair.com/en/",
            "Origin": "https://www.ryanair.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
    
    def get_prices(self, departure_date=None):
        """
        Query Ryanair API for flight prices
        
        Args:
            departure_date: datetime object for flight date (default: tomorrow)
        
        Returns:
            dict with price info or None if error
        """
        
        if not departure_date:
            departure_date = datetime.now() + timedelta(days=1)
        
        # Format date as YYYY-MM-DD
        date_str = departure_date.strftime("%Y-%m-%d")
        
        logger.info(f"🔍 Querying API for {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT} on {date_str}")
        
        # Build query parameters for new API format
        params = {
            "departureAirportIataCode": DEPARTURE_AIRPORT,
            "arrivalAirportIataCode": ARRIVAL_AIRPORT,
            "outboundDepartureDate": f"{date_str}T00:00:00",
            "timezoneName": "UTC",
            "limit": 16
        }
        
        try:
            # Make request to Ryanair API
            response = requests.get(self.api_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ API response received")
            
            # Parse flights from response
            flights = self._parse_flights(data)
            
            if flights:
                logger.info(f"✅ Found {len(flights)} flights")
                return {
                    "departure": DEPARTURE_AIRPORT,
                    "arrival": ARRIVAL_AIRPORT,
                    "date": date_str,
                    "flights": flights,
                    "lowest_price": min([f["price"] for f in flights]),
                    "highest_price": max([f["price"] for f in flights]),
                    "average_price": sum([f["price"] for f in flights]) / len(flights),
                    "scraped_at": datetime.now().isoformat(),
                    "source": "ryanair_api"
                }
            else:
                logger.warning("⚠️ No flights found in API response")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error processing API response: {e}")
            return None
    
    def _parse_flights(self, data):
        """Extract flight info from API response"""
        flights = []
        
        try:
            # New API format returns trips array
            if "trips" not in data:
                logger.warning("No 'trips' key in API response")
                return flights
            
            trips = data.get("trips", [])
            if not trips:
                return flights
            
            # Get the first trip (outbound flights)
            trip = trips[0]
            flight_dates = trip.get("flightDates", [])
            
            for flight_date in flight_dates:
                try:
                    flights_list = flight_date.get("flights", [])
                    
                    for flight in flights_list:
                        price = flight.get("regularFare", {}).get("fares", [{}])[0].get("amount")
                        
                        if price is None:
                            continue
                        
                        departure_time = flight.get("departureTime", "N/A")
                        arrival_time = flight.get("arrivalTime", "N/A")
                        duration_mins = flight.get("duration", 0)
                        
                        # Convert minutes to HH:MM format
                        hours = duration_mins // 60
                        minutes = duration_mins % 60
                        duration = f"{hours}h {minutes}m" if duration_mins > 0 else "N/A"
                        
                        flights.append({
                            "price": float(price),
                            "currency": "EUR",
                            "departure_time": departure_time,
                            "arrival_time": arrival_time,
                            "duration": duration,
                            "scraped_at": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    logger.debug(f"Could not parse flight: {e}")
                    continue
            
            return flights
            
        except Exception as e:
            logger.error(f"Error parsing flights: {e}")
            return []
    
    def scrape_price(self, departure_date=None):
        """Main function to scrape prices"""
        return self.get_prices(departure_date)


# Test the scraper
if __name__ == "__main__":
    logger.info("Starting Ryanair API scraper test...")
    
    scraper = RyanairAPIScraperV2()
    result = scraper.scrape_price()
    
    if result:
        print("\n✅ Scraping successful!")
        print(f"Route: {result['departure']} → {result['arrival']}")
        print(f"Date: {result['date']}")
        print(f"Lowest price: €{result['lowest_price']:.2f}")
        print(f"Average price: €{result['average_price']:.2f}")
        print(f"Flights found: {len(result['flights'])}")
        
        # Show first 5 flights
        print("\nTop 5 cheapest flights:")
        sorted_flights = sorted(result['flights'], key=lambda x: x['price'])
        for i, flight in enumerate(sorted_flights[:5]):
            print(f"  {i+1}. €{flight['price']:.2f} - {flight['departure_time']} → {flight['arrival_time']} ({flight['duration']})")
    else:
        print("\n❌ Scraping failed")
