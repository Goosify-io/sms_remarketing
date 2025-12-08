from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    secret_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
