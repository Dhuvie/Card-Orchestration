import os
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_whatsapp_notification(phone_number: str, contact_name: str):
    token = settings.WHATSAPP_TOKEN
    phone_id = settings.WHATSAPP_PHONE_ID
    
    if not token or not phone_id:
        logger.warning("WhatsApp credentials missing. Skipping notification.")
        return False
        
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # In a real scenario, you'd use a pre-approved template message to initiate a conversation.
    # We will send a basic text message for this assignment's prototype.
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": f"Alert: A new contact, {contact_name}, has been saved to the CRM system."
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info("WhatsApp notification sent successfully.")
            return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False
