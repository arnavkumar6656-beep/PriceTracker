import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models, database

def inspect():
    db = database.SessionLocal()
    try:
        print("=== SETTINGS ===")
        settings = db.query(models.Settings).all()
        for s in settings:
            print(f"Key: {s.key}, Value: {s.value}")
        
        print("\n=== PRODUCTS ===")
        products = db.query(models.Product).all()
        for p in products:
            print(f"ID: {p.id}, Title: {p.title}, URL: {p.url}, Current Price: {p.current_price}, Target Price: {p.target_price}, Threshold Type: {p.alert_threshold_type}, Threshold Value: {p.alert_threshold_value}, Active: {p.is_active}")
            
        print("\n=== PRICE HISTORY ===")
        history = db.query(models.PriceHistory).all()
        for h in history:
            print(f"Product ID: {h.product_id}, Price: {h.price}, Timestamp: {h.timestamp}")
            
    finally:
        db.close()

if __name__ == "__main__":
    inspect()
