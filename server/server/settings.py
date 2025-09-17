from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # Whatsapp
    whatsapp_app_id: str
    whatsapp_app_secret: str
    whatsapp_business_account_id: str
    whatsapp_access_token: str
    whatsapp_api_version: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    # Openai
    openai_api_key: str
    # Mongo
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    mongo_host: str
    mongo_port: str

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="allow")


settings = Settings()
