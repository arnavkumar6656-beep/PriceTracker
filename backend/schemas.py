from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    url: HttpUrl
    target_price: Optional[float] = None
    alert_threshold_type: str = "fixed" # "fixed" or "percentage"
    alert_threshold_value: float = 0.0
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    target_price: Optional[float] = None
    alert_threshold_type: Optional[str] = None
    alert_threshold_value: Optional[float] = None
    is_active: Optional[bool] = None

class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    timestamp: datetime

    class Config:
        from_attributes = True

class ProductResponse(ProductBase):
    id: int
    title: Optional[str] = None
    site: Optional[str] = None
    image_url: Optional[str] = None
    current_price: Optional[float] = None
    last_checked: Optional[datetime] = None
    url: str 
    
    class Config:
        from_attributes = True

class ProductDetailResponse(ProductResponse):
    history: List[PriceHistoryResponse] = []

class SettingsUpdate(BaseModel):
    discord_webhook_url: Optional[str] = None
    history_retention_days: Optional[int] = None

class SettingsResponse(BaseModel):
    discord_webhook_url: str = ""
    history_retention_days: int = 30
