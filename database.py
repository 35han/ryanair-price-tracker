"""
Database setup and management for Ryanair Price Tracker
Creates SQLite database with tables to store flight prices
"""

import sqlite3
from datetime import datetime
import os
from config import DATABASE_NAME

def create_database():
    """Create SQLite database and tables if they don't exist"""
    
    # Connect to database (creates it if doesn't exist)
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create 'prices' table to store price history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departure_airport TEXT NOT NULL,
            arrival_airport TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            departure_date TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ryanair_url TEXT
        )
    ''')
    
    # Create 'alerts' table to track which alerts have been sent
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price REAL NOT NULL,
            alerted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_via TEXT  -- 'email', 'telegram', or 'both'
        )
    ''')
    
    # Create 'price_checks' table to track when bot runs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            lowest_price REAL,
            status TEXT,  -- 'success', 'error'
            error_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database created successfully!")

def get_lowest_price(days=7):
    """Get the lowest price from the last N days"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT MIN(price), MAX(price), AVG(price), COUNT(*)
        FROM prices
        WHERE checked_at >= datetime('now', '-' || ? || ' days')
    ''', (days,))
    
    result = cursor.fetchone()
    conn.close()
    return result

def insert_price(departure, arrival, price, currency='EUR', departure_date=None, url=None):
    """Store a price check in database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO prices (departure_airport, arrival_airport, price, currency, departure_date, ryanair_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (departure, arrival, price, currency, departure_date, url))
    
    conn.commit()
    conn.close()

def insert_alert(price, sent_via):
    """Record that an alert was sent"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alerts (price, sent_via)
        VALUES (?, ?)
    ''', (price, sent_via))
    
    conn.commit()
    conn.close()

def insert_price_check(lowest_price, status, error_message=None):
    """Record a price check attempt"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO price_checks (lowest_price, status, error_message)
        VALUES (?, ?, ?)
    ''', (lowest_price, status, error_message))
    
    conn.commit()
    conn.close()

def get_all_prices():
    """Get all prices from database (for dashboard/export)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM prices ORDER BY checked_at DESC')
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    # When you run this file directly, it creates the database
    create_database()
