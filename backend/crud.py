from sqlalchemy.orm import Session
from . import models, schemas
import datetime

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_url(db: Session, url: str):
    return db.query(models.Product).filter(models.Product.url == url).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_active_products(db: Session):
    return db.query(models.Product).filter(models.Product.is_active == True).all()

def create_product(db: Session, product: schemas.ProductCreate, site: str):
    db_product = models.Product(
        url=str(product.url),
        site=site,
        target_price=product.target_price,
        alert_threshold_type=product.alert_threshold_type,
        alert_threshold_value=product.alert_threshold_value,
        is_active=product.is_active
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def add_price_history(db: Session, product_id: int, price: float):
    history = models.PriceHistory(product_id=product_id, price=price)
    db.add(history)
    
    product = get_product(db, product_id)
    if product:
        product.current_price = price
        product.last_checked = datetime.datetime.utcnow()
        
    db.commit()
    return history

def get_setting(db: Session, key: str, default: str = ""):
    setting = db.query(models.Settings).filter(models.Settings.key == key).first()
    return setting.value if setting else default

def set_setting(db: Session, key: str, value: str):
    setting = db.query(models.Settings).filter(models.Settings.key == key).first()
    if setting:
        setting.value = str(value)
    else:
        setting = models.Settings(key=key, value=str(value))
        db.add(setting)
    db.commit()
    return setting

def cleanup_old_history(db: Session, retention_days: int):
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=retention_days)
    db.query(models.PriceHistory).filter(models.PriceHistory.timestamp < cutoff_date).delete()
    db.commit()
