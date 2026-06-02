from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database, notifier

router = APIRouter()

@router.get("/", response_model=schemas.SettingsResponse)
def get_settings(db: Session = Depends(database.get_db)):
    discord_webhook_url = crud.get_setting(db, "discord_webhook_url", "")
    history_retention_days = int(crud.get_setting(db, "history_retention_days", "30"))
    
    return schemas.SettingsResponse(
        discord_webhook_url=discord_webhook_url,
        history_retention_days=history_retention_days
    )

@router.post("/", response_model=schemas.SettingsResponse)
def update_settings(settings: schemas.SettingsUpdate, db: Session = Depends(database.get_db)):
    if settings.discord_webhook_url is not None:
        crud.set_setting(db, "discord_webhook_url", settings.discord_webhook_url)
    
    if settings.history_retention_days is not None:
        crud.set_setting(db, "history_retention_days", str(settings.history_retention_days))
        
    return get_settings(db)

@router.post("/test-discord")
async def test_discord(db: Session = Depends(database.get_db)):
    discord_webhook_url = crud.get_setting(db, "discord_webhook_url", "")
    if not discord_webhook_url:
        raise HTTPException(status_code=400, detail="Discord Webhook URL is not configured.")
        
    try:
        await notifier.send_test_message(discord_webhook_url)
        return {"status": "success", "message": "Test notification sent successfully to Discord."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send webhook: {str(e)}")
