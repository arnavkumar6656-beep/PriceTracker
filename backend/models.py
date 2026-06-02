from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    site = Column(String)  # 'Amazon', 'Flipkart', 'Croma'
    image_url = Column(String, nullable=True)
    
    current_price = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True)
    
    # Alert threshold configuration
    alert_threshold_type = Column(String, default="fixed") # 'fixed' or 'percentage'
    alert_threshold_value = Column(Float, default=0.0) # e.g. 500 for fixed, 10 for percentage
    
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    
    history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("Product", back_populates="history")

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
