"""
Export module - CSV and JSON export of price history
Useful for analysis and backup
"""

import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from database import get_all_prices, get_lowest_price
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceExporter:
    """Handles exporting price data to various formats"""
    
    def __init__(self, output_dir="exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Export directory: {self.output_dir.absolute()}")
    
    def export_to_csv(self, days=30, filename=None):
        """
        Export price history to CSV file
        
        Args:
            days: How many days of history to export
            filename: Output filename (optional)
        
        Returns:
            Path to exported file
        """
        
        if not filename:
            filename = f"prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.output_dir / filename
        
        logger.info(f"📊 Exporting to CSV: {filename}")
        
        try:
            # Get all prices
            all_prices = get_all_prices()
            
            if not all_prices:
                logger.warning("No price data to export")
                return None
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_prices = [
                p for p in all_prices
                if datetime.fromisoformat(p[6]) >= cutoff_date  # checked_at
            ]
            
            logger.info(f"Exporting {len(filtered_prices)} records")
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'ID',
                    'Departure',
                    'Arrival',
                    'Price (€)',
                    'Currency',
                    'Flight Date',
                    'Checked At',
                    'URL'
                ])
                
                # Data rows
                for price in filtered_prices:
                    writer.writerow([
                        price[0],  # id
                        price[1],  # departure_airport
                        price[2],  # arrival_airport
                        f"{price[3]:.2f}",  # price
                        price[4],  # currency
                        price[5],  # departure_date
                        price[6],  # checked_at
                        price[7] or "N/A"  # ryanair_url
                    ])
            
            logger.info(f"✅ CSV exported: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ CSV export failed: {e}")
            return None
    
    def export_to_json(self, days=30, filename=None):
        """
        Export price history to JSON file
        
        Args:
            days: How many days of history to export
            filename: Output filename (optional)
        
        Returns:
            Path to exported file
        """
        
        if not filename:
            filename = f"prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        logger.info(f"📊 Exporting to JSON: {filename}")
        
        try:
            # Get all prices
            all_prices = get_all_prices()
            
            if not all_prices:
                logger.warning("No price data to export")
                return None
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_prices = [
                p for p in all_prices
                if datetime.fromisoformat(p[6]) >= cutoff_date
            ]
            
            logger.info(f"Exporting {len(filtered_prices)} records")
            
            # Get statistics
            stats = get_lowest_price(days)
            if stats:
                lowest, highest, average, count = stats
            else:
                lowest = highest = average = count = 0
            
            # Prepare data
            data = {
                "export_info": {
                    "exported_at": datetime.now().isoformat(),
                    "route": f"{DEPARTURE_AIRPORT} → {ARRIVAL_AIRPORT}",
                    "days_exported": days,
                    "records": len(filtered_prices)
                },
                "statistics": {
                    "lowest_price": float(lowest) if lowest else None,
                    "highest_price": float(highest) if highest else None,
                    "average_price": float(average) if average else None,
                    "total_checks": count
                },
                "prices": []
            }
            
            # Add price records
            for price in filtered_prices:
                data["prices"].append({
                    "id": price[0],
                    "departure_airport": price[1],
                    "arrival_airport": price[2],
                    "price": float(price[3]),
                    "currency": price[4],
                    "departure_date": price[5],
                    "checked_at": price[6],
                    "ryanair_url": price[7]
                })
            
            # Write JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ JSON exported: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ JSON export failed: {e}")
            return None
    
    def get_statistics(self, days=30):
        """Get price statistics"""
        
        stats = get_lowest_price(days)
        
        if not stats:
            return None
        
        lowest, highest, average, count = stats
        
        return {
            "days": days,
            "lowest_price": float(lowest),
            "highest_price": float(highest),
            "average_price": float(average),
            "total_checks": count,
            "price_range": float(highest - lowest) if highest and lowest else 0,
            "generated_at": datetime.now().isoformat()
        }
    
    def list_exports(self):
        """List all exported files"""
        
        files = list(self.output_dir.glob("*.csv")) + list(self.output_dir.glob("*.json"))
        
        logger.info(f"Found {len(files)} exported files:")
        
        for f in sorted(files, reverse=True):
            size_kb = f.stat().st_size / 1024
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            logger.info(f"  {f.name} ({size_kb:.1f}KB) - {mtime.strftime('%Y-%m-%d %H:%M')}")
        
        return files


# Test function
if __name__ == "__main__":
    logger.info("Testing export module...")
    
    exporter = PriceExporter()
    
    # Get statistics
    logger.info("\n📊 Statistics (last 30 days):")
    stats = exporter.get_statistics(30)
    if stats:
        print(f"  Lowest: €{stats['lowest_price']:.2f}")
        print(f"  Highest: €{stats['highest_price']:.2f}")
        print(f"  Average: €{stats['average_price']:.2f}")
        print(f"  Range: €{stats['price_range']:.2f}")
        print(f"  Total checks: {stats['total_checks']}")
    
    # Export to CSV
    logger.info("\n📄 Exporting to CSV...")
    csv_file = exporter.export_to_csv(days=30)
    if csv_file:
        print(f"  ✅ {csv_file}")
    
    # Export to JSON
    logger.info("\n📄 Exporting to JSON...")
    json_file = exporter.export_to_json(days=30)
    if json_file:
        print(f"  ✅ {json_file}")
    
    # List exports
    logger.info("\n📁 All exports:")
    exporter.list_exports()
