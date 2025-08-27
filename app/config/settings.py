from __future__ import annotations
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str = Field(..., description="Telegram bot token")
    TG_WEBHOOK_SECRET: str = Field(..., description="Shared secret for Telegram webhook header")

    # Web
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()