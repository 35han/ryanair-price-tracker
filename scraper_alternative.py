"""
Alternative scraper using direct Ryanair price search
This bypasses the problematic API endpoint
"""

import requests
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT
logger = logging.getLogger(__name__)

class RyanairAlternativeScraper:
    """Alternative scraper - tries different API endpoints and methods"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Referer": "https://www.ryanair.com/en/",
        })
    
    def scrape_price(self, departure_date=None):
        """Try multiple strategies to get price"""
        
        if not departure_date:
            departure_date = datetime.now() + timedelta(days=1)
        
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        
        date_str = departure_date.strftime("%Y-%m-%d")
        
        logger.info(f"🔍 Attempting alternative scraping for {DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT} on {date_str}")
        
        # Strategy 1: Try v3 API
        result = self._try_v3_api(date_str)
        if result:
            return result
        
        # Strategy 2: Try v4 API with POST instead of GET
        result = self._try_v4_post(date_str)
        if result:
            return result
        
        # Strategy 3: Try search page scraping
        result = self._try_search_page(date_str)
        if result:
            return result
        
        logger.error("❌ All alternative methods failed")
        return None
    
    def _try_v3_api(self, date_str):
        """Try older v3 API endpoint"""
        try:
            logger.info("📡 Trying v3 API...")
            
            url = "https://www.ryanair.com/api/booking/v3/en/availability"
            params = {
                "outboundDepartureDate": f"{date_str}T00:00:00",
                "departureAirportIataCode": DEPARTURE_AIRPORT,
                "arrivalAirportIataCode": ARRIVAL_AIRPORT,
                "market": "en",
                "limit": 16,
                "offset": 0,
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                flights = self._parse_v3_response(data)
                
                if flights:
                    logger.info(f"✅ v3 API worked! Found {len(flights)} flights")
                    return {
                        "departure": DEPARTURE_AIRPORT,
                        "arrival": ARRIVAL_AIRPORT,
                        "date": date_str,
                        "flights": flights,
                        "lowest_price": min([f["price"] for f in flights]),
                        "highest_price": max([f["price"] for f in flights]),
                        "average_price": sum([f["price"] for f in flights]) / len(flights),
                        "scraped_at": datetime.now().isoformat(),
                        "source": "ryanair_v3_api"
                    }
        except Exception as e:
            logger.warning(f"v3 API failed: {e}")
        
        return None
    
    def _try_v4_post(self, date_str):
        """Try v4 API with POST method"""
        try:
            logger.info("📡 Trying v4 POST API...")
            
            url = "https://www.ryanair.com/api/booking/v4/en/search"
            
            payload = {
                "outbound": {
                    "departureDate": date_str,
                    "departureAirport": DEPARTURE_AIRPORT,
                    "arrivalAirport": ARRIVAL_AIRPORT,
                },
                "limit": 16,
                "offset": 0,
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                flights = self._parse_v4_response(data)
                
                if flights:
                    logger.info(f"✅ v4 POST API worked! Found {len(flights)} flights")
                    return {
                        "departure": DEPARTURE_AIRPORT,
                        "arrival": ARRIVAL_AIRPORT,
                        "date": date_str,
                        "flights": flights,
                        "lowest_price": min([f["price"] for f in flights]),
                        "highest_price": max([f["price"] for f in flights]),
                        "average_price": sum([f["price"] for f in flights]) / len(flights),
                        "scraped_at": datetime.now().isoformat(),
                        "source": "ryanair_v4_post_api"
                    }
        except Exception as e:
            logger.warning(f"v4 POST API failed: {e}")
        
        return None
    
    def _try_search_page(self, date_str):
        """Try scraping the search results page HTML"""
        try:
            logger.info("📡 Trying search page scraping...")
            
            url = f"https://www.ryanair.com/en/booking/home/{DEPARTURE_AIRPORT}/{ARRIVAL_AIRPORT}/{date_str}"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # For now just log that we got the page
                logger.info(f"✅ Got search page ({len(response.text)} bytes)")
                # Real HTML parsing would go here but it's complex
                return None
        except Exception as e:
            logger.warning(f"Search page scraping failed: {e}")
        
        return None
    
    def _parse_v3_response(self, data):
        """Parse v3 API response"""
        flights = []
        try:
            trips = data.get("trips", [])
            if not trips:
                return flights
            
            trip = trips[0]
            dates = trip.get("dates", [])
            
            for date_info in dates:
                for flight in date_info.get("flights", []):
                    price = flight.get("regularFare", {}).get("fares", [{}])[0].get("amount")
                    
                    if price:
                        flights.append({
                            "price": float(price),
                            "currency": "EUR",
                            "departure_time": flight.get("departureTime"),
                            "arrival_time": flight.get("arrivalTime"),
                            "duration": str(flight.get("duration", "N/A")),
                        })
        except Exception as e:
            logger.warning(f"Error parsing v3 response: {e}")
        
        return flights
    
    def _parse_v4_response(self, data):
        """Parse v4 API response"""
        flights = []
        try:
            trips = data.get("trips", [])
            if not trips:
                return flights
            
            trip = trips[0]
            dates = trip.get("dates", [])
            
            for date_info in dates:
                for flight in date_info.get("flights", []):
                    price = flight.get("price", {}).get("amount")
                    
                    if price:
                        flights.append({
                            "price": float(price),
                            "currency": flight.get("price", {}).get("currency", "EUR"),
                            "departure_time": flight.get("departureTime"),
                            "arrival_time": flight.get("arrivalTime"),
                            "duration": str(flight.get("duration", "N/A")),
                        })
        except Exception as e:
            logger.warning(f"Error parsing v4 response: {e}")
        
        return flights
