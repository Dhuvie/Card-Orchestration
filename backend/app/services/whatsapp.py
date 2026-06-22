import os
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_whatsapp_notification(phone_number: str, contact_name: str):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_WHATSAPP_FROM
    
    if not account_sid or not auth_token or not from_number:
        logger.warning("Twilio WhatsApp credentials missing. Skipping notification.")
        return False
        
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    # Twilio requires numbers to have the 'whatsapp:' prefix
    to_number = phone_number
    if not to_number.startswith("whatsapp:"):
        # Ensure there's a + sign before the country code if it's missing
        if not to_number.startswith("+"):
            to_number = f"+{to_number}"
        to_number = f"whatsapp:{to_number}"
        
    from_num_formatted = from_number
    if not from_num_formatted.startswith("whatsapp:"):
        if not from_num_formatted.startswith("+"):
            from_num_formatted = f"+{from_num_formatted}"
        from_num_formatted = f"whatsapp:{from_num_formatted}"

    payload = {
        "To": to_number,
        "From": from_num_formatted,
        "Body": f"Alert: A new contact, {contact_name}, has been saved to the CRM system."
    }
    
    try:
        # Twilio requires Basic Auth and Form-encoded data
        async with httpx.AsyncClient() as client:
            response = await client.post(url, auth=(account_sid, auth_token), data=payload)
            response.raise_for_status()
            logger.info("WhatsApp notification sent successfully via Twilio.")
            return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False
