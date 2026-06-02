from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
from .. import crud, schemas, scraper, database, models, notifier
import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    logger.info(f"[Products Router] Request to add product URL: {product.url}")
    db_product = crud.get_product_by_url(db, url=str(product.url))
    if db_product:
        logger.warning(f"[Products Router] Product already registered: {product.url}")
        raise HTTPException(status_code=400, detail="Product already registered")
        
    site = scraper.determine_site(str(product.url))
    if site == 'Unknown':
        logger.warning(f"[Products Router] Unsupported website domain for URL: {product.url}")
        raise HTTPException(status_code=400, detail="Unsupported website domain")

    created_product = crud.create_product(db=db, product=product, site=site)
    logger.info(f"[Products Router] Product created in database (ID: {created_product.id}, Site: {site})")
    
    background_tasks.add_task(scrape_and_update, created_product.id)
    logger.info(f"[Products Router] Scheduled background scrape for product ID: {created_product.id}")
    
    return created_product

@router.get("/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=schemas.ProductDetailResponse)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(database.get_db)):
    db_product = crud.update_product(db, product_id=product_id, product_update=product_update)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_product(db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.post("/{product_id}/scrape")
async def force_scrape_product(product_id: int, db: Session = Depends(database.get_db)):
    logger.info(f"[Products Router] Force scrape requested for product ID: {product_id}")
    db_product = crud.get_product(db, product_id=product_id)
    if not db_product:
        logger.warning(f"[Products Router] Force scrape failed: Product ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
        
    success, result = await scrape_and_update(product_id, db)
    if not success:
        logger.error(f"[Products Router] Force scrape failed for product ID {product_id}: {result}")
        raise HTTPException(status_code=400, detail={"error": "Scraping failed", "details": result})
        
    logger.info(f"[Products Router] Force scrape completed successfully for product ID {product_id}")
    return {"message": "Scraping completed", "data": result}

async def scrape_and_update(product_id: int, db: Session = None):
    logger.info(f"[Products Router] Starting scrape_and_update for product ID: {product_id}")
    if db is None:
        logger.info(f"[Products Router] Opening new database session for background task.")
        db = database.SessionLocal()
        should_close = True
    else:
        logger.info(f"[Products Router] Using provided database session.")
        should_close = False
        
    try:
        product = crud.get_product(db, product_id)
        if not product:
            logger.warning(f"[Products Router] Product ID {product_id} not found in database.")
            return False, "Product not found"

        logger.info(f"[Products Router] Found product: {product.title or product.url}. Initiating scraper...")
        result = await scraper.scrape_product(product.url)
        
        if "error" in result:
            logger.error(f"[Products Router] Scraper returned error for product ID {product_id}: {result['error']}")
            return False, result["error"]

        logger.info(f"[Products Router] Scraper completed successfully. Updating product attributes in database...")
        if result.get("title") and product.title != result.get("title"):
            logger.info(f"[Products Router] Updating title: '{product.title}' -> '{result.get('title')}'")
            product.title = result.get("title")
        if result.get("image_url") and product.image_url != result.get("image_url"):
            logger.info(f"[Products Router] Updating image URL: '{product.image_url}' -> '{result.get('image_url')}'")
            product.image_url = result.get("image_url")
            
        db.commit()

        price = result.get("price")
        if price:
            logger.info(f"[Products Router] Updating current price to ₹{price} and adding to history.")
            old_price = product.current_price
            crud.add_price_history(db, product_id, price)
            
            # Evaluate alerts and send Discord notification if conditions pass
            await notifier.evaluate_alerts_and_notify(db, product, old_price, price)
        else:
            logger.warning(f"[Products Router] No valid price returned from scraper for product ID {product_id}")

        logger.info(f"[Products Router] Database updates successfully committed for product ID {product_id}")
        return True, result
    except Exception as e:
        logger.exception(f"[Products Router] Unexpected error in scrape_and_update for product ID {product_id}: {e}")
        return False, str(e)
    finally:
        if should_close:
            db.close()
            logger.info(f"[Products Router] Closed background database session.")
