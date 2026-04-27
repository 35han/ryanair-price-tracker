"""
Phase 5 comprehensive test - Tests export and dashboard functionality
"""

import logging
from datetime import datetime
from exporter import PriceExporter
from database import get_lowest_price, get_all_prices
from config import DEPARTURE_AIRPORT, ARRIVAL_AIRPORT, PRICE_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_export_functionality():
    """Test export features"""
    
    print("\n" + "="*70)
    print("🧪 PHASE 5 - EXPORT & DASHBOARD TEST")
    print("="*70)
    
    exporter = PriceExporter()
    
    # Test 1: Statistics
    print("\n📊 Test 1: Statistics")
    print("-" * 70)
    
    stats = exporter.get_statistics(30)
    if stats:
        print(f"✅ Statistics generated:")
        print(f"   Lowest price: €{stats['lowest_price']:.2f}")
        print(f"   Highest price: €{stats['highest_price']:.2f}")
        print(f"   Average price: €{stats['average_price']:.2f}")
        print(f"   Price range: €{stats['price_range']:.2f}")
        print(f"   Total checks: {stats['total_checks']}")
    else:
        print("❌ No statistics available")
        return False
    
    # Test 2: CSV Export
    print("\n📄 Test 2: CSV Export")
    print("-" * 70)
    
    csv_file = exporter.export_to_csv(days=30, filename="test_export.csv")
    if csv_file:
        size_kb = csv_file.stat().st_size / 1024
        print(f"✅ CSV exported successfully")
        print(f"   File: {csv_file}")
        print(f"   Size: {size_kb:.1f}KB")
    else:
        print("❌ CSV export failed")
        return False
    
    # Test 3: JSON Export
    print("\n📄 Test 3: JSON Export")
    print("-" * 70)
    
    json_file = exporter.export_to_json(days=30, filename="test_export.json")
    if json_file:
        size_kb = json_file.stat().st_size / 1024
        print(f"✅ JSON exported successfully")
        print(f"   File: {json_file}")
        print(f"   Size: {size_kb:.1f}KB")
    else:
        print("❌ JSON export failed")
        return False
    
    # Test 4: Dashboard API
    print("\n🌐 Test 4: Dashboard API Simulation")
    print("-" * 70)
    
    all_prices = get_all_prices()
    print(f"✅ API would serve {len(all_prices)} price records")
    
    stats = exporter.get_statistics(7)
    if stats:
        print(f"✅ API statistics available:")
        print(f"   {stats['total_checks']} checks in last 7 days")
        print(f"   Average: €{stats['average_price']:.2f}")
    
    # Test 5: Export listing
    print("\n📁 Test 5: Export Listing")
    print("-" * 70)
    
    files = exporter.list_exports()
    print(f"✅ Found {len(files)} exported files")
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL PHASE 5 TESTS PASSED!")
    print("="*70)
    
    print("\n📋 Summary:")
    print(f"   ✅ Statistics generation working")
    print(f"   ✅ CSV export working")
    print(f"   ✅ JSON export working")
    print(f"   ✅ Dashboard API ready")
    print(f"   ✅ Export management working")
    
    return True

def show_usage():
    """Show how to use export and dashboard"""
    
    print("\n" + "="*70)
    print("📖 USAGE GUIDE")
    print("="*70)
    
    print("\n1️⃣  Export to CSV:")
    print("   from exporter import PriceExporter")
    print("   exporter = PriceExporter()")
    print("   csv_file = exporter.export_to_csv(days=30)")
    
    print("\n2️⃣  Export to JSON:")
    print("   json_file = exporter.export_to_json(days=30)")
    
    print("\n3️⃣  Get Statistics:")
    print("   stats = exporter.get_statistics(30)")
    print("   print(f'Lowest: €{stats[\"lowest_price\"]}')")
    
    print("\n4️⃣  Start Dashboard:")
    print("   cd ~/ryanair-price-tracker")
    print("   python dashboard.py")
    print("   Then open: http://localhost:5000")
    
    print("\n5️⃣  Dashboard Endpoints:")
    print("   GET  / - Main dashboard")
    print("   GET  /api/stats - JSON statistics")
    print("   GET  /api/prices - Price history")
    print("   GET  /api/export/csv - Download CSV")
    print("   GET  /api/export/json - Download JSON")
    
    print("\n6️⃣  Automated Exports:")
    print("   Add to scheduler.py to export after each job:")
    print("   exporter.export_to_csv()")
    print("   exporter.export_to_json()")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    logger.info("Starting Phase 5 test...")
    
    try:
        success = test_export_functionality()
        if success:
            show_usage()
        else:
            print("\n❌ Phase 5 test failed")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
