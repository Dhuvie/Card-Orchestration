from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Visiting Card Platform"
    MONGODB_URL: str = "mongodb://localhost:27017" # Default for local dev
    DATABASE_NAME: str = "visiting_cards"
    GOOGLE_API_KEY: str = ""
    GOOGLE_SHEET_ID: str = ""
    GOOGLE_SHEETS_CREDENTIALS: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = ""
    WHATSAPP_MANAGER_PHONE: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
