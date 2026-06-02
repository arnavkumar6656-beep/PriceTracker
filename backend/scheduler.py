import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
import os
import logging
from . import database, crud, scraper, models, notifier

logger = logging.getLogger(__name__)

async def scheduled_scrape_job():
    logger.info("Starting scheduled scrape job...")
    db = database.SessionLocal()
    try:
        products = crud.get_active_products(db)
        webhook_url = crud.get_setting(db, "discord_webhook_url", "")
        
        for product in products:
            logger.info(f"Scraping {product.title or product.url}")
            result = await scraper.scrape_product(product.url)
            
            if "error" in result:
                logger.error(f"Error scraping {product.url}: {result['error']}")
                continue
                
            new_price = result.get("price")
            old_price = product.current_price
            
            if result.get("title") and product.title != result.get("title"):
                product.title = result.get("title")
            if result.get("image_url") and product.image_url != result.get("image_url"):
                product.image_url = result.get("image_url")
            db.commit()
            
            if new_price:
                # Update price history and current price
                crud.add_price_history(db, product.id, new_price)
                
                # Evaluate alerts and notify
                await notifier.evaluate_alerts_and_notify(db, product, old_price, new_price)
                
            await asyncio.sleep(2)
            
        retention_days = int(crud.get_setting(db, "history_retention_days", "30"))
        crud.cleanup_old_history(db, retention_days)
        
    except Exception as e:
        logger.error(f"Error in scheduled job: {e}")
    finally:
        db.close()
    logger.info("Scheduled scrape job completed.")

def init_scheduler():
    scheduler = AsyncIOScheduler()
    interval_minutes = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))
    scheduler.add_job(scheduled_scrape_job, 'interval', minutes=interval_minutes)
    scheduler.start()
    return scheduler
