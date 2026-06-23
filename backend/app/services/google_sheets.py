import json
import os
import gspread_asyncio
from google.oauth2.service_account import Credentials
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_creds():
    creds_json_str = settings.GOOGLE_SHEETS_CREDENTIALS
    if not creds_json_str or creds_json_str == "{}":
        return None
    try:
        creds_dict = json.loads(creds_json_str)
        creds = Credentials.from_service_account_info(creds_dict)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped
    except Exception as e:
        logger.error(f"Error loading Google Sheets credentials: {e}")
        return None

agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

async def get_worksheet():
    try:
        agc = await agcm.authorize()
        spreadsheet_id = settings.GOOGLE_SHEET_ID
        if not spreadsheet_id:
            logger.warning("GOOGLE_SHEET_ID not set, Sheets integration disabled.")
            return None
        doc = await agc.open_by_key(spreadsheet_id)
        worksheet = await doc.get_worksheet(0)
        return worksheet
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets: {e}")
        return None

async def find_duplicate(email: str, phone: str) -> bool:
    worksheet = await get_worksheet()
    if not worksheet:
        return False
    
    import re
    
    def normalize_phone(p: str) -> str:
        return re.sub(r'[^0-9]', '', str(p))
        
    def normalize_email(e: str) -> str:
        return str(e).strip().lower().replace(" ", "")
    
    try:
        all_values = await worksheet.get_all_values()
        if not all_values or len(all_values) <= 1:
            return False
            
        headers = [str(h).strip().lower() for h in all_values[0]]
        
        email_idx = headers.index('email') if 'email' in headers else -1
        phone_idx = headers.index('phone') if 'phone' in headers else -1
        
        if email_idx == -1 and phone_idx == -1:
            return False
            
        norm_email_in = normalize_email(email)
        norm_phone_in = normalize_phone(phone)
            
        for row in all_values[1:]:
            sheet_email = normalize_email(row[email_idx]) if email_idx != -1 and len(row) > email_idx else ''
            sheet_phone = normalize_phone(row[phone_idx]) if phone_idx != -1 and len(row) > phone_idx else ''
            
            if norm_email_in and sheet_email == norm_email_in:
                return True
            if norm_phone_in and sheet_phone == norm_phone_in:
                return True
                
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
    
    return False

async def append_row(data: dict) -> int:
    """Appends a row and returns the row index."""
    worksheet = await get_worksheet()
    if not worksheet:
        return -1
    
    try:
        all_values = await worksheet.get_all_values()
        expected_headers = ["ID", "Full Name", "Company", "Email", "Phone", "Website", "LinkedIn", "Audio URL"]
        
        if not all_values:
            await worksheet.append_row(expected_headers)
        
        try:
            # Force update row 1 to perfectly named columns
            await worksheet.update('A1:H1', [expected_headers])
            # Make headers bold and neat
            await worksheet.format('A1:H1', {
                "textFormat": {"bold": True, "fontSize": 11},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            })
            
            # Auto resize columns for the new headers
            body = {
                "requests": [{
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 8
                        }
                    }
                }]
            }
            # The spreadsheet property of AsyncioGspreadWorksheet exposes batch_update
            await worksheet.spreadsheet.batch_update(body)
        except Exception as sheet_format_error:
            logger.warning(f"Formatting headers failed, but data will still append: {sheet_format_error}")
            
        # Assuming headers: ID, Full Name, Company, Email, Phone, Website, LinkedIn, Audio URL
        row = [
            data.get("contact_id", ""),
            data.get("full_name", ""),
            data.get("company", ""),
            data.get("email", ""),
            data.get("phone", ""),
            data.get("website", ""),
            data.get("linkedin", ""),
            data.get("audio_url", "")
        ]
        await worksheet.append_row(row)
        
        return len(all_values) + 1
    except Exception as e:
        logger.error(f"Error appending row: {e}")
        return -1

async def update_row_audio(contact_id: str, audio_url: str) -> bool:
    worksheet = await get_worksheet()
    if not worksheet:
        return False
    
    try:
        records = await worksheet.get_all_records()
        row_index = 2 # 1 is header
        for record in records:
            if str(record.get('ID', '')) == str(contact_id):
                # Update Audio URL column, assuming it's the 8th column (H)
                await worksheet.update_cell(row_index, 8, audio_url)
                return True
            row_index += 1
    except Exception as e:
        logger.error(f"Error updating audio: {e}")
    return False
