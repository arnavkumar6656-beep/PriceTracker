import httpx
import logging
from sqlalchemy.orm import Session
from . import models, crud
import traceback

logger = logging.getLogger(__name__)

async def evaluate_alerts_and_notify(db: Session, product: models.Product, old_price: float, new_price: float):
    # 1. Fetch Discord Webhook URL from settings
    webhook_url = crud.get_setting(db, "discord_webhook_url", "")
    if not webhook_url:
        logger.warning("[Notifier] No Discord Webhook URL configured in settings. Skipping alert evaluation.")
        return

    # 2. Extract values for logging
    current_price = new_price
    target_price = product.target_price
    threshold_type = product.alert_threshold_type
    threshold_value = product.alert_threshold_value

    # Requirement 2: Log notification evaluation parameters
    logger.info("Evaluating notification conditions...")
    logger.info(f"Current price: {current_price}")
    logger.info(f"Old price: {old_price}")
    logger.info(f"Target price: {target_price}")
    logger.info(f"Threshold type: {threshold_type}")
    logger.info(f"Threshold value: {threshold_value}")

    should_alert = False
    reason = ""

    # Requirement 5: Trigger notification on FIRST successful scrape if current_price <= target_price
    if old_price is None:
        if target_price is not None and current_price <= target_price:
            should_alert = True
            reason = f"First successful scrape and current price (₹{current_price}) is below/at target price (₹{target_price})"
    else:
        # Standard drop threshold check
        if current_price < old_price:
            if threshold_type == "fixed":
                if (old_price - current_price) >= threshold_value:
                    should_alert = True
                    reason = f"Price dropped from ₹{old_price} to ₹{current_price} (drop of ₹{old_price - current_price} >= threshold ₹{threshold_value})"
            elif threshold_type == "percentage":
                percentage_drop = ((old_price - current_price) / old_price) * 100
                if percentage_drop >= threshold_value:
                    should_alert = True
                    reason = f"Price dropped from ₹{old_price} to ₹{current_price} (drop of {percentage_drop:.2f}% >= threshold {threshold_value}%)"

        # Standard target price reached check
        if target_price is not None and current_price <= target_price and old_price > target_price:
            should_alert = True
            reason = f"Price crossed below target price (₹{target_price}). Old price: ₹{old_price}, New price: ₹{current_price}"

    # Requirement 3: Log pass/fail
    if should_alert:
        logger.info(f"Notification conditions PASSED. Reason: {reason}")
        # Requirement 4: Call Discord webhook immediately & log POST attempt
        logger.info(f"[Notifier] Attempting to send Discord webhook notification to URL (len: {len(webhook_url)})...")
        await notify_price_drop(webhook_url, product, old_price, new_price)
    else:
        logger.info("Notification conditions FAILED. No alert triggered.")

async def notify_price_drop(webhook_url: str, product: models.Product, old_price: float, new_price: float):
    if not webhook_url:
        logger.warning("[Notifier] Attempted to send notification, but no webhook URL was provided.")
        return
        
    logger.info(f"[Notifier] Formatting price drop alert for product: {product.title or product.url}")
    old_price_str = f"₹{old_price:,.2f}" if old_price is not None else "N/A"
    new_price_str = f"₹{new_price:,.2f}" if new_price is not None else "N/A"
    
    embed = {
        "title": "🚨 PRICE DROP ALERT",
        "description": f"**{product.title or product.url}**\n{product.site}",
        "color": 65280, 
        "fields": [
            {"name": "Old Price", "value": old_price_str, "inline": True},
            {"name": "New Price", "value": new_price_str, "inline": True},
            {"name": "Target Price Reached ✅", "value": "Yes" if product.target_price and new_price <= product.target_price else "No", "inline": False},
            {"name": "Product Link", "value": f"[Click Here]({product.url})", "inline": False}
        ]
    }
    
    if product.image_url:
        embed["thumbnail"] = {"url": product.image_url}
        
    if product.last_checked:
        embed["timestamp"] = product.last_checked.isoformat()

    payload = {
        "embeds": [embed]
    }

    # Requirement 6: Log sending action
    logger.info("Sending Discord notification...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            
            # Requirement 6: Log webhook response status
            logger.info(f"Webhook response status: {response.status_code}")
            
            # Requirement 7: Handle Discord 204 success correctly
            if response.status_code == 204:
                logger.info(f"[Notifier] Discord notification sent successfully (204 No Content) for {product.title or product.url}")
            else:
                # Requirement 8: Webhook failure logs
                logger.error(f"[Notifier] Webhook returned non-204 status: {response.status_code}")
                print(f"WEBHOOK FAILURE RESPONSE BODY:\n{response.text}")
                response.raise_for_status()
    except Exception as e:
        # Requirement 8: Never silently swallow errors
        logger.error(f"[Notifier] Exception encountered sending Discord notification: {e}")
        print("WEBHOOK FAILURE EXCEPTION TRACEBACK:")
        traceback.print_exc()
        raise e

async def send_test_message(webhook_url: str):
    if not webhook_url:
        logger.warning("[Notifier] Attempted to send test message, but no webhook URL was provided.")
        return
        
    payload = {
        "content": "🔔 **Price Tracker Test Message**\nYour Discord Webhook notification pipeline is configured correctly! 🎉"
    }

    # Requirement 6: Log sending action
    logger.info("Sending Discord notification...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            
            # Requirement 6: Log webhook response status
            logger.info(f"Webhook response status: {response.status_code}")
            
            # Requirement 7: Handle 204 success
            if response.status_code == 204:
                logger.info("[Notifier] Test notification sent successfully (204 No Content)")
            else:
                # Requirement 8
                logger.error(f"[Notifier] Webhook returned non-204 status: {response.status_code}")
                print(f"WEBHOOK FAILURE RESPONSE BODY:\n{response.text}")
                response.raise_for_status()
    except Exception as e:
        # Requirement 8
        logger.error(f"[Notifier] Exception encountered sending test notification: {e}")
        print("WEBHOOK FAILURE EXCEPTION TRACEBACK:")
        traceback.print_exc()
        raise e
